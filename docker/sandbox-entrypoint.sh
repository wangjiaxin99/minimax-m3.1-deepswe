#!/usr/bin/env bash
set -euo pipefail
: "${REPO_DIR:?}" "${CONTROL_GATEWAY:?}" "${SERVER_PORT:?}" "${SANDBOX_IP:?}"
mkdir -p "${REPO_DIR}/state"
# Docker-in-Docker otherwise drops the outer 127.0.0.11 resolver and may fall
# back to public DNS. Relay the actual outer resolver for nested image builds.
dns_upstream=$(awk '$1 == "nameserver" {print $2; exit}' /etc/resolv.conf)
test -n "$dns_upstream"
dnsmasq --keep-in-foreground --user=root --no-resolv \
  --server="$dns_upstream" --listen-address="$SANDBOX_IP" --bind-interfaces &
# Squid permits ports 80/443. This is plain HTTP on port 443, as in the historical run.
socat -t 86400 TCP-LISTEN:443,reuseaddr,fork "TCP:${CONTROL_GATEWAY}:${SERVER_PORT}" &
# Avoid the dind entrypoint's TCP API defaults. Only expose the shared Unix socket.
exec /usr/local/bin/dockerd-entrypoint.sh dockerd \
  --host="unix://${REPO_DIR}/state/docker.sock" --group=root --init \
  --dns="${SANDBOX_IP}" \
  --bip="${DAEMON_BRIDGE}" \
  --default-address-pool="base=${DAEMON_ADDRESS_POOL},size=24"
