# Enabling Customer High Speed Network Routing

- [Enabling Customer High Speed Network Routing](#enabling-customer-high-speed-network-routing)
  - [Process overview and warnings](#process-overview-and-warnings)
  - [Prerequisites](#prerequisites)
  - [Backup Phase](#backup-phase)
    - [Preparation](#preparation)
    - [Create system backups](#create-system-backups)
  - [Update Phase](#update-phase)
    - [Update SLS](#update-sls)
    - [Update customizations](#update-customizations)
  - [Migrate Phase](#migrate-phase)
    - [Migrate NCN workers](#migrate-ncn-workers)
    - [Migrate CSM Services (MetalLB)](#migrate-csm-services-metallb)
    - [Migrate UAN](#migrate-uan)
    - [Migrate UAI](#migrate-uai)
    - [Migrate Computes (optional)](#migrate-computes-optional)
  - [Cleanup Phase](#cleanup-phase)
    - [Remove CAN from SLS](#remove-can-from-sls)
    - [Remove CAN from BSS](#remove-can-from-bss)
    - [Remove CAN interfaces from NCN workers](#remove-can-interfaces-from-ncn-workers)
    - [Remove CAN names from hosts file](#remove-can-names-from-hosts-file)
    - [Remove CAN service endpoints](#remove-can-service-endpoints)
  - [Update the management network](#update-the-management-network)
  - [Testing](#testing)

## Process overview and warnings

**IMPORTANT** This procedure is quite involved and the complexities should be completely understood before beginning.  The procedure may be run as part of a system upgrade, or at any time after the CSM 1.3 system upgrade - out-of-band with the upgrade itself.

The primary objective of this procedure is to move user traffic (users running jobs) from a `CAN` network running over the CSM management network, to a `CHN` network over the Slingshot high speed network, while *minimizing* downtime and outages.

For safety and flexibility this procedures brings up the `CHN` network while the system remains running on the `CAN`.  Components can the be migrated to the `CHN` in a controlled manner, with minimal interruptions to existing `CAN` operations.

The overall process can be summarized as:

1. Backup phase
   1. Save critical runtime data
   2. Prevent components from migrating to the `CHN`
2. Update phase
   1. Add the `CHN` data and configurations while the `CAN` remains as-is
3. Migrate phase - perform a controlled configuration and migration of components from the `CAN` to the `CHN`
      1. NCN workers
      2. CSM services
      3. UAN NCN
      4. UAI
      5. Compute (optional)
4. Cleanup phase
   1. Remove the `CAN` from operations and all data sets

The procedure, to be safe and flexible, is intensive from both the number of steps involved and the amount of system data which needs to be managed.
However, during the migration phase, ample time and flexibility exists to contact system users as well as reverse the migration.

## Prerequisites

1. The system as a whole must be healthy and running.
2. A site-routable IPv4 subnet for the `CHN`.  Minimally this must be sized to accommodate:
   1. Three IPs for switching, plus
   2. The number of `NCN` workers on the system, plus
   3. One IP for the API ingress gateway, plus
   4. The number of `NCN` `UANs` on the system, plus
   5. The maximum number of `UAIs` required, plus
   6. IPs for any other services to be brought up dynamically on the `CHN`
   7. **NOTE** A `/24` subnet is usually more than sufficient for small-to-medium sized systems with minimal `UAI` requirements.
3. The Slingshot high speed network is configured and up, including the fabric manager service.  This network is required to transit CHN traffic.
4. The Slingshot Host Software is installed and configured on NCN Worker nodes.  This is required to expose CHN services.  For the purpose of CHN, the host software creates the (required) primary IPv4 address on `hsn0`, often a `10.253` address.

## Backup Phase

### Preparation

1. (`ncn-m001#`) Create the a directory for the procedure and set environment variables.

   ```bash
   mkdir migrate_can_to_chn
   cd migrate_can_to_chn
   export BASEDIR=$(pwd)
   mkdir backups updates cleanup
   export BACKUPDIR=${BASEDIR}/backups
   export UPDATEDIR=${BASEDIR}/updates
   export CLEANUPDIR=${BASEDIR}/cleanup
   ```

2. (`ncn-m001#`) Obtain a token.

   ```bash
   export TOKEN=$(curl -s -k -S -d grant_type=client_credentials -d client_id=admin-client \
                 -d client_secret=`kubectl get secrets admin-client-auth -o jsonpath='{.data.client-secret}' | base64 -d` \
                 https://api-gw-service-nmn.local/keycloak/realms/shasta/protocol/openid-connect/token | jq -r '.access_token')
   ```

### Create system backups

1. (`ncn-m001#`) Create a backup directory.

   ```bash
   cd ${BACKUPDIR}
   ```

2. (`ncn-m001#`) Backup original `SLS` data.

   ```bash
   curl -k -H "Authorization: Bearer ${TOKEN}" https://api-gw-service-nmn.local/apis/sls/v1/dumpstate | jq -S . > sls_input_file.json
   ```

3. (`ncn-m001#`) Backup original customizations data.

   ```bash
   kubectl -n loftsman get secret site-init -o json | jq -r '.data."customizations.yaml"' | base64 -d > customizations.yaml
   ```

4. (`ncn-m001#`) Backup original MetalLB `configmap` data.

   ```bash
   kubectl get cm -n metallb-system metallb -o yaml > metallb.yaml
   ```

5. (`ncn-m001#`) Backup original manifest data.

   ```bash
   kubectl get cm -n loftsman loftsman-platform -o jsonpath='{.data.manifest\.yaml}' > manifest.yaml
   ```

6. (`ncn-m001#`) Backup original NCN Personalization data.

   ```bash
   cray cfs configurations describe ncn-personalization --format json | jq 'del(.lastUpdated) | del(.name)' > ncn-personalization.json
   ```

7. (`ncn-m001#`) Backup original BSS data.

   ```bash
   curl -s -X GET -H "Authorization: Bearer ${TOKEN}" https://api-gw-service-nmn.local/apis/bss/boot/v1/bootparameters | jq . > bss-bootparameters.json
   ```

8. (`ncn-m001#`) Backup system databases (optional).

   ```bash
   TODO: DO WE NEED THIS?
   ```

## Update Phase

### Update SLS

1. (`ncn-m001#`) Move to the update directory.

   ```bash
   cd ${UPDATEDIR}
   ```

2. (`ncn-m001#`) Set the directory location for the `SLS` `CHN` script

   ```bash
   [[ -f /usr/share/doc/csm/upgrade/scripts/sls/sls_can_to_chn.py ]] &&
      export SLS_CHN_DIR=/usr/share/doc/csm/upgrade/scripts/sls || 
      echo "STOP:  Manual intervention is required.
      1. Ensure the [CSM 1.3 Documentation](../../update_product_stream/README.md#check-for-latest-documentation) is installed.
      2. export SLS_CHN_DIR=/usr/share/doc/csm/upgrade/scripts/sls"
   ```

3. (`ncn-m001#`) Add `CHN` to `SLS` data.

   ```bash
   ${SLS_CHN_DIR}/sls_can_to_chn.py --sls-input-file ${BACKUPDIR}/sls_input_file.json
      --customer-highspeed-network <CHN VLAN> <CHN IPv4 Subnet>
      --number-of-chn-edge-switches <number of edge switches>
      --sls-output-file ${UPDATEDIR}/sls_file_with_chn.json
   ```

   where:

      - `<CHN VLAN>` is the "stub" `VLAN` for the `CHN`.  This is currently used only on the edge switches in access mode, not a trunk through the high speed network.
      - `<CHN IPv4 Subnet>` is the pre-requisite site-routable IPv4 subnet for the `CHN`
      - `<number of edge switches>` is typically 2 Arista or Aruba switches, but some pre-production systems have 1

4. (`ncn-m001#`) Upload data to `SLS`.

   ```bash
   curl --fail -H "Authorization: Bearer ${TOKEN}" -k -L -X POST 'https://api-gw-service-nmn.local/apis/sls/v1/loadstate' -F "sls_dump=@${UPDATEDIR}/sls_file_with_chn.json"
   ```

### Update customizations

1. (`ncn-m001#`) Move to the update directory.

   ```bash
   cd ${UPDATEDIR}
   ```

2. (`ncn-m001#`) Set the directory location for the customizations script to add `CHN`.

   ```bash
   [[ -f /usr/share/doc/csm/upgrade/scripts/upgrade/util/update-customizations.sh ]] &&
      export CUSTOMIZATIONS_SCRIPT_DIR=/usr/share/doc/csm/upgrade/scripts/upgrade/util || 
      echo "STOP:  Requires manual steps"
   grep NETWORKSJSON ${CUSTOMIZATIONS_SCRIPT_DIR}/update-customizations.sh >/dev/null 2>&1 ||
      echo "STOP:  This does not to update networking.  Manual steps required.
      1. Ensure the [CSM 1.3 Documentation](../../update_product_stream/README.md#check-for-latest-documentation) is installed.
      2. export SLS_CHN_DIR=/usr/share/doc/csm/upgrade/scripts/sls"
   ```

3. (`ncn-m001#`) Create updated `customizations.yaml` against updated `SLS`.

   ```bash
   cd ${UPDATEDIR}
   ${CUSTOMIZATIONS_SCRIPT_DIR}/update-customizations.sh ${BACKUPDIR}/customizations.yaml > customizations.yaml
   yq validate customizations.yaml
   ```

   **Important** If the updated `customizations.yaml` file is empty or not valid `YAML`, do not proceed.  Debug in place.

4. (`ncn-m001#`) Upload new `customizations.yaml` to ensure changes persist across updates

   ```bash
   kubectl delete secret -n loftsman site-init
   kubectl create secret -n loftsman generic site-init --from-file=customizations.yaml
   ```

## Migrate Phase

### Migrate NCN workers

1. (`ncn-m001#`) Change to updates directory

   ```bash
   cd ${UPDATESDIR}
   ```

2. (`ncn-m001#`) Ensure SHS is active by testing if there is an `HSN` IP address (typically `10.253`) on the `hsn0` interfaces.  If there is not primary address on the `hsn0` interface this must be fixed before proceeding;

   ```bash
   pdsh -w ncn-w00[1-$(egrep 'ncn-w...\.nmn' /etc/hosts | wc -l)] ip address list dev hsn0
   ```

   **NOTE** If some interfaces have a `HSN` address and others do not, this is typically indicative that the CFS plays are failing at some point.
   The following `CFS` steps may help, but checking if the Slingshot high speed network and host software is operating correctly prior to moving forward in this procedure is required.

3. Determine the CFS configuration in use on the worker nodes.

   1. (`ncn#`) Identify the all worker nodes.

      ```bash
      cray hsm state components list --role Management --subrole Worker --format json | jq -r '.Components[] | .ID'
      ```

      Example output:

      ```text
      x3000c0s4b0n0
      x3000c0s6b0n0
      x3000c0s5b0n0
      x3000c0s7b0n0
      ```

   2. (`ncn#`) Identify CFS configuration in use by running the following for each of the the worker nodes identified above.

      ```bash
      cray cfs components describe --format toml x3000c0s4b0n0
      ```

      Example output:

      ```toml
      configurationStatus = "configured"
      desiredConfig = "ncn-personalization"
      enabled = true
      errorCount = 0
      id = "x3000c0s4b0n0"
      ```

      **NOTE** Errors or failed CFS personalization runs may be fixed via the following process as CFS will be re-run. Likely, though, it's better to take a few minutes to troubleshoot the current issue.

4. (`ncn#`) Extract the CFS configuration.

   ```bash
   cray cfs configurations describe ncn-personalization --format json | jq 'del(.lastUpdated) | del(.name)' > ncn-personalization.json
   ```

   The resulting output file should look similar to this. Installed products, versions, and commit hashes will vary.

   ```json
   {
     "layers": [
       {
         "cloneUrl": "https://api-gw-service-nmn.local/vcs/cray/slingshot-host-software-config-management.git",
         "commit": "f4e2bb7e912c39fc63e87a9284d026a5bebb6314",
         "name": "shs-1.7.3-45-1.0.26",
         "playbook": "shs_mellanox_install.yml"
       },
       {
         "cloneUrl": "https://api-gw-service-nmn.local/vcs/cray/csm-config-management.git",
         "commit": "92ce2c9988fa092ad05b40057c3ec81af7b0af97",
         "name": "csm-1.9.21",
         "playbook": "site.yml"
       },
       {
         "cloneUrl": "https://api-gw-service-nmn.local/vcs/cray/sat-config-management.git",
         "commit": "4e14a37b32b0a3b779b7e5f2e70998dde47edde1",
         "name": "sat-2.3.4",
         "playbook": "sat-ncn.yml"
       },
       {
         "cloneUrl": "https://api-gw-service-nmn.local/vcs/cray/cos-config-management.git",
         "commit": "dd2bcbb97e3adbfd604f9aa297fb34baa0dd90f7",
         "name": "cos-integration-2.3.75",
         "playbook": "ncn.yml"
       },
       {
         "cloneUrl": "https://api-gw-service-nmn.local/vcs/cray/cos-config-management.git",
         "commit": "dd2bcbb97e3adbfd604f9aa297fb34baa0dd90f7",
         "name": "cos-integration-2.3.75",
         "playbook": "ncn-final.yml"
       }
     ]
   }
   ```

5. Edit the extracted file. Copy the existing CSM layer and create an new layer to run the `enable_chn.yml` playbook.  The original CSM layer should still exist after this operation as well as the new layer.

   ```json
   {
     "cloneUrl": "https://api-gw-service-nmn.local/vcs/cray/csm-config-management.git",
     "commit": "92ce2c9988fa092ad05b40057c3ec81af7b0af97",
     "name": "csm-1.9.21",
     "playbook": "enable_chn.yml"
   }
   ```

   **Important:** This new layer *must* run after the COS `ncn-final.yml` layers, otherwise the HSN interfaces will not be configured correctly and this playbook will fail.  Typically at the end of the list is okay.

6. (`ncn#`) Update the NCN personalization configuration.

   ```bash
   cray cfs configurations update ncn-personalization --file ncn-personalization.json --format toml
   ```

   Example output:

   ```toml
   lastUpdated = "2022-05-25T09:22:44Z"
   name = "ncn-personalization"
   [[layers]]
   cloneUrl = "https://api-gw-service-nmn.local/vcs/cray/   slingshot-host-software-config-management.git"
   commit = "f4e2bb7e912c39fc63e87a9284d026a5bebb6314"
   name = "shs-1.7.3-45-1.0.26"
   playbook = "shs_mellanox_install.yml"

   [[layers]]
   cloneUrl = "https://api-gw-service-nmn.local/vcs/cray/csm-config-management.git"
   commit = "92ce2c9988fa092ad05b40057c3ec81af7b0af97"
   name = "csm-1.9.21"
   playbook = "site.yml"

   [[layers]]
   cloneUrl = "https://api-gw-service-nmn.local/vcs/cray/sat-config-management.git"
   commit = "4e14a37b32b0a3b779b7e5f2e70998dde47edde1"
   name = "sat-2.3.4"
   playbook = "sat-ncn.yml"

   [[layers]]
   cloneUrl = "https://api-gw-service-nmn.local/vcs/cray/cos-config-management.git"
   commit = "dd2bcbb97e3adbfd604f9aa297fb34baa0dd90f7"
   name = "cos-integration-2.3.75"
   playbook = "ncn.yml"

   [[layers]]
   cloneUrl = "https://api-gw-service-nmn.local/vcs/cray/cos-config-management.git"
   commit = "dd2bcbb97e3adbfd604f9aa297fb34baa0dd90f7"
   name = "cos-integration-2.3.75"
   playbook = "ncn-final.yml"

   [[layers]]
   cloneUrl = "https://api-gw-service-nmn.local/vcs/cray/csm-config-management.git"
   commit = "92ce2c9988fa092ad05b40057c3ec81af7b0af97"
   name = "csm-1.9.21"
   playbook = "enable_chn.yml"
   ```

7. (`ncn#`) Check that NCN personalization runs and completes successfully on all worker nodes.

   Updating the CFS configuration will cause CFS to schedule the nodes for configuration. Run the following command to verify this has occurred.

   ```bash
   cray cfs components describe --format toml x3000c0s4b0n0
   ```

   Example output:

   ```toml
   configurationStatus = "pending"
   desiredConfig = "ncn-personalization"
   enabled = true
   errorCount = 0
   id = "x3000c0s4b0n0"
   state = []
   
   [tags]
   ```

   `configurationStatus` should change from `pending` to `configured` once NCN personalization completes successfully.

For more information on managing NCN personalization, see [Perform NCN Personalization](../../operations/CSM_product_management/Perform_NCN_Personalization.md).

### Migrate CSM Services (MetalLB)

```text
TODO
extract metallb configmap
yq just the metallb stuff from new customizations
merge into configmap
load into metallb

kick pod? (luke did not have to) kubectl rollout restart
```

### Migrate UAN

```text
TODO
```

### Migrate UAI

```text
TODO
```

### Migrate Computes (optional)

```text
TODO
```

## Cleanup Phase

### Remove CAN from SLS

```text
TODO
```

### Remove CAN from BSS

1. (`ncn-m001#`) Move to the update directory.

   ```bash
   cd ${CLEANUPDIR}
   ```

2. (`ncn-m001#`) Set the directory location for the `BSS` `CHN` script.

   ```bash
   [[ -f /usr/share/doc/csm/upgrade/scripts/bss/bss_remove_can.py ]] &&
      export BSS_CAN_DIR=/usr/share/doc/csm/upgrade/scripts/bss || 
      echo "STOP:  Manual intervention is required.
      1. Ensure the [CSM 1.3 Documentation](../../update_product_stream/README.md#check-for-latest-documentation) is installed.
      2. export BSS_CAN_DIR=/usr/share/doc/csm/upgrade/scripts/bss"
   ```

3. (`ncn-m001#`) Remove `CAN` from `BSS` data.

   ```bash
   ${BSS_CAN_DIR}/bss_remove_can.py --bss-input-file ${BACKUPDIR}/bss-bootparameters.json --bss-output-file ${CLEANUPDIR}/bss-ouput-chn.json
   ```

4. (`ncn-m001#`) Upload data to `BSS`.

   ```bash
   ${BSS_CAN_DIR}/post-bootparameters.sh -u https://api-gw-service-nmn.local/apis/bss/boot/v1/bootparameters -f ${CLEANUPDIR}/bss-ouput-chn.json
   ```

### Remove CAN interfaces from NCN workers

```text
TODO
```

### Remove CAN names from hosts file

```text
TODO
```

### Remove CAN service endpoints

```text
TODO
```

## Update the management network

```text
TODO
```

## Testing

```text
TODO
```
