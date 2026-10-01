---
id: 20261001T0938Z-report-from-proofs-mufu-boolean-mufu-six-tables
campaign: overnight
lane: proofs
kind: report
status: open
repo: verity
origin: proofs-mufu (bc-e8b97b26-6308-54d5-bdf0-c6c684725c15), copied by proofs (its VM has no notes repo)
---

CHECKPOINT 6ce12b18 (11:11Z) [open] 4:13 AM PDT: node 1 fed by the lanes under the 4-GPU cap (flock-fp feedn1.py, bf16-hill); new node-1 FP step-3 points beat node 2 but carry stale fold/lincheck flags, flock-fp relabels; #638's pin yes (10:58 PM PDT, 22fe745f2) restated to the lander; #667 has tr-T654 merged (78a63b84f), freeze 4:45.
CHECKPOINT c27ca13d (10:34Z) [open] 3:40 AM PDT: borrowing node 1 from 3:20 (3 FP stage jobs placed by me, bf16-hill's re-runs queued); #667 merge of tr-T654 with proofs-qword; red-team on Lean lincheck records (369850ad1) till 11:50Z; owner asked for proofs-arch's serve session
CHECKPOINT 7b7d04e8 (10:03Z) [open] 3:04 AM PDT: Q_word v2 opened as #667 (draft) for proofs-qword; #642 in T1, #654 in T654, #653+#638 next as C6; goal 2 hit 37.8 s (r20261001-092917-8b05); Q3c granted, verifier-c0-once-unreviewed dropping on 62 points; K=2048 step-12 collision handed to bf16-hill
# proofs-mufu: all six MUFU Boolean Definitions bit-exact against their words, circuit-check green

Branch `cursor/proofs-mufu-bool-95d4`, head `3bf1b6d02` (pushed), on the IR's `46c768b2c`. The worker's checkpoint is in the
message of commit `6ae4828f5`. Its full report is in its own VM's store as `internal/20261001T0830Z-report-from-proofs-mufu-boolean-mufu.md`,
which isn't visible from proofs' VM; this note restates it.

| Id | Word view | AND | XOR | NOT | Descriptor bytes |
|---|---|---|---|---|---|
| `MufuEx2Ftz_v2` | `MufuEx2Ftz_v1` | 1073 | 4546 | 98 | 176,088 |
| `MufuRcpFtz_v2` | `MufuRcpFtz_v1` | 902 | 4810 | 101 | 166,098 |
| `MufuSqrtFtz_v2` | `MufuSqrtFtz_v1` | 879 | 4840 | 110 | 168,591 |
| `RsqrtApprox_v2` | `RsqrtApprox_v1` | 1134 | 5269 | 163 | 198,080 |
| `DivFullRcp_v2` | `DivFullRcp_v1` | 1152 | 5172 | 144 | 189,907 |
| `DivFullScaleA_v3` | `DivFullScaleA_v1` | 531 | 860 | 94 | 47,035 |

**How the tables are built.**
- Each table is the hardware's own quadratic interpolator, `y = base + ((C0[g] + C1[g]·u + (C2[g]·Q(u)) << s) >> t)`. Only rsq
  needs an override, at index 0 (+1).
- The coefficients are in `tables/mufu_quadratic.json` (19 KB). They are written in ±1 digits, so they cost no ANDs.
- It is pure AND/XOR/NOT, with no ROM or lookup gate (Daniel, 11:11 PM PDT).
- Each table read was checked against every index (2^23 or 2^24) with 0 mismatches. The reads cost 693–776 ANDs, about a third
  fewer than a minterm decode.

**Checks.**
- `circuit-check` on all six: ok, with 0 failures and 0 warnings. The lowering compares on 66 vectors, the AND pins match, and
  the word view compares on 1,024 vectors. `DivFullScaleA_v3` doesn't read b's sign, and neither does the operation.
- Exhaustive against the word primitives, with 0 mismatches:
  - rcp, ex2 and DivFullRcp over [1, 2);
  - sqrt and rsq over [1, 4);
  - the subnormals and top binades of DivFullRcp and RsqrtApprox;
  - DivFullScaleA over 1.08G words;
  - ex2 over exponents 100–136, both signs.
- `test_boolean_mufu.py`: 35 passed.
- `suites.py`: 21 of 22 passed. In verity-vllm, `test_the_stored_tp2_moe_builds_merge_with_every_peer_bound[qwen3-30b-a3b…]` was
  OOM-killed (8 GB resident on a 15 GiB, 4-core VM, beside three other workers). It passes alone at the same head, and vLLM
  doesn't import the MUFU module.
- Not run: `check`, which needs a pod.

**Landing.** No proofs PR. circuits-bool-switch integrates this branch into circuits' integration PR (told in `lanes/circuits/`).
