# Cray System Management (CSM) - Release Notes

CSM 1.3 contains approximately 500 changes spanning bug fixes, new feature development, and documentation improvements. This page lists some of the highlights.

## New

### Monitoring

* TBD

### DHCP

#### Changed

* **Kea**: Fixed a bug that could cause the auto-repair logic to fail due to an incorrect index

### DNS

#### Changed

* **ExternalDNS**: Fixed a bug where cray-externaldns-manager could panic if it couldn't connect to PowerDNS on startup
* **PowerDNS**: Changed powerdns-manager SLS error message to debug
* **PowerDNS**: Fixed bug that caused powerdns-manager and externaldns-manager to update the same record
* **PowerDNS**: Fixed a bug that could cause PowerDNS to intermittently crash when performing a lookup for an existing TSIG key
* **PowerDNS**: powerdns-manager will now retry attempts to add a TSIG key
* **PowerDNS**: powerdns-manager will now create PTR records that are not created by external-dns
* **Unbound**: Changed cray-dns-unbound MaxUnavailable default to 1 to avoid issues when evicting pods from NCNs

### Management Network

#### Added

* **Documentation**: Added procedure to migrate from the customer access network (CAN) to the customer high-speed network (CHN), allowing user traffic over the HSN instead of the NMN (This is an extension of the bi-furcated CAN feature that shipped in CSM 1.2)
* **Documentation**: Added various troubleshooting guides

#### Changed

* **CANU**: Fixed bug where UAN VLANs in generated switch configs were wrong when using the CHN
* **CANU**: Other various bug fixes (see https://github.com/cray-hpe/canu for a full changelog)
* **CANU**: Added an ACL on systems with Dell and Mellanox switches to prevent high-speed network (HSN) switches on the Hardware Management Network (HMN) from communicating with the Fabric Manager service on the Node Management Network (NMN) API gateway
* **CSI**: Fixed bug where CSI could generate bad SLS chassis data
* **Documentation**: Admins are now asked to updated CANU to the latest version when beginning a CSM upgrade
* **Documentation**: Management network switch upgrade instructs are now separate from the CSM upgrade procedure
* **Documentation**: Removed stale reference to Kea postgres from troubleshooting documentation
* **Documentation**: Fixed invalid commands in generate_switch_configs.md

### Miscellaneous functionality

* Integrated Kyverno Native Policy Management engine
* Ansible has been added to NCNs
* Added support for the Replace/Remove/Add NCN procedures
* Integrated Argo Server workflow engine for Kubernetes
* Technology Preview: BOS V2 (Boot Orchestration) Asynchronous boot state handling and CRUS replacement for rolling upgrade
* Technology Preview: Tenant and Partition Management Service (TAPMS)
* Support for setting of Bios Settings through SCSD
* Ability to set power cap on n number of computes

### New hardware support

* Olympus Antero Blade (AMD Genoa) with Slingshot 11
* Aruba JL705C, JL706C, JL707C management network switches

### Automation improvements

* TBD

### Base platform component upgrades

| Platform Component           | Version        |
|------------------------------|----------------|
| Ceph                         | `16.6.29`      |
| `containerd`                 | `1.5.10`       |
| Istio                        | `1.10.6`       |
| Kubernetes                   | `1.21.12`      |
| Nexus                        | `3.38.0-1`     |
| Prometheus                   | `2.36.1`       |
| `oauth2-proxy`               | `7.3.0`        |
| `cray-opa`                   | `0.42.1`       |
| `cray-velero`                | `1.6.3-2`      |

### Security improvements

* Replaced High/Critical CVE container use in Spire
* Addressed CVE remediation for `postgres-operator`
* Addressed Expat-15: High/Critical CVE container use in UAS/UAI
* IPXE binary name randomization for added security
* Access allowed to heartbeat's tunables OPA for `cray-heartbeat`

### Customer-requested enhancements

* Added the ability to list all lock conditions with `cray hsm locks` API
* Enabled pressure stats on all nodes with Linux 5.x kernel

### Documentation enhancements

* Added documentation for:
  * Add/Remove/Replace NCN procedures using `sat swap blade`
  * How to troubleshoot `ncn-m001` PXE loop
  * NCN image modification using IMS and CFS
  * Minimal space requirements for CSM V1.3.0
  * The new `cray-externaldns-manager` service
* CAN documentation updated to reflect BICAN

## Bug fixes

* TBD

## Deprecations

* CAPMC v1 partial deprecation
* HSM v1 interface

See [Deprecated features](introduction/differences.md#deprecated-features).

## Removals

* TBD

## Known issues

### Security vulnerability exceptions in CSM 1.3

* TBD
