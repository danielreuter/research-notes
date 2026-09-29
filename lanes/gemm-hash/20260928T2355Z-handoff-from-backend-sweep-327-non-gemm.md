---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
id: 20260928T2355Z-handoff-from-backend-sweep-327-non-gemm
campaign: backend-sweep
lane: gemm-hash
kind: handoff
status: final
repo: verity
origin: backend-sweep (bc-ea1c2c4f), via verity-root
---

# #101's non-GEMM shapes on #327: the top 8 fell 4.9×, and #101 on the L40S is 2.16 × 10⁷ × native

For `docs/gemm-hash-cost-plan.md`, row 3 ("Re-prove #101's non-GEMM shapes on #327"). Daniel approved the top-8 option.

**Headline:** #101 on the L40S is **1.83 × 10⁵ GPU-seconds, 2.16 × 10⁷ × native** (0.00848 s native), down from 3.4 × 10⁷:
- GEMM: 1.465 × 10⁵ s (79.9%), from #327 at m = 34, `r20260928-213503-2861`;
- the 8 re-proved shapes: 2.71 × 10⁴ s (14.8%);
- **the other 839 non-GEMM shapes: 9.67 × 10³ s (5.3%), carried over from the pre-#327 sweep** (prover #192), not re-proved.

The carried share probably overstates: at the top 8's 4.9×, the row would be 2.1 × 10⁷. After this, GEMM is 80% of #101.

## Per shape

The prover is #327 `b87e2651`, with #212's harness (`adee9024`). The pod was one 1× L40S (`5h2r6b37aplfl3`).
- **Sessions:** one warm and three timed; median shown.
- **Batch:** #101's own statement sizes (B = 1,024, m = 30–31).
- **Time on this shape** = #101's row units ÷ B × median prove.

| Shape (#101 digest) | m | Median prove, #101 → #327 | Device per rep, rep 0 / rep 1 | Host per rep | Time on this shape, #101 → #327 | Proof per rep | Verify |
|---|---:|---:|---:|---:|---:|---:|---:|
| `AttentionHead_v3` T = 2, with table reads (`191fb6e5…`) | 30 | 3.312 → 0.427 s | 0.389 / 0.032 | 3–4 ms | 68,424 → 8,824 s | 740,034 B | 0.59 s |
| `SiluMulBf16_v1` (`78199905…`) | 30 | 0.500 → 0.128 s | 0.092 / 0.031 | 2–3 ms | 18,364 → 4,717 s | 740,034 B | 0.47 s |
| `RMSNormFusedCuda_v2` (`b044e943…`) | 31 | 0.839 → 0.197 s | 0.145 / 0.047 | 2 ms | 15,418 → 3,609 s | 803,082 B | 0.44 s |
| `AttentionHead_v3` T = 2, table-free (`7957925c…` → `1a7a9853…`, below) | 30 | 0.444 → 0.142 s | 0.107 / 0.031 | 2 ms | 9,173 → 2,928 s | 740,034 B | 0.47 s |
| `RMSNormFusedCuda_v2` (`e66c4b79…`) | 30 | 0.409 → 0.135 s | 0.097 / 0.032 | 3 ms | 7,505 → 2,480 s | 740,034 B | 0.49 s |
| `AttentionHead_v3` T = 1 (`40e34040…`) | 30 | 0.295 → 0.112 s | 0.078 / 0.030 | 1–3 ms | 6,104 → 2,319 s | 735,906 B | 0.48 s |
| `RopeOutAdd_v1` (`a5eb3fa1…`) | 31 | 0.728 → 0.197 s | 0.135 / 0.057 | 2–3 ms | 4,177 → 1,134 s | 807,210 B | 0.54 s |
| `RopeOut_v1` (`9254fd7a…`) | 31 | 0.656 → 0.198 s | 0.144 / 0.050 | 1–2 ms | 3,768 → 1,135 s | 807,210 B | 0.55 s |
| **Total** | | | | | **1.329 × 10⁵ → 2.715 × 10⁴ s (4.9×)** | | |

- **Rep 1 reuses rep 0** (`rep_reused [false, true]`) on all eight at these sizes on the L40S. That's most of the gain, together with #327's host time of about 3 ms.
- **The successor shape:** on #327's tree (`main` `ac412eb8`), #101's table-free T = 2 attention circuit `7957925c…` is cut as `1a7a9853…`. It has the same role, 320 units per Call and 5 word gates. It was proved against #101's row units for `7957925c…`.
  - The other 7 digests are unchanged.
  - One lighter attention shape, `f49b4582…`, also moved (to `12802732…`). It's among the carried 839.

## Byte identity

`r20260928-222616-c761` (B = 16) on `SiluMulBf16_v1` and the table-read attention shape `191fb6e5…`. Both are accepted, both GPU cases pass, and `all_pass` is true.
- `gpu_paths_agree`: proofs and transcripts equal, `host_units [true, true]`, `rep_reused [false, true]`;
- `gpu_proofs_match_cpu`: proofs and transcripts equal.

## Runs and spend

- **The runs,** all preserved and labelled `for_pr=327`, `row=101`:
  - `r20260928-221825-3558`: all 8, at the sweep's basis (`SELFTEST=25 SELFTEST_LARGEST=0`). Its RoPE selftest passes, 35/35.
  - `r20260928-222850-0dba`: the 5 attention and RoPE shapes again, with #101's Call counts (the attention Call × 16, RoPE × 4,592). The first run gave each Call a count of 1, so the batch planner capped B at 256 for these; those 5 rows of the first run are superseded.
  - `r20260928-222616-c761`: byte identity.
- **Spend:** $0.27 of the $0.60 cap (`vyb101n-` guard). The pod was terminated at 22:31:34Z.
