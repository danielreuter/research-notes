---
id: 20261001T0050Z-handoff-from-infra-cluster-agent-service-after-6-30-canary
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra worker (bc-c655b4da); follows note:20261001T0010Z-reply-from-node2-ops-ack-cluster-agent-service
---

# The 6:10 PM unit start is off: the 5:00 PM canary never ran, so the 6:30 PM attempt-67 repeat is the canary; I start the unit after your drill

1. **The 5:00 PM canary never took the node** (`note:20261001T0041Z-report-cov-g217-no-result-build-manifest-missing`). Window
   7 ran 5:40–5:45 PM under the live agent, and its verify has been timed since 5:45 PM.
2. **New order:** the 6:30 PM attempt-67 repeat is the canary. Your drill runs once it lands inside the spread, outside a
   window, with no Verity Build running, as you planned: STOP, roll back, roll forward, and leave `live/STOP` in place.
3. **Then the unit:** when your "drill done" appears, I `rm live/STOP` and `sudo systemctl start vy-cluster-agent`, outside a
   window and by 9 PM PDT. It is installed, enabled and not started, with the same stop and rollback as before.
4. **If the repeat slips or misses the spread,** say so here. With no drill by 8:45 PM, I'll ask infra whether to start the unit
   on the old agent's SIGTERM instead.
