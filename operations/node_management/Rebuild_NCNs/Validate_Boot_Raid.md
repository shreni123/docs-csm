# Validate `BOOTRAID` Artifacts

Perform the following steps **on `ncn-m001`**.

1. Initialize the `cray` command and follow the prompts (required for the next step).

   ```screen
   cray init
   ```

1. Run the script to ensure the local `BOOTRAID` has a valid kernel and initrd.

    ```screen
    pdsh -S -b -w $(grep -oP 'ncn-\w\d+' /etc/hosts | sort -u |  tr -t '\n' ',') '
    /opt/cray/tests/install/ncn/scripts/check_bootloader.sh
    '
    ```

## Workaround: CASMINST-2015

As a result of rebuilding any NCN(s), remove any dynamically assigned interface IP addresses that did not get released automatically by running the CASMINST-2015 script:

```bash
/usr/share/doc/csm/scripts/CASMINST-2015.sh
```

Once that is done only follow the steps in the section for the node type that was rebuilt:

* [Storage Node](Re-add_Storage_Node_to_Ceph.md)
