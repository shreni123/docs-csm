# Stage 3 - CSM Service Upgrades

1. Prepare assets:

   ```bash
    ncn-m002# CSM_RELEASE=csm-1.2.0
   ```

   - Internet Connected

     1. Set the ENDPOINT variable to the URL of the directory containing the CSM release tarball.

        In other words, the full URL to the CSM release tarball will be ${ENDPOINT}${CSM_RELEASE}.tar.gz

        **NOTE** This step is optional for Cray/HPE internal installs.

        ```bash
        ncn-m002# ENDPOINT=https://put.the/url/here/
        ```

     1. Run the script

        ```bash
        ncn-m002# /usr/share/doc/csm/upgrade/1.2/scripts/upgrade/prepare-assets.sh --csm-version [CSM_RELEASE] --endpoint [ENDPOINT]
        ```

   - Air Gapped (replace the PATH_TO below with the location of the CSM release tarball)

     1. Copy CSM release tarball to `ncn-m002`.

     1. Run the script

        ```bash
        ncn-m002# /usr/share/doc/csm/upgrade/1.2/scripts/upgrade/prepare-assets.sh --csm-version [CSM_RELEASE] --tarball-file [PATH_TO_CSM_TARBALL_FILE]
        ```

1. Run `csm-upgrade.sh` to deploy upgraded CSM applications and services:
   **IMPORTANT:**

   > During this stage there will be a brief (approximately 5 minutes) window where pods with Persistent Volumes(PVs) will not be able to migrate between nodes. This is due to a redeployment of the Ceph csi provisioners into namespaces to accommodate the newer charts and a better upgrade strategy.

   > Set the `SW_ADMIN_PASSWORD` environment variable to the admin password for the switches. This is needed for post upgrade tests.

   ```bash
   ncn-m002# export SW_ADMIN_PASSWORD=PutYourOwnPasswordHere
   ```

   ```bash
   ncn-m002# /usr/share/doc/csm/upgrade/1.2/scripts/upgrade/csm-upgrade.sh
   ```

1. Verify that the Keycloak Users Localize job has completed as expected.

   This step can be skipped if user localization is not required.

   After an upgrade, it is possible that all expected Keycloak users were not localized. Check to see if the Keycloak users localize job has completed. You should see output containing `condition met`.

   ```bash
   ncn# kubectl -n services wait --for=condition=complete --timeout=10s job/`kubectl -n services get jobs | grep users-localize | awk '{print $1}'`
   ```

   If the job completed, check that the count of localized users matches the expected count from your Keycloak server. This can be done by looking at the count of users reported from the command below.

   ```bash
   ncn# cray artifacts get wlm etc/passwd /dev/stdout | wc -l
   ```

   If that count looks correct, then no further action is needed.  If not, rerun the localize job by following the steps below:

   ```bash
   ncn# kubectl get job -n services -l app.kubernetes.io/name=cray-keycloak-users-localize \
        -ojson | jq '.items[0]' > keycloak-users-localize-job.json
   ncn# kubectl delete job -n services -l app.kubernetes.io/name=cray-keycloak-users-localize
   ncn# cat keycloak-users-localize-job.json | jq 'del(.spec.selector)' | \
        jq 'del(.spec.template.metadata.labels)' | kubectl apply -f -
   ```

   Expected output looks similar to:

   ```bash
   job.batch "keycloak-users-localize-1" deleted
   job.batch/keycloak-users-localize-1 created
   ```

   Confirm that the job completed. You should see output containing `condition met`.

   ```bash
   ncn# kubectl -n services wait --for=condition=complete --timeout=10s job/`kubectl -n services get jobs | grep users-localize | awk '{print $1}'`
   ```

   Confirm that the user count looks correct by running the command below again:

   ```bash
   ncn# cray artifacts get wlm etc/passwd /dev/stdout | wc -l
   ```

Once `Stage 3` is completed, proceed to [Stage 4](Stage_4.md)
