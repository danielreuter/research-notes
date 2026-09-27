---
lane: coordinator
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-27T03:20Z
---

# 9 total cells on EU-NL-1 (L40S + H100): 8 measured, 0 registered. `bench.cell register` refused them all because the runs' `placement.json` has no pod_id. Your call: force-register on the boot-id evidence, or re-run with a probe fix

**The run:**
- **Pair:** L40S prover xxmt4blnx3d5uq (machine wmu7hc6fck55, ASUSTeK ESC8000A-E11, bare metal) and H100 SXM verifier
  5x4lwhftnv9z8t (machine 6i0r8tuwk7kw). Both are in EU-NL-1 behind a shared NAT IP, linked over the global network
  (`5x4lwhftnv9z8t.runpod.internal`, 30/30 connects, median 0.69 ms).
- **Gate:** r20260927-020416-a981, GATE OK on the prover pod.
- **Pods:** both terminated at 03:05Z after the records were fetched.
- **Spend:** about $5 for this run; about $11 of $25 in total.

| cell | prover run / verifier run | B (proofs) | VU/s | RTT | interaction | contended |
|---|---|---|---:|---:|---|---|
| #39 K1536 | r20260927-021747-e3b2 / …021508-bd5b | 2,048 (1) | 2,716 | 0.94 ms | pass | false |
| #57/#67 K2048 | …022036-c6b1 / …022028-2db1 | 2,048 (1) | 2,636 | 0.76 ms | **+15 % (fails ±10 %)** | false |
| #60 K4096 | …022328-d426 / …022320-6425 | 2,048 (2) | 1,094 | 1.54 ms | pass | false |
| #57 K9216 | …022835-9947 / …022740-53c7 | 1,024 (2) | 434 | 0.75 ms | pass | false |
| #60 K14336 | (prover launch failed after the verifier started; not run) | — | — | — | — | — |
| #101 K2048 | …024735-1352 / …024551-7bc3 | 4,096 (1) | 3,221 | 0.85 ms | pass | false |
| #101 K8192 | …025208-0fe3 / …025155-4db3 | 1,024 (1) | 954 | 0.32 ms | pass | false |
| #57 K2304 ChunkTail(4) | …025646-cc9a / …025622-6647 | 2,048 (1) | 963 | 0.78 ms | pass | false |
| #39 K8960 ChunkTail(17) | …030053-0004 / …030039-6fc7 | 1,024 (2) | 254 | 0.77 ms | pass | false |

**Why register refused:**
- Each cell was refused with "the prover run did not record pod_id / the verifier run did not record pod_id: the NAT
  exception is re-checked on the runs' own records".
- `placement.probe` reads `RUNPOD_POD_ID` from the job's environment. A research job started over ssh doesn't inherit
  the container's `RUNPOD_*` variables, so pod_id, public_ip and datacenter are all null in every run's placement.json.
- **Evidence the runs are the planned pods:** both runs of every cell record the same boot_ids as the plan's probe of
  those pods (prover ffb05349…, verifier d9fde200…). So there was no reboot and no pod swap between plan and run. They also
  record bare-metal DMI (hypervisor false) and the internal link.
- **Fix:** cursor/flock-backend-4983 @ 852816d6. `placement.probe` now falls back to `/proc/1/environ` for `RUNPOD_*`,
  with a test. bench-spine should take it into main.
  - I couldn't check on a live pod that RunPod's init environment carries `RUNPOD_POD_ID`.

**Options:**
- **(a) Register the 8 with `bench.cell register --force`,** plus a label that cites the boot-id match. K2048 would record
  its interaction failure. red-team-flock-3 decides whether that satisfies S5.
- **(b) Re-run the 9 on a fresh EU-NL-1 L40S + H100 pair with the probe fix,** about $5, within the cap. K14336 would get
  a retry, and K2048 a second interaction measurement.

No pods are running. The old cells are not labelled `superseded_by` yet, because nothing registered.
