# syntax=docker/dockerfile:1
FROM dperson/openvpn-client
RUN apk add socat tcpdump
COPY openvpn.sh /usr/bin/
ENTRYPOINT ["/sbin/tini", "--", "/usr/bin/openvpn.sh"]
