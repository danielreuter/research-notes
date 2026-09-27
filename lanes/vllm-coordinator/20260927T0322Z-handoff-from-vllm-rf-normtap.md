---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-normtap (agent bc-12c2f2d9)
created: 2026-09-27T03:22Z
---
# Merge-ready: FA3's per-iteration `Check_inf` as `Attention_v4`, opt-in, PR #105 (`cursor/vllm-rf-fa3-checkinf-57d5` @ `b0a12771`)

Re `20260927T0200Z-handoff-from-vllm-coordinator.md` (option 1) and the H100 pre-approval. [PR #105](https://github.com/danielreuter/verity/pull/105)
is a draft stacked on #102: base `cursor/vllm-rf-ms-plane-57d5` @ `64a4c3d3`. Merge #102 first, then #105, which retargets to main. All pods are
terminated.

## What it adds (opt-in: `TargetProfile.fa3_construction = "check-inf-per-iteration"`; default `guard-every-block` = `Attention_v2`)
- **`registry/fa3_check_inf.py`**, new versions, so `*_v2` stays the record.
  - `AttnBlock_v4{D, NVIS, FIRST, BN, DOT, CHECK}`. With `CHECK` false the block reads the unguarded running max for both the rescale and
    `max * scale`, as FA3's `fwd_step(..., check_inf=false)` / `max_get_scale` / `scale_apply_exp2` do. `FIRST` requires `CHECK`.
  - `AttentionHead_v4` / `Attention_v4{..., MASKED_FROM}`: block b runs `CHECK = b >= MASKED_FROM`.
  - `MASKED_FROM` is the kernel's `n_block_min_causal_local_mask` for the row's tile (pinned mainloop, lines 1285-1293):
    `(m_idx_min + seqlen_k - seqlen_q) / kBlockN`, with PackGQA's `m_idx_min = m_block * kBlockM / g`.
  - A group size that does not divide kBlockM is refused.
- **A derived static, not a new input.** `targets.attention_spec(..., row=)` computes it from the geometry that already picks `BN` / `FIRST`
  / `NVIS`: the launch's `max_seqlen_q` picks the tile (`fa3_tile_m`, `fa3_kblock_n`), plus the row's index among its request's query rows.
  - The Bet A builder passes `i` on the prefill and 0 on decode.
  - The Match fold groups rows by (T, row) under the selector, and by T as before otherwise.
- **Also updated:**
  - the row evaluator and self-check targets (`kernels/rows.py`);
  - the numpy twin (`derived_rows`, line-neutral);
  - `FLASH_ATTENTION_LAUNCHES` and the replay family sets;
  - the query registry list, with `hopper` importing the module so every Hopper decode path knows v4;
  - `guarded_max.attention_words`: an unguarded block commits its running max (ROW word 0), not a guard.
- **The switch to the record** waits for the re-baseline epoch, and root decides when. Flipping `DEFAULT_FA3_CONSTRUCTION` or declaring the
  field moves the H100 rows' (#73, #74) Programs, manifests and roots; FA2 rows don't move.

## Acceptance
| check | run | result |
|---|---|---|
| nothing of record moves with the selector off | `r20260927-025023-e706` (CPU) | head = base on 7/7 records (`registry_version`, the builder vocabulary's version, 4 target profiles' digests / records / `describe`); 1,248 attention bindings, hash `a4ee0ae0…` on both |
| partition checker on `Attention_v4` | `e706` | 20 FA3 geometries (hd 64/128, decode + 287-row prefill tiles): 0 violations, **0 recomputes**, units <= 32 bits; guard / `max_scaled` counts = formulas; 3 `AttentionHead_v4` cuts ok, 0 recomputed gates |
| CPU tests, lints | `e706` | rc 0 / rc 0 |
| gate (b) base `40ec2e13` / head `ac76ac43` | `r20260927-025031-cb9e` / `r20260927-025051-52f5` | jdiff rc 0: 0 new failures, 0 new skips, +16 tests pass (the CPU pod's 49 environment failures on both sides) |
| **FA3 exactness under the new construction, H100** | `r20260927-025855-18e5` | default `cddc93cf…` OK 20/20; guarded `e8dfd09d…` **OK: 20/20 cases, 10/10 negatives** |

**On the H100:**
- **MS words:** all 62,050 equal `AttnBlock_v4`'s value, 33,628 of them at unguarded blocks. `edge_rows` passes at both head dims; its 16 + 24
  unguarded words are the ones that failed #102's record.
- **Outputs:** every output row equals `Attention_v4` on the launch's inputs. That is 7,504 rows and 21,928 heads, 0 mismatches. The
  reference evaluator covered the 56 non-finite edge-row heads, and none were left unevaluated.
- **The rest** passes as in #102: ROW word 3, the six classes equal to the default build's, closedness, and out/lse equal to the installed kernel.
- Environment: torch 2.13.0+cu129, vLLM 0.28.1rc1.dev472+gd9105ea80, Triton 3.7.1, driver 570.

## History
- `c19bae0d` is the IR and selector, `ac76ac43` the property (g).
- `b0a12771` merges #102's new head `64a4c3d3` (with main `3040ac1f`) cleanly; the CPU part ran on `ac76ac43`.
- The H100 exactness ran on `ac76ac43`, and #102's merge touched none of the tap sources or the IR since then.

## Pods, spend
- The CPU pod `vyv-rf-normtap-c1` ran 02:48Z-03:15:08Z (~$0.43). The H100 `vyv-rf-normtap-h3` ran 02:58Z-03:16:30Z (~$1.08).
- The follow-up cost about $1.5 in total. With #102 that is about $3.8 of the $10 cap.

Evidence: `lanes/vllm-rf-normtap/evidence/fa3-check-inf/` (`record_digests_*.json`, `partition_v4.json`, jdiff, `h100/`); pod scripts
`cpu_bootstrap.sh`, `f3_check.sh`, `f3_exact.sh`. The #102 re-merge is `20260927T0318Z-handoff-from-vllm-rf-normtap.md`.
