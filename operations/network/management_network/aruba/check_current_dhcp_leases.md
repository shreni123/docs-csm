# Check Current DHCP Leases

Use the Kea API to retrieve data from the DHCP lease database.

For each of the commands replace `SYSTEM_DOMAIN_NAME` with the system domain name.

## Prerequisites

An authentication token is set up. If one has not been set up, log on to `ncn-w001` or a worker/manager with `kubectl` and run the following:

```bash
export TOKEN=$(curl -s -k -S -d grant_type=client_credentials -d client_id=admin-client -d client_secret=`kubectl get secrets admin-client-auth -o jsonpath='{.data.client-secret}' | base64 -d` https://api.nmnlb.SYSTEM_DOMAIN_NAME/keycloak/realms/shasta/protocol/openid-connect/token | jq -r '.access_token')
```

Once an authentication token is generated, these commands can be run on a worker or manager node.

## Commands to Check Leases

Get all leases:

> **WARNING:** This may cause the terminal to crash based on the size of the output.

```bash
curl -H "Authorization: Bearer ${TOKEN}" -X POST -H "Content-Type: application/json" -d '{ "command": "lease4-get-all",  "service": [ "dhcp4" ] }' https://api.nmnlb.SYSTEM_DOMAIN_NAME/apis/dhcp-kea | jq
If you have the IP and are looking for the hostname/MAC address.
```

IP Lookup:

```bash
curl -H "Authorization: Bearer ${TOKEN}" -X POST -H "Content-Type: application/json" -d '{ "command": "lease4-get", "service": [ "dhcp4" ], "arguments": { "ip-address": "x.x.x.x" } }' https://api.nmnlb.SYSTEM_DOMAIN_NAME/apis/dhcp-kea | jq
```

Use the MAC to find the hostname/IP Address:

```bash
curl -H "Authorization: Bearer ${TOKEN}" -X POST -H "Content-Type: application/json" -d '{ "command": "lease4-get-all",  "service": [ "dhcp4" ] }' https://api.nmnlb.SYSTEM_DOMAIN_NAME/apis/dhcp-kea | jq '.[].arguments.leases[] | select(."hw-address"=="XX:XX:XX:XX:XX:5d")'
```

Use the hostname to find the MAC/IP address:

```bash
curl -H "Authorization: Bearer ${TOKEN}" -X POST -H "Content-Type: application/json" -d '{ "command": "lease4-get-all",  "service": [ "dhcp4" ] }' https://api.nmnlb.SYSTEM_DOMAIN_NAME/apis/dhcp-kea | jq '.[].arguments.leases[] | select(."hostname"=="xNAME")'
```

View the total amount of leases:

```bash
curl -H "Authorization: Bearer ${TOKEN}" -X POST -H "Content-Type: application/json" -d '{ "command": "lease4-get-all",  "service": [ "dhcp4" ] }' https://api.nmnlb.SYSTEM_DOMAIN_NAME/apis/dhcp-kea | jq '.[].text'
```

[Back to Index](../index.md)
