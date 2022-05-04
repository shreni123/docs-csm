# Bootstrap PIT Node from LiveCD USB

The Pre-Install Toolkit (PIT) node needs to be bootstrapped from the LiveCD. There are two media available
to bootstrap the PIT node: the RemoteISO or a bootable USB device. This procedure describes using the USB
device. If not using the USB device, see [Bootstrap PIT Node from LiveCD Remote ISO](bootstrap_livecd_remote_iso.md).

These steps provide a bootable USB with SSH enabled, capable of installing this CSM release.

## Topics

1. [Create the Bootable Media](#create-the-bootable-media)
1. [Boot the LiveCD](#boot-the-livecd)
   1. [First Login](#first-login)
1. [Configure the Running LiveCD](#configure-the-running-livecd)
1. [Next Topic](#next-topic)

<a name="download-and-expand-the-csm-release"></a>
## 1. Download and Expand the CSM Release

Fetch the base installation CSM tarball, extract it, and install the contained CSI tool.

1. Create a working area for this procedure:

   ```bash
   linux# mkdir usb
   linux# cd usb
   ```

1. Set up the initial typescript.

   ```bash
   linux# SCRIPT_FILE=$(pwd)/csm-install-usb.$(date +%Y-%m-%d).txt
   linux# script -af ${SCRIPT_FILE}
   linux# export PS1='\u@\H \D{%Y-%m-%d} \t \w # '
   ```

<a name="create-the-bootable-media"></a>
## 2. Create the Bootable Media

Cray Site Init will create the bootable LiveCD. Before creating the media, identify
which device will be used for it.

1. Identify the USB device.

    This example shows the USB device is `/dev/sdd` on the host.

    ```bash
    linux# lsscsi
    ```

    Expected output looks similar to the following:
    ```
    [6:0:0:0]    disk    ATA      SAMSUNG MZ7LH480 404Q  /dev/sda
    [7:0:0:0]    disk    ATA      SAMSUNG MZ7LH480 404Q  /dev/sdb
    [8:0:0:0]    disk    ATA      SAMSUNG MZ7LH480 404Q  /dev/sdc
    [14:0:0:0]   disk    SanDisk  Extreme SSD      1012  /dev/sdd
    [14:0:0:1]   enclosu SanDisk  SES Device       1012  -
    ```

    In the above example, we can see our internal disks as the `ATA` devices and our USB as the `disk` or `enclosu` device. Because the `SanDisk` fits the profile we are looking for, we are going to use `/dev/sdd` as our disk.

    Set a variable with your disk to avoid mistakes:

    ```bash
    linux# USB=/dev/sd<disk_letter>
    ```

1. Format the USB device

   **TODO:** Step to copy `write-livecd.sh` into place.

    * On Linux, use the CSI application to do this:

        ```bash
        linux# write-livecd.sh ${USB} ${CSM_PATH}/cray-pre-install-toolkit-*.iso 50000
        ```

<a name="boot-the-livecd"></a>
## 3. Boot the LiveCD

Some systems will boot the USB device automatically if no other OS exists (bare-metal). Otherwise the
administrator may need to use the BIOS Boot Selection menu to choose the USB device.

If an administrator has the node booted with an operating system which will next be rebooting into the LiveCD,
then use `efibootmgr` to set the boot order to be the USB device. See the
[set boot order](../background/ncn_boot_workflow.md#set-boot-order) page for more information about how to set the
boot order to have the USB device first.

> **Note:** UEFI booting must be enabled in order for the system to find the USB device's EFI bootloader.

1. Start a typescript on an external system.

   This will record this section of activities done on the console of `ncn-m001` using IPMI.

   ```bash
   external# script -a boot.livecd.$(date +%Y-%m-%d).txt
   external# export PS1='\u@\H \D{%Y-%m-%d} \t \w # '
   ```

1. Confirm that the IPMI credentials work for the BMC by checking the power status.

   Set the `BMC` variable to the hostname or IP address of the BMC of the PIT node.

   > `read -s` is used in order to prevent the credentials from being displayed on the screen or recorded in the shell history.

   ```bash
   external# BMC=eniac-ncn-m001-mgmt
   external# read -s IPMI_PASSWORD
   external# export IPMI_PASSWORD ; ipmitool -I lanplus -U root -E -H ${BMC} chassis power status
   ```

1. Connect to the IPMI console.

   ```bash
   external# ipmitool -I lanplus -U root -E -H ${BMC} sol activate
   ```

1. Watch the shutdown and boot from the `ipmitool` console session.

   > **An integrity check** runs before Linux starts by default; it can be skipped by selecting `OK` in its prompt.

<a name="first-login"></a>
### 3.1 First Login

On first log in (over SSH or at local console), the LiveCD will prompt the administrator to change the password.

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

   > **Note:** If this password ever becomes lost or forgotten, one may reset it by mounting the USB device on another computer. See [Reset root Password on LiveCD](reset_root_password_on_LiveCD.md) for information on clearing the password.

1. Disconnect from IPMI console.

   Once the network is up so that SSH to the node works, disconnect from the IPMI console.

   You can disconnect from the IPMI console by entering `~.`; That is, the tilde character followed by a period character.

1. Exit the typescript started on the external system and use `scp` to transfer it to the PIT node.

   > Set `PIT_NODE` variable to the site IP address or hostname of the PIT node.

   ```bash
   external# exit
   external# PIT_NODE=eniac-ncn-m001
   external# scp boot.livecd.*.txt root@${PIT_NODE}:/root
   ```

1. Log in to the PIT node as `root` using `ssh`.

   ```bash
   external# ssh root@${PIT_NODE}
   ```

1. Mount the data partition.

   The data partition is set to `fsopt=noauto` to facilitate LiveCDs over virtual-ISO mount. Therefore, USB installations
   need to mount this manually by running the following command.

   > **Note:** When creating the USB PIT image, this was mounted over `/mnt/pitdata`. Now that the USB PIT is booted,
   > it will mount over `/var/www/ephemeral`. The FSLabel `PITDATA` is already in `/etc/fstab`, so the path is omitted
   > in the following call to `mount`.

   ```bash
   pit# mount -vL PITDATA
   ```

<a name="next-topic"></a>
## Next Topic

After completing this procedure, proceed to [Configuring the LiveCD](./bootstrap_livecd.md#4-configure-the-running-livecd).
