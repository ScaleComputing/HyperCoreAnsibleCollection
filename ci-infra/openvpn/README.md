# About

# How to run

On arbitrary host (will be called vpn-host), install docker-ce.
Copy `scale_computing/hypercore/ci-infra/openvpn` subdir to the vpn-host.

Setup openvpn config directory.
We want to store username and password into `login.txt` file.
It will contain username and password, on first two lines, and only that
```yaml
cp path/to/pfsense-UDP4-1194-USERNAME-config.ovpn scale_computing/hypercore/ci-infra/openvpn/config/vpn.conf

# Check ovpn conf will use login.txt file
# Path is used inside container.
grep -e auth-user-pass scale_computing/hypercore/ci-infra/openvpn/config/vpn.conf
auth-user-pass /vpn/login.txt

# Check login.txt content
cat scale_computing/hypercore/ci-infra/openvpn/config/login.txt
your-username
your-password
```

Run:
```
cd scale_computing/hypercore/ci-infra/openvpn
docker-compose rm -f; docker-compose down --remove-orphans; docker-compose build; docker-compose up
```

Test it works:
```
# on vpn-host
curl -vk -u admin:CHANGEME https://localhost:8443/rest/v1/ping
```

Ensure port 8443 is allowed/forwarded at vpn-host provider. For specific IPs only!
Test again from allowed external IP (xlab-lan, xlab-dmz), and from not-allowed external IP (xlab-guest WiFi):
```
curl -vk -u admin:CHANGEME https://VPN_HOST_PUBLIC_IP:8443/rest/v1/ping
```

# Notes

Notes:
- Openvpn need privileged mode, or NET_ADMIN caps.
- Once vpn client runs, it should be used to route traffic for other containers.
  That requires modifying network configuration, routing tables, firewall if it is set - PITA.
- So we will instead use someting like HTTP proxy.
  https://hub.docker.com/r/dperson/openvpn-client recommends nginx (no auth).
  In Messer project we used squid proxy with auth.
  But we do not want to seach for corner cases with real HTTP proxy (code using request and urllib3 would need some adjustmens).
  Instead we will forward traffic on TCP level with socat.

socat problems:
- No auth possible.
  We need to protect access to port 8433 with firewall.
  Only IPs where CI tests run will be allowed to access.
