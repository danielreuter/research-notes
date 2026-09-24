---
lane: fill-consumer
kind: report
created: 2026-09-24T06:37Z
status: final
---

CHECKPOINT 444084d3 (07:46Z) [final] 4 cells: 5090 bare 0.0340 (art:d5c9e1f3), 5090 col2 0.1387 (art:99867b4c, fix 444084d3 frozen ref), 4090 col2 0.3474 (art:1abdf12a); 4090 bare 0.0907 unbeaten. All live-accepted alts; verify-night handoff 0725Z; pods terminated.
CHECKPOINT fd635ab (07:06Z) [open] 07:13Z 5090 done+registered (bare l8192 p8 local 0.034/live 0.043, art:33b9b625 a1b2c5dc c2e34e1d...). 5090 col2 was rejected: fp4 hashed ref said synthetic/dev -> fix 444084d3, rerunning. 4090 col2 l8192 p4 ~0.350 local; 4090 live running on vtest.
CHECKPOINT 1b0ffb6 (06:37Z) [open] 06:53Z pods up EU-RO-1 SECURE: 4090 9u778ye2z127j4, 5090 kjzbulmek8or0z, verifiers cpu3c ver4090 x5qbvwxa510d9z (8vCPU) / vtest 1vchd2ej1iey9k (16vCPU); local sweeps running (warm + 3 rounds x 6 arms each). Next: verifier RTT, live rounds.

# fill-consumer: Table 2 B-Ligero and B-Ligero + in-proof hash on RTX 4090 FP8 and RTX 5090 NVFP4

## Outcome
All four cells have fresh candidates on the fixed runner. Each one is live-accepted, self-consistent (buckets ≤ t.total,
`contract.validate` 0 problems, not contended) and registered with PRESERVED dumps. `bench.tables` gives each exactly one
rejection reason: `not independently verified`. The handoff to verify-night is
`lanes/verify-night/20260924T0725Z-handoff-from-fill-consumer.md`.

**The 5090 column-2 cell was empty because of a label bug, not a missing run.** `fp4/hashed.py` labelled its instances
`synthetic` / `dev`, although it proves the frozen NVFP4 set (it draws `chain.instances_fp4` at seed 20260922 and uses
`chain.instances_digest`, the definition the contract pins). Fix: **444084d3** on lane/fill-consumer. After rerunning on
it, the results carry the frozen ref exactly and Rust `ligero-verify` accepts them against the pinned `fp4-nvf4+hash`.

| row / column | chosen config | best local t.total (overhead) | best live-accepted t.total (t.total_live, overhead) | in Table 2 now |
| --- | --- | --- | --- | --- |
| 5090 NVFP4, B-Ligero | `fp4-nvf4` l=8192 p8 | 0.0340 s (4.5e6×) art:d5c9e1f3 | 0.0417 s (0.0430; 5.5e6×) art:33b9b625 | 0.0383 s (5.1e6×) |
| 5090 NVFP4, + in-proof hash | `fp4-nvf4+poseidon2 --auth included-hash` l=8192 p8, tree 444084d3 | 0.1387 s (1.85e7×) art:99867b4c | 0.1457 s (0.1466; 1.94e7×) art:a3cc225d | empty |
| 4090 FP8, B-Ligero | `fp8-ada-v3x4` l=4096 p8 (equiv art:d40f5065) | 0.0938 s (2.46e6×) art:1b6f3299 | 0.1020 s (0.1033; 2.68e6×) art:3524269d | 0.0907 s (2.4e6×), not beaten |
| 4090 FP8, + in-proof hash | `fp8-ada --auth included-hash` l=8192 p4 | 0.3474 s (9.1e6×) art:1abdf12a | 0.3773 s (0.3792; 9.9e6×) art:3a3ae66e | 0.3879 s (1.0e7×) |

The frozen-set fallback for the 4090 bare column (`fp8-ada` l=16384 p4, live) came in at 0.1836-0.1940 s, art:f36d9530 and
two more. Once verify-night labels them, the renderer keeps the minimum `t.total`. That improves the 5090 bare cell, fills
the 5090 column-2 cell and improves the 4090 column-2 cell. The 4090 bare cell stays at art:fb4934af.

## What ran
- Pods, all SECURE EU-RO-1: RTX 4090 `9u778ye2z127j4` (EPYC 7443, quota 10.2 cores, PCIe gen4 x8), RTX 5090 `kjzbulmek8or0z`
  (Ryzen 9950X, quota 13.6), verifier `vy-fill-consumer-vtest` `1vchd2ej1iey9k` (cpu3c 16 vCPU, idle EPYC 9655, probe
  0.6-0.7 ms and 5-7 Gbps from both provers, `LIVE_JOBS` 15).
- Dedicated 4090 verifiers all failed the same-DC checks. cpu3c 8 and 16 vCPU pods sat on hosts at load 320-400 and gave a
  2.6-2.7 ms probe. An NVIDIA L4 pod was capped at ~0.9 Gbps. No other SKU had stock. So the 4090 used vtest **after** the
  5090's live rounds, one set after the other and never at once. The schedule is in the verify-night handoff (kb:
  live-verifier.md).
- Local sweeps: 3 rounds, alternating order, reps 5, warm-ups first (`evidence/pod-scripts/10-*`, `11-*`). On the 5090,
  l=8192 beat l=16384 and l=4096 on both columns. On the 4090, column 2 had l=16384 p8 OOM on 24 GB; l=8192 p4 won over
  6 rounds (0.347-0.353, one run at 0.390). The 4090 bare sweep confirmed v3x4 p8 as the pick (coordinator 06:47Z).
- Live: 3 rounds per chosen config (`20-*`, `21-*`, `22-*`). All 120 verifier sessions were accepted, and the verifier's
  records are preserved as **art:970c7d81** (run-files/v1, 9.5 MB, 3602 files, SHA256SUMS).
- The 4090 host was noisy. Reps within a single run swung 0.09-0.37 s while the contention guard stayed silent, and there
  was no SECURE 4090 stock for a replacement at 07:05Z. The extra noise only slows runs (kb: pods-4090.md).
- Registration ran from the pods (`60-register.sh`, a short-lived credential in the environment only): 38 bench-result/v1 +
  38 run-files/v1. The full id list is in `evidence/registered-{4090,5090}.txt` and the handoff. The nine pre-fix 5090
  column-2 results (art:981ffbe9 fb3ad776 57ee5c58 e5d89c39 8fb32739 0847c1c5 f57b319b 5c9eae89 48d357cd) are rejected on
  instances and superseded.

## Handoffs received
- `20260924T0647Z-handoff-coordinator-4090-sweep-done.md`: acted on. The 4090 bare pick is v3x4 p8 live (3 rounds), the v1
  p4 live fallback ran, and the rest of the time went to column 2 and the 5090.

## FINAL

~~~text
tip: lane/fill-consumer @ 444084d3 (base lane/fill-consumer@1b3c7be6)        merge-with: none
known-failures: none (no tests run; the change is a 2-line label fix)    pod: terminated 07:23-07:24Z (4090, 5090, verifier); ~$3.3
artifacts: art:d5c9e1f3 art:33b9b625 art:99867b4c art:a3cc225d art:1b6f3299 art:3524269d art:1abdf12a art:3a3ae66e art:f36d9530 art:970c7d81
~~~

Merge 444084d3 for any further fp4-nvf4+poseidon2 run: without it the 5090 column 2 can never count. Every candidate waits
on verify-night (handoff 07:25Z). kb updated: fp4-nvf4.md (the label gotcha, 5090 l=8192 numbers), pods-4090.md (column-2
configs, the l16384 p8 OOM, noisy hosts), live-verifier.md (choosing a same-DC verifier, `LIVE_JOBS`, puts from a verifier
pod).
