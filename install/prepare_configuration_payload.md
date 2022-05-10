# Prepare Configuration Payload

The configuration payload consists of the information which must be known about the HPE Cray EX system so it
can be passed to the `csi` (Cray Site Init) program during the CSM installation process.

Information gathered from a site survey is needed to feed into the CSM installation process, such as system name,
system size, site network information for the CAN, site DNS configuration, site NTP configuration, network
information for the node used to bootstrap the installation. More detailed component level information about the
system hardware is encapsulated in the SHCD (Shasta Cabling Diagram), which is a spreadsheet prepared by HPE Cray
Manufacturing to assemble the components of the system and connect appropriately labeled cables.

## Topics

* [Command Line Configuration Payload](#command_line_configuration_payload)
* [Configuration Payload Files](#configuration_payload_files)
    * [File Reference](#file-reference)
    * [Steps for Collection](#steps-for-collection)
* [CSI Tips](#csi-tips)
* [Next Topic](#next-topic)

<a name="command_line_configuration_payload"></a>
## Command Line Configuration Payload

The information from a site survey can be given to the `csi` command as command line arguments or to the blank config file.
The information and options shown below are to explain what data is needed. It will not be used until moving
to the [Bootstrap PIT Node](index.md#bootstrap_pit_node) procedure.

<a name="configuration_payload_files"></a>
## Configuration Payload Files

A few configuration files are needed for the installation of CSM. These are all provided to the `csi`
command during the installation process.

<a name="file-reference"></a>
### File Reference

| Filename | Source | Information |
| --- | --- | --- |
| `cabinets.yaml` | SHCD | The number and type of air-cooled and liquid-cooled cabinets. cabinet IDs, and VLAN numbers |
| `application_node_config.yaml` | SHCD | The number and type of application nodes with mapping from the name in the SHCD to the desired hostname |
| `hmn_connections.json` | SHCD | The network topology for HMN of the entire system |
| `ncn_metadata.csv` | SHCD, other| The number of master, worker, and storage nodes and MAC address information for BMC and bootable NICs |
| `switch_metadata.csv` | SHCD | Inventory of all spine, leaf, CDU, and leaf-bmc switches |
| `system_config.yaml` | other | Inputs from the site-survey |

<a name="steps-for-collection"></a>

### Steps for Collection

The process to install for the first time must collect the information needed to create these files.  These files can be created using `canu` and `csi` with a valid SHCD file.

#### Generate A Paddle File

1. Generate a Paddle file using `canu`:

```bash
canu validate <options> --shcd <shcd.xlsx>
```

#### Generate Seed Files From A Paddle File

The Paddle file is a machine-readable representation of the SHCD.  The `csi` command can interpret this file and produce the seed files needed for an installation.

1. Automatically create `application_node_config.yaml`, `hmn_connections.json`, `ncn_metadata.csv`, and `switch_metadata.csv`.

```bash
csi config shcd paddle.json -AHNS
```

The manual steps to create these files can be found here as reference:

- See [Create Application Node YAML](create_application_node_config_yaml.md) for instructions about creating this file.
- See [Create HMN Connections JSON](create_hmn_connections_json.md) for instructions about creating this file.
- See [Create NCN Metadata CSV](create_ncn_metadata_csv.md) for instructions about creating this file.
- See [Create Switch Metadata CSV](create_switch_metadata_csv.md) for instructions about creating this file.

1. Collect data for `cabinets.yaml`.

   See [Create Cabinets YAML](create_cabinets_yaml.md) for instructions about creating this file.

1. Create a `system_config.yaml` if one is not already present from a previous install.

   ```bash
   pit# csi config init empty
   ```

   > **`NOTE`** For a short description of each key in the file, run `csi config init --help`.

   > **`NOTE`** For more description of these settings and the default values, see
   > [Default IP Address Ranges](../introduction/csm_overview.md#default_ip_address_ranges) and the other topics in
   > [CSM Overview](../introduction/csm_overview.md). There are additional options not shown on this page that can be
   > seen by running `csi config init --help`.

<a name="csi-tips"></a>
### CSI Tips

* The `bootstrap-ncn-bmc-user` and `bootstrap-ncn-bmc-pass` must match what is used for the BMC account and its password for the management nodes.
* Set site parameters (`site-domain`, `site-ip`, `site-gw`, `site-nic`, `site-dns`) for the information which connects `ncn-m001` (the PIT node) to the site. The `site-nic` is the interface on this node connected to the site.
* There are other interfaces possible, but the `install-ncn-bond-members` are typically:
   * `p1p1,p10p1` for HPE nodes
   * `p1p1,p1p2` for Gigabyte nodes
   * `p801p1,p801p2` for Intel nodes
* The starting cabinet number for each type of cabinet (for example, `starting-mountain-cabinet`) has a default that can be overridden. See the `csi config init --help` output for more information.
* An override to default cabinet IPv4 subnets can be made with the `hmn-mtn-cidr` and `nmn-mtn-cidr` parameters.
* Several parameters (`can-gateway`, `can-cidr`, `can-static-pool`, `can-dynamic-pool`) describe the CAN (Customer Access network). The `can-gateway` is the common gateway IP address used for both spine switches and commonly referred to as the Virtual IP address for the CAN. The `can-cidr` is the IP subnet for the CAN assigned to this system. The `can-static-pool` and `can-dynamic-pool` are the MetalLB address static and dynamic pools for the CAN.
* Several parameters (`cmn-gateway`, `cmn-cidr`, `cmn-static-pool`, `cmn-dynamic-pool`) describe the CMN (Customer Management network). The `cmn-gateway` is the common gateway IP address used for both spine switches and commonly referred to as the Virtual IP address for the CMN. The `cmn-cidr` is the IP subnet for the CMN assigned to this system. The `cmn-static-pool` and `cmn-dynamic-pool` are the MetalLB address static and dynamic pools for the CAN. The `cmn-external-dns` is the static IP address assigned to the DNS instance running in the cluster to which requests the cluster subdomain will be forwarded. The `cmn-external-dns` IP address must be within the `cnn-static-pool` range.
* Set `ntp-pool` to a reachable NTP server.
* The `application_node_config.yaml` file is required. It is used to describe the mapping between prefixes in `hmn_connections.csv` and HSM subroles. This file also defines aliases application nodes. For details, see [Create Application Node YAML](create_application_node_config_yaml.md).
* For systems that use non-sequential cabinet id numbers, use `cabinets-yaml` to include the `cabinets.yaml` file. This file can include information about the starting ID for each cabinet type and number of cabinets which have separate command line options, but is a way to specify explicitly the id of every cabinet in the system. See [Create Cabinets YAML](create_cabinets_yaml.md).
* The PowerDNS zone transfer arguments `primary-server-name`, `secondary-servers`, and `notify-zones` are optional unless zone transfer is being configured. For more information see the [PowerDNS Configuration Guide](../operations/network/dns/PowerDNS_Configuration.md#zone-transfer)

<a name="next-topic"></a>
## Next Topic

After completing this procedure the next step is to prepare the management nodes. See [Prepare Management Nodes](index.md#prepare_management_nodes)

