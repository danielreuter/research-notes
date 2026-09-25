---
lane: x4-hopper-blake3
kind: report
created: 2026-09-25T17:43Z
status: final
---

CHECKPOINT 775786b7 (23:07Z) [final] tip 775786b7; cells blake3 art:d88a9948/art:5ea60c40 (verified), xob art:955a52e0 7.08e7x / art:f15909f5 6.94e7x for verification; pod terminated 23:06Z, ~$18.6
CHECKPOINT 775786b7 (22:14Z) [open] POD NEEDED until ~23:00Z: xob run r20260925-211547-43ab has the fp8-hopper-x4+blake3-xob plateau (32768) done and bf16 xob at p4; its outputs publish only at run end. Then terminate + FINAL.
CHECKPOINT 775786b7 (21:16Z) [open] cells art:d88a9948 fp8 1.50e8x @65536, art:5ea60c40 bf16 1.47e8x @16384 (+14 equiv docs) handed off 2112Z; xob PINS 775786b7; xob sweeps r20260925-211547-43ab running, polling in-turn
CHECKPOINT 9a78cd68 (20:01Z) [open] fp8-hopper-x4+blake3 sweep done: plateau 65536 at 4271 VU/s (~1.5e8x vs 1978.9T; slower than sha256 x4's 6162), pinned Rust 193/193, equiv equal=True; bf16 sweep running (r20260925-182011-dcc4)
CHECKPOINT 9a78cd68 (19:44Z) [open] fp8-hopper-x4+blake3 sweep at p7 131072 (e2e ~4.2-4.4k VU/s from 32768 on; in-process verifier ~400 s/rep dominates wall); bf16 sweep next; polling in-turn r20260925-182011-dcc4
CHECKPOINT 9a78cd68 (18:22Z) [open] WAITING r20260925-182011-dcc4 on vy-x4-hopper-blake3-h100 (pinned sweeps fp8/bf16-hopper-x4+blake3 l4096 p4 from 1024 + equiv), check after 19:30Z; agent bc-4c84a7da-0134-54f4-a563-e23117bb6a32; done: PINS 9a78cd68 pushed, merge-ready handoff 1824Z; next: verification handoff
CHECKPOINT cd963fd4 (17:50Z) [open] WAITING r20260925-174812-50ad on vy-x4-hopper-blake3-h100 (bootstrap OK; fixtures+gates fp8/bf16-hopper-x4+blake3), check after 18:40Z; agent bc-4c84a7da-0134-54f4-a563-e23117bb6a32; next: PINS rows commit, then 20-pinned-sweeps.sh
CHECKPOINT cd963fd4 (17:46Z) [open] pod vy-x4-hopper-blake3-h100 (chrjjy3bvb2aif, H100 80GB HBM3 ref part) created+registered guard 60; next: sync + bootstrap, then 10-pins-gates LEAF=blake3 RELS='fp8-hopper-x4 bf16-hopper-x4'
CHECKPOINT cd963fd4 (17:43Z) [open] started: branch lane/x4-hopper-blake3 at cd963fd4; reading contract, pod scripts; no pod yet; agent bc-4c84a7da-0134-54f4-a563-e23117bb6a32

## FINAL

~~~text
tip: lane/x4-hopper-blake3 @ 775786b7 (base origin/main@cd963fd4)        merge-with: none
known-failures: none    pod: terminated 23:06Z; ~$18.6 (vy-x4-hopper-blake3-h100, 17:46-23:06Z at $3.49/h)
artifacts: art:d88a9948 art:5ea60c40 art:d5a814d7 art:f200431e art:a400cae2 art:6b27220a art:955a52e0 art:f15909f5 art:bce73cd7 art:a5225b9d art:72745743 art:04f24f73
~~~

| cell (H100 SXM5 80GB, l=4096 p=4, 5 warm reps) | result | plateau | VU/s | overhead |
|---|---|---|---|---|
| fp8-hopper-x4+blake3 | art:d88a9948 | 65536 | 4271 | 1.50e8x |
| bf16-hopper-x4+blake3 | art:5ea60c40 | 16384 | 2177 | 1.47e8x |
| fp8-hopper-x4+blake3-xob | art:955a52e0 | 32768 | 8978 | 7.08e7x |
| bf16-hopper-x4+blake3-xob | art:f15909f5 | 32768 | 4589 | 6.94e7x |

- PINS: 9a78cd68 (blake3; gates r20260925-174812-50ad) and 775786b7 (blake3-xob; gates r20260925-211046-ede9). All gates
  2048 VUs + 86 negatives, 0 failures.
- Sweeps: r20260925-182011-dcc4 (blake3), r20260925-211547-43ab (xob). Equiv docs for every size: r20260925-204225-9f8d, plus
  the plateau docs in the sweep runs.
- The blake3 cells are verified by verify-night-3 and labelled by red-team-standard-hash-2. The xob cells await verification,
  and the red-team review of 775786b7.
- Finding: xob runs about 2.1x faster than blake3 on both H100 lines, likely because the blake3 systems exceed 2^16 rows and the
  xob ones don't (encoding cost roughly doubles).
- Handoffs received: 20260925T1836Z-handoff-from-coordinator.md (plateau cells, rounds/bytes/RTT record): done; both
  handoffs report them.
- Handoffs sent: lanes/coordinator/20260925T1824Z (merge + class request), 2112Z (blake3 cells), 2308Z (FINAL, xob cells).
