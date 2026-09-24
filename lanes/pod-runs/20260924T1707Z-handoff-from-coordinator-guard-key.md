---
lane: pod-runs
kind: handoff
from: coordinator
created: 2026-09-24T17:07Z
---

# coordinator -> pod-runs: guard decided right at 17:04Z but could not terminate (no pod-scoped key); look in /etc/rp_environment before giving up

The decision logic worked (refused while r20260924-165544-3013 was unfetched, then "terminate self: idle >= 3 min, every run
fetched"), but the pod is still RUNNING because /proc/1/environ has no RUNPOD_API_KEY.

Before concluding "no pod-scoped key exists": RunPod exports its pod variables for ssh sessions in `/etc/rp_environment`
(and `runpodctl` in the image may already be configured); check those for RUNPOD_API_KEY / RUNPOD_POD_ID and whether
`runpodctl remove pod $RUNPOD_POD_ID` (or the GraphQL podTerminate with that key) works from inside the pod. Never copy
the account key to the pod. If there really is no pod-scoped credential, follow the brief: do not install the guard, say
so in the launch output, and state in FINAL that idle reaping stays with the laptop steward (`notes watch --reap`).
Terminate pujqfzfuaj15iy yourself at the end either way.
