# Cray System Management (CSM) - Release Notes

[CSM](glossary.md#cray-system-management-csm) 1.3 contains approximately 500 changes spanning bug fixes, new feature development, and documentation improvements. This page lists some of the highlights.

## New

### Monitoring

* TBD

### Networking

* TBD

### Miscellaneous functionality

* Integrated Kyverno Native Policy Management engine
* Ansible has been added to [NCN](glossary.md#non-compute-node-ncn)s
* Added support for procedures:
  * Replace/Remove/Add NCNs
  * Add River cabinets
* Integrated Argo server workflow engine for Kubernetes
* Technology Preview: [BOS](glossary.md#boot-orchestration-service-bos) V2
  * Asynchronous boot state handling and [CRUS](glossary.md#compute-rolling-upgrade-service-crus) replacement for rolling upgrades
* Technology Preview: Tenant and Partition Management Service (TAPMS)
* Added support for using SCSD to enable or disable TPM BIOS setting on Gigabyte and HPE hardware
* Boot NCNs using private S3 bucket
* Enable [IMS](glossary.md#image-management-service-ims) recipe templating to allow for dynamic repository selection
* CSM health check performance improvements
  * HMS tests now execute in parallel using Helm Test
  * NCN and Kubernetes health checks now execute in parallel and eliminate lengthy output for tests that pass
* Included [SAT](glossary.md#system-admin-toolkit-sat) CLI in CSM (see [SAT in CSM](operations/sat/sat_in_csm.md))

### New hardware support

* Aruba JL705C, JL706C, JL707C management network switches
* Milan-based DL325 as a Compute Node
* Olympus Antero Blade (AMD Genoa) with Slingshot 11
  * No power capping support

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
* Addressed Expat-15: High/Critical CVE container use in [UAS](glossary.md#user-access-service-uas)/[UAI](glossary.md#user-access-instance-uai)
* IPXE binary name randomization for added security
* Access allowed to heartbeat's tunables OPA for `cray-heartbeat`

### Customer-requested enhancements

* Added the ability to list all lock conditions with Cray [HSM](glossary.md#hardware-state-manager-hsm) locks API
* Enabled pressure stats on all nodes with Linux 5.x kernel

### Documentation enhancements

* Added documentation for:
  * Add/Remove/Replace NCN procedures
  * Add/Remove/Replace compute nodes using `sat swap blade`
  * How to troubleshoot `ncn-m001` PXE loop
  * NCN image modification using [IMS](glossary.md#image-management-service-ims) and [CFS](glossary.md#configuration-framework-service-cfs)
  * Minimal space requirements for CSM V1.3.0
  * The new `cray-externaldns-manager` service
* [CAN](glossary.md#customer-access-network) documentation updated to reflect BICAN

## Bug fixes

* TBD

## Deprecations

The following features are now deprecated and will be removed from CSM in a future release.

* [BOS](glossary.md#boot-orchestration-service-bos) v1 is now deprecated, in favor of BOS v2. BOS v1 will be removed from CSM in a future release.
  * It is likely that even prior to BOS v1 being removed from CSM, the [Cray CLI](glossary.md#cray-cli-cray) will change its behavior when no
    version is explicitly specified in BOS commands. Currently it defaults to BOS v1, but it may change to default to BOS v2 even before BOS v1
    is removed from CSM.

For a list of all deprecated CSM features, including those that were deprecated in previous CSM releases but have not yet been removed,
see [Deprecated Features](introduction/deprecated_features/README.md).

## Removals

* TBD

## Known issues

### Security vulnerability exceptions in CSM 1.3

* TBD
