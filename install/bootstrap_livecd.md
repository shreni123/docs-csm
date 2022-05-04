# Bootstrap PIT Node from LiveCD Remote ISO

The Pre-Install Toolkit (PIT) node needs to be bootstrapped from the LiveCD. There are two media available
to bootstrap the PIT node: the RemoteISO or a bootable USB device. This procedure describes using the USB
device.

This page will walk one through setting up storage on the NCN to use as a staging area, by default an arbitrary disk will be used. One may also use a USB stick (removable storage) to accomplish this. Using a local disk entails a necessary wipe prior to [deploying the final NCN](deploy_final_ncn.md) after the CSM install.


**Important:** Before starting this procedure be sure to complete the procedure to
[Prepare Configuration Payload](prepare_configuration_payload.md) for the relevant installation scenario.

## Topics

1. [Known Compatibility Issues](#known-compatibility-issues)
1. [Attaching and Booting the LiveCD with the BMC](#attaching-and-booting-the-livecd-with-the-bmc)
1. [First Login](#first-login)
1. [Configure the Running LiveCD](#configure-the-running-livecd)
   1. [Generate Installation Files](#generate-installation-files)
   1. [Prepare Site Init](#prepare-site-init)
1. [Bring-up the PIT Services and Validate PIT Health](#bring---up-the-pit-services-and-validate-pit-health)
1. [Next Topic](#next-topic)

<a name="known-compatibility-issues"></a>
## 1. Known Compatibility Issues

The LiveCD Remote ISO has known compatibility issues for nodes from certain vendors.

   * Intel nodes will fail to boot the LiveCD when in UEFI mode. UEFI is required for the NCN deploy, one may switch to Legacy BIOS for the PIT if they switch back to UEFI before [deploying the final NCN](./deploy_final_ncn.md)

<a name="attaching-and-booting-the-livecd-with-the-bmc"></a>
## 2. Attaching and Booting the LiveCD with the BMC

Obtain and attach the LiveCD `cray-pre-install-toolkit` ISO file to the BMC. Depending on the vendor of the node,
the instructions for attaching to the BMC will differ.

1. Download the CSM software release and extract the LiveCD remote ISO image.

   **Important:** Ensure that you have the CSM release plus any patches or hotfixes by
   following the instructions in [Update CSM Product Stream](../update_product_stream/index.md)

   The `cray-pre-install-toolkit` ISO and other files are now available in the directory from the extracted CSM tar file.
   The ISO will have a name similar to
   `cray-pre-install-toolkit-sle15sp3.x86_64-1.5.8-20211203183315-geddda8a.iso`

   This ISO file can be extracted from the CSM release tar file using the following command:
   ```bash
   linux# tar --wildcards --no-anchored -xzvf <csm-release>.tar.gz 'cray-pre-install-toolkit-*.iso'
   ```

1. Prepare a server on the network to host the `cray-pre-install-toolkit` ISO file.

   Place the `cray-pre-install-toolkit` ISO file on a server which the BMC of the PIT node
   will be able to contact using HTTP or HTTPS.

   **Note:** A short URL is better than a long URL for the PIT file on the webserver.

1. See the [Booting ] respective procedure below to attach an ISO.

   - [HPE iLO BMCs](boot_livecd_remoteiso.md#hpe-ilo-bmcs)
   - [Gigabyte BMCs](boot_livecd_remoteiso.md#gigabyte-bmcs)
   - **Intel BMCs** currently need directions.

1. The chosen procedure should have rebooted the server. Observe the server boot into the LiveCD.

<a name="first-login"></a>
## 3. First Login

On first login (over SSH or at local console) the LiveCD will prompt the administrator to change the password.

1. **The initial password is empty**; enter the username of `root` and press `return` twice.

   ```
   pit login: root
   ```

   Expected output looks similar to the following:

   ```
   Password:           <-------just press Enter here for a blank password
   You are required to change your password immediately (administrator enforced)
   Changing password for root.
   Current password:   <------- press Enter here, again, for a blank password
   New password:       <------- type new password
   Retype new password:<------- retype new password
   Welcome to the CRAY Pre-Install Toolkit (LiveOS)
   ```

<a name="configure-the-running-livecd"></a>
## 4. Configure the Running LiveCD

1. Start a typescript to record this section of activities done on `ncn-m001` while booted from the LiveCD.

   ```bash
   pit# script -af ~/csm-install-remoteiso.$(date +%Y-%m-%d).txt
   pit# export PS1='\u@\H \D{%Y-%m-%d} \t \w # '
   ```

1. Print information about the booted PIT image.

   There is nothing in the output that needs to be verified. This is run in order to ensure the information is
   recorded in the typescript file, in case it is needed later. For example, this information is useful to include in
   any bug reports or service queries for issues encountered on the PIT node.

   ```bash
   pit# /root/bin/metalid.sh
   ```

   Expected output looks similar to the following:

   ```
   = PIT Identification = COPY/CUT START =======================================
   VERSION=1.6.0
   TIMESTAMP=20220504161044
   HASH=g10e2532
   2022/05/04 17:08:19 Using config file: /var/www/ephemeral/prep/system_config.yaml
   CRAY-Site-Init build signature...
   Build Commit   : 0915d59f8292cfebe6b95dcba81b412a08e52ddf-main
   Build Time     : 2022-05-02T20:21:46Z
   Go Version     : go1.16.10
   Git Version    : v1.9.13-29-g0915d59f
   Platform       : linux/amd64
   App. Version   : 1.17.1
   metal-ipxe-2.2.6-1.noarch
   metal-net-scripts-0.0.2-20210722171131_880ba18.noarch
   metal-basecamp-1.1.12-1.x86_64
   pit-init-1.2.20-1.noarch
   pit-nexus-1.1.4-1.x86_64
   = PIT Identification = COPY/CUT END =========================================
   ```

1. Find a local disk for storing product installers.

   ```bash
   pit# disk="$(lsblk -l -o SIZE,NAME,TYPE,TRAN | grep -E '(sata|nvme|sas)' | sort -h | awk '{print $2}' | head -n 1 | tr -d '\n')"
   pit# echo $disk
   pit# parted --wipesignatures -m --align=opt --ignore-busy -s /dev/$disk -- mklabel gpt mkpart primary ext4 2048s 100%
   pit# mkfs.ext4 -L PITDATA "/dev/${disk}1"
   pit# mount -vL PITDATA
   ```

   The `parted` command may give an error similar to the following:
   ```text
   Error: Partition(s) 4 on /dev/sdX have been written, but we have been unable to inform the kernel of the change, probably
   because it/they are in use. As a result, the old partition(s) will remain in use. You should reboot now before making
   further changes.
   ```

   In that case, the following steps may resolve the problem without needing to reboot. These commands remove
   volume groups and raid arrays that may be using the disk. **These commands only need to be run if the earlier
   `parted` command failed.**

   ```bash
   pit# RAIDS=$(grep "${disk}[0-9]" /proc/mdstat | awk '{ print "/dev/"$1 }') ; echo ${RAIDS}
   pit# VGS=$(echo ${RAIDS} | xargs -r pvs --noheadings -o vg_name 2>/dev/null) ; echo ${VGS}
   pit# echo ${VGS} | xargs -r -t -n 1 vgremove -f -v
   pit# echo ${RAIDS} | xargs -r -t -n 1 mdadm -S -f -v
   ```

   After running the above procedure, retry the `parted` command which failed. If it succeeds, resume the install from that point.

1. <a name="set-up-site-link"></a>Set up the site-link, enabling SSH to work. You can reconnect with SSH after this step.
   > **Note:** If your site's network authority or network administrator has already provisioned a DHCP IPv4 address for your master node's external NIC(s), **then skip this step**.

   1. Set networking variables.

      > If you have previously created the `system_config.yaml` file for this system, the values for these variables are in it. The
      > following table lists the variables being set, their corresponding `system_config.yaml` fields, and a description of what
      > they are.

      | Variable    | `system_config.yaml`   | Description                                                                        |
      |-------------|------------------------|------------------------------------------------------------------------------------|
      | `site_ip`   | `site-ip`              | The IPv4 address **and CIDR netmask** for the node's external interface(s)         |
      | `site_gw`   | `site-gw`              | The IPv4 gateway address for the node's external interface(s)                      |
      | `site_dns`  | `site-dns`             | The IPv4 domain name server address for the site                                   |
      | `site_nics` | `site-nic`             | The actual NIC name(s) for the external site interface(s)                          |

      > If the `system_config.yaml` file has not yet been generated for this system, the values for `site_ip`, `site_gw`, and
      > `site_dns` should be provided by the site's network administrator or network authority. The `site_nics` interface(s)
      > are typically the first onboard adapter or the first copper 1 GbE PCIe adapter on the PIT node. If multiple interfaces are
      > specified, they must be separated by spaces (for example, `site_nics='p2p1 p2p2 p2p3'`).

      ```bash
      pit# site_ip=172.30.XXX.YYY/20
      pit# site_gw=172.30.48.1
      pit# site_dns=172.30.84.40
      pit# site_nics=em1
      ```

   1. Run the `csi-setup-lan0.sh` script to set up the site link.

      > **Note:** All of the `/root/bin/csi-*` scripts are harmless to run without parameters; doing so will print usage statements.

      ```bash
      pit# /root/bin/csi-setup-lan0.sh $site_ip $site_gw $site_dns $site_nics
      ```

   1. Verify that `lan0` has an IP address

      The script appends `-pit` to the end of the hostname as a means to reduce the chances of confusing the PIT node with an actual, deployed NCN.

      ```bash
      pit# ip a show lan0
      ```

   1. Add helper variables to PIT node environment.

      > **Important:** All CSM install procedures on the PIT node assume that these variables are set
      > and exported.

      1. Set helper variables.

         ```bash
         pit# CSM_RELEASE=csm-x.y.z
         pit# PITDATA=$(lsblk -o MOUNTPOINT -nr /dev/disk/by-label/PITDATA)
         ```

      1. Add variables to the PIT environment.

         By adding these to the `/etc/environment` file of the PIT node, these variables will be
         automatically set and exported in shell sessions on the PIT node.

         > The `echo` prepends a newline to ensure that the variable assignment occurs on a unique line,
         > and not at the end of another line.

         ```bash
         pit# echo "
         CSM_RELEASE=${CSM_RELEASE}
         PITDATA=${PITDATA}
         CSM_PATH=${PITDATA}/${CSM_RELEASE}" | tee -a /etc/environment
         ```

   1. Exit the typescript, exit the console session, and log in again using SSH.

      ```bash
      pit# exit # exit the typescript started earlier
      pit# exit # log out of the pit node
      # Close the console session by entering &. or ~.
      # Then ssh back into the PIT node
      external# ssh root@<system DNS name or IP>
      ```

   1. After reconnecting, resume the typescript (the `-a` appends to an existing script).

       ```bash
      pit# script -af $(ls -tr ~/csm-install-remoteiso*.txt | head -n 1)
      pit# export PS1='\u@\H \D{%Y-%m-%d} \t \w # '
      ```

   1. Verify that expected environment variables are set in the new login shell.

      ```bash
      pit# echo -e "CSM_PATH=${CSM_PATH}\nCSM_RELEASE=${CSM_RELEASE}\nPITDATA=${PITDATA}\n"
      ```

1. Mount local disk.

   > **Note:** The FSLabel `PITDATA` is already in `/etc/fstab`, so the path is omitted in the following call to `mount`.

   ```bash
   pit# mount -vL PITDATA &&
        mkdir -pv ${PITDATA}/{admin,configs} ${PITDATA}/prep/{admin,logs} ${PITDATA}/data/{k8s,ceph}
   ```

1. Relocate the typescript to the newly mounted `PITDATA` directory.

   1. Quit the typescript session with the `exit` command.

   1. Copy the typescript file to its new location.

      ```bash
      pit# cp -v ~/csm-install-remoteiso.*.txt ${PITDATA}/prep/admin
      ```

   1. Restart the typescript, appending to the previous file.

      ```bash
      pit# script -af $(ls -tr ${PITDATA}/prep/admin/csm-install-remoteiso*.txt | head -n 1)
      pit# export PS1='\u@\H \D{%Y-%m-%d} \t \w # '
      ```

1. Download the CSM software release to the PIT node.

   1. Set variable to URL of CSM tarball.

      ```bash
      pit# URL=https://arti.dev.cray.com/artifactory/shasta-distribution-stable-local/csm/${CSM_RELEASE}.tar.gz
      ```

   1. Fetch the release tarball.

      ```bash
      pit# wget ${URL} -O ${CSM_PATH}.tar.gz
      ```

   1. Expand the tarball on the PIT node.

      > **Note:** Expansion of the tarball may take more than 45 minutes.

      ```bash
      pit# tar -C ${PITDATA} -zxvf ${CSM_PATH}.tar.gz && ls -l ${CSM_PATH}
      ```

   1. Copy the artifacts into place.

      ```bash
      pit# rsync -a -P --delete ${CSM_PATH}/images/kubernetes/   ${PITDATA}/data/k8s/ &&
           rsync -a -P --delete ${CSM_PATH}/images/storage-ceph/ ${PITDATA}/data/ceph/
      ```

   > **Note:** The PIT ISO, Helm charts/images, and bootstrap RPMs are now available in the extracted CSM tar file.

1. Install/upgrade CSI; check if a newer version was included in the tarball.

   ```bash
   pit# rpm -Uvh $(find ${CSM_PATH}/rpm/ -name "cray-site-init-*.x86_64.rpm" | sort -V | tail -1)
   ```

1. Install the latest Goss Tests and Server.

   ```bash
   pit# rpm -Uvh --force $(find ${CSM_PATH}/rpm/ -name "goss-servers*.rpm" | sort -V | tail -1) \
                         $(find ${CSM_PATH}/rpm/ -name "csm-testing*.rpm" | sort -V | tail -1)
   ```

1. Install the latest documentation RPM.

   See [Check for Latest Documentation](../update_product_stream/index.md#documentation)

1. Re-run the Metal ID script to output information into the running typescript:

   ```bash
   pit# /root/bin/metalid.sh
   ```

   Expected output looks similar to the following:

   ```
   = PIT Identification = COPY/CUT START =======================================
   VERSION=1.6.0
   TIMESTAMP=20220504161044
   HASH=g10e2532
   2022/05/04 17:08:19 Using config file: /var/www/ephemeral/prep/system_config.yaml
   CRAY-Site-Init build signature...
   Build Commit   : 0915d59f8292cfebe6b95dcba81b412a08e52ddf-main
   Build Time     : 2022-05-02T20:21:46Z
   Go Version     : go1.16.10
   Git Version    : v1.9.13-29-g0915d59f
   Platform       : linux/amd64
   App. Version   : 1.17.1
   metal-ipxe-2.2.6-1.noarch
   metal-net-scripts-0.0.2-20210722171131_880ba18.noarch
   metal-basecamp-1.1.12-1.x86_64
   pit-init-1.2.20-1.noarch
   pit-nexus-1.1.4-1.x86_64
   = PIT Identification = COPY/CUT END =========================================
   ```

<a name="generate-installation-files"></a>
### 4.1 Generate Installation Files

Some files are needed for generating the configuration payload. See [Configuration Payload Files](prepare_configuration_payload.md#configuration_payload_files) topics if one has not already prepared the information for this system.

* [Configuration Payload Files](prepare_configuration_payload.md#configuration_payload_files)

1. Copy these files into the current working directory (e.g. `/var/www/ephemeral/prep`), or create them if this is an initial install of the system:

   - `application_node_config.yaml` (optional - see below)
   - `cabinets.yaml` (optional - see below)
   - `hmn_connections.json`
   - `ncn_metadata.csv`
   - `switch_metadata.csv`
   - `system_config.yaml`

   > The optional `application_node_config.yaml` file may be provided for further definition of settings relating to how application nodes will appear in HSM for roles and subroles. See [Create Application Node YAML](create_application_node_config_yaml.md).

   > The optional `cabinets.yaml` file allows cabinet naming and numbering as well as some VLAN overrides. See [Create Cabinets YAML](create_cabinets_yaml.md).
   
<a name="prepare-site-init"></a>
### 4.2 Prepare Site Init

> **Important:** Although the command prompts in this procedure are `linux#`, the procedure should be
> performed on the PIT node.

Prepare the `site-init` directory by performing the [Prepare Site Init](prepare_site_init.md) procedures.

<a name="bring---up-the-pit-services-and-validate-pit-health"></a>
## 5. Bring-up the PIT Services and Validate PIT Health

1. Initialize the PIT.

   The `pit-init.sh` script will prepare the PIT server for deploying NCNs.

   ```bash
   pit# /root/bin/pit-init.sh
   ```

1. Invoke the pre-flight checks

   ```bash
   pit# csi pit validate --livecd-preflight
   pit# csi pit validate --ncn-preflight
   ```

<a name="next-topic"></a>
## Next Topic

After completing this procedure, proceed to configure the management network switches.

See [Configure Management Network Switches](index.md#configure_management_network)
