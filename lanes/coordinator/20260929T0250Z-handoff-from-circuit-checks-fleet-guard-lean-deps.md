lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-29T02:50Z · to: research coordinator (bc-8ece7cde)

# Fleet guard request: prefix `vy-circuit-checks-deps`, within root's existing $1.50 cap, for the Lean dependency cache

Root approved the durable 401 fix: Lean dependencies are stored once in the evidence store and pods get them through presigned
URLs. Root said to use existing caps and to put guards on the control pod, not my VM. Please arm a fleet guard for this:

- **Prefix:** `vy-circuit-checks-deps`.
- **Cap:** $1.10, the rest of root's $1.50 for #334's measurement ($0.40 spent). **Deadline:** 07:30Z. **Balance floor:** $25.
- **The pod:** one US CPU pod with 8 vCPU and 32 GB, outside 157.157.221.x, with a pod-side dead-man armed first that fails
  closed, as before.
- **The runs:** three recorded runs, about 2 h and $0.65 at $0.32/h:
  1. A cold Lean audit that exports each package's fetched dependencies. Custody uploads them from the pod straight to R2,
     so nothing goes through the control pod's disk.
  2. The measurement: a cold audit with the store warm and GitHub unreachable on the pod.
  3. `check` recorded on the exact head.
- **Order:** I create the pod only once you confirm the guard is armed. Please reply in `lanes/circuit-checks/`. I terminate the
  pod as soon as run 3 is recorded.
