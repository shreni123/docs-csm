# Audit Logs

How to enable and disable audit logging for host and Kubernetes APIs.

Audit logs are used to monitor the system and search for suspicious behavior.
Host and Kubernetes API audit logging can be enabled to produce extra audit logs for analysis.
Enabling audit logging is optional and will generate some load and data on the non-compute nodes \(NCNs\).
Host and Kubernetes API audit logging is not enabled by default.

To enable or disable host and Kubernetes API audit logging, change the CSI setting:

* `ncn-mgmt-node-auditing-enabled`: Set to `true` to enable host logging or to `false` to disable host logging.
* `k8s-api-auditing-enabled`: Set to `true` to enable Kubernetes API logging or to `false` to disable Kubernetes API logging.

When the CSI setting is changed, each NCN will need to be restarted to apply the new setting.

Host audit logs are stored in the `/var/log/audit/HostOS` directory on each NCN. Host audit logging uses a maximum of 60GB on each NCN when using log rotation settings. The log rotation settings are enabled when the Ansible playbook is run.

The Kubernetes API audit logs are stored in the `/var/log/audit/kl8s/apiserver` directory on each master NCN. Kubernetes API audit logging uses a maximum of 1GB on each master NCN when using log rotation settings.
