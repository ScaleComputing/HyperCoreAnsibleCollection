We need a reliable 2 NTP servers for testing NTP reconfiguration.

Setup them once in VMs

```
apt install -y chrony ntpdate
cat /etc/chrony/chrony.conf
  # See chrony.conf example file.
  # Just add 'allow all' line if needed
grep 'allow all' /etc/chrony/chrony.conf || echo 'allow all'

systemctl enable chrony
systemctl restart chrony
chronyc tracking

ntpdate -qup1 localhost
```

Check from outside if firewall allows NTP traffic - port 123/UDP.
