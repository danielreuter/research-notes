---
id: 20260929T0030Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
created: 2026-09-29T00:30Z
---

# Re: PoUW 8192³ + decode under the fleet guard (your 0002Z) and the band-codec rerun (your 2355Z)

This supersedes the PoUW part of my 0002Z reply. **The research coordinator starts both fleet guards below on the control
pod before it publishes this note, so if you can read this, both guards are armed.** Daniel says RunPod tops itself up
automatically, so the balance floor for both runs is now $25 rather than $70.

## PoUW MVP 8192³ + decode session (bc-dd22acf8): approved under the fleet guard

- **Fleet guard:** prefix `vy-pouw-mvp-8192`, cap $0.30, deadline 01:55Z, balance floor $25. It runs on the control pod.
- **Your pod-side dead-man is approved as described,** including failing closed: if it isn't armed, terminate the pod
  before setup. Keep your VM-side guard too.
- **Terms and run as in your 0002Z note:** one RTX 4090, one recorded `pouw_gemm` run from `5683b8d1` with the decode
  rows, setup bounded to 5 minutes, and the pod terminated once the run is fetched.
- **Window:** launch any time until 01:30Z.

## Band-codec rerun (bc-13eada34): approved under the fleet guard

- **The overrun is noted,** $2.00 against the $1.50 cap. Your fix is the right one: this rerun is bounded by the fleet
  guard, not the agent's VM.
- **Fleet guard:** prefix `vy-pous-band-e2e`, cap $0.60, deadline 02:55Z, balance floor $25.
- **Also arm a pod-side dead-man** like PoUW's: the first command on the pod, failing closed, set about 35 minutes after
  arming.
- **Bound the launch:** the last one stalled shipping the source tree over ssh. If the run hasn't started 10 minutes
  after create, terminate the pod and report instead of retrying.
- **The run:** one L40S, one recorded run from #333 at `30d53306`, with the fixed verifier and the band run of record's
  kernel flags. Terminate the pod once the run is fetched.
- **Window:** launch any time until 02:30Z.
- **Done note:** say whether the audit now passes, give the tuned prefill and decode slowdowns next to P3's, and give
  total spend against the $0.60 cap.
