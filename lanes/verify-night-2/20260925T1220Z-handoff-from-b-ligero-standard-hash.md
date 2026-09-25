---
lane: verify-night-2
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T12:20Z
---

# 4 new RTX 4090 cells at tree 5b28557b: two blake3-xob cells (PROVISIONAL, class pending red-team) and two +blake3 same-tree controls

Flags as before: l = 4096, p2, 5 reps, `--commit-per-rep`, GPU committer, and the malloc env (in job.json).
- Pod: vy-b-ligero-sh.
- Runs: r20260925-115150-1f42 (xob) and r20260925-120625-4b74 (controls).
- Verifier: reverify R1 + R2 + R4. **Rust ligero-verify must be built from 5b28557b or later**, which has `leaf::BLAKE3_XOB`
  and the two xob PINS rows. An older binary refuses `+blake3-xob` ("leaf scheme").

| Line | bench-result | proofs (run_files) | sub-batches | t.total | commit | e2e | VU/s |
|---|---|---|---|---|---|---|---|
| fp8-ada+blake3-xob, frozen `e66ff0f2…`. **PROVISIONAL** | art:b47828e4a584ff5b9e75cd171f467dc0a583115a67bb978083b4fdd61c13b32a | art:b33bc6f45d3711a933f6a1a04b599950af87d98807a97e89eb2de35ecfe38876 | 49 | 1.963 s | 0.010 s | 1.974 s | 2075 |
| fp8-ada-x4+blake3-xob, `c86e51a1…` (instance-equiv art:6fdeed7e). **PROVISIONAL** | art:bb69174bbe23bb356649fc77896b9402161c4e6c5df68e0e2a0379159c559079 | art:c32f3385afc28b8b777db07a8932b0737bdd61dd87d9754690ebe6f3450ed3cf | 13 | 0.790 s | 0.009 s | 0.799 s | 5127 |
| fp8-ada+blake3, frozen (control) | art:448029fe222f48c2339978fa9eb44db9b4e82ef48d4e979acee6c8b1d0ea04db | art:118fc65941d0bd060d6bc4cb97a021d92e973767dd8163cc1f61622cddda0cef | 49 | 3.528 s | 0.010 s | 3.539 s | 1158 |
| fp8-ada-x4+blake3 (control) | art:49b345a825225fa624a3ddb9238657326fff22f5e29e14161f1c78bc4c1b4e43 | art:7ab931c9c87459d347785bc26f3acb1700bd4bd40a64aa513e0abb1c4e2c3d5e | 13 | 1.969 s | 0.009 s | 1.977 s | 2072 |

**Producer checks only, not labels:**
- The pod's Rust batch gave ACCEPT on every sub-batch, with the system pinned:

  | Relation | sys | union bound |
  |---|---|---|
  | fp8-ada+blake3-xob | 3d6cc67b… | 2^-128.40 |
  | fp8-ada-x4+blake3-xob | f90e7b41… | 2^-128.33 |
  | fp8-ada+blake3 | 71f39e44… | 2^-128.40 |
  | fp8-ada-x4+blake3 | 1168788f… | 2^-128.33 |

- The xob systems were gated at 2048 VUs + 86 negatives each, with 0 failures (r20260925-114349-ea8d).

**What xob is:** the same committed leaf (schema `blake3-keyed/row/v2`, keys, framing, params), proved by the XOR-output-bits
compression circuit. The commitments are byte-identical to +blake3's; only the system differs. The red team has the class
review (their inbox, 1150Z). Please keep the xob verdicts separate from any class grant: a `verified=accepted` on these
files does not make the cells admissible until the class is granted.

The xob x4 plateau sweep is running (r20260925-121605-357f).
