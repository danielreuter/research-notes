---
id: 20261001T0057Z-handoff-from-old-circuits-and-proofs-merge-request-gemma2-six
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-ecac3029)
---
# Merge request: the six Gemma-2 Commit fixes (lane vllm-coverage-defs, bc-ea0126bf), all granted

| PR | Head | Fix |
|---|---|---|
| #623 | bb3dfa021 | the acquire plan body is linear (m007 committer_setup hang) |
| #620 | 2f22290b3 | the Gemm_v2 float64 k16 chain for any DOT (m005 warm-up stall) |
| #619 | 737a47409 | warm-up requests map to workload rows (m006 staging overrun) |
| #624 | 5c13a4e2f | X-03 checks call boundaries per step (k06) |
| #622 | a7a963c81 | the replay reads f64 statics; one-output members |
| #621 | cb341f707 | the replay addresses ATen norm scales and reconciles them against Q(P) |

- **Merge:** each merges cleanly with `git merge-tree` on main as of 00:56Z. #622 and #621 add a test at the same spot in test_dense_replay_rows.py; the second to land keeps both. Integration-only, no engine change, a regression test in each.
- **Evidence:** k06 r20261001-003049-5383 and m006 r20261001-003125-0ccd pass 460/460. A Llama-3.2-1B B1 control on main (r20261001-004114-a2cb) and on main plus the six (r20261001-003650-983b) has the same manifest digest, Programs and run root 76e207d8….
- **Review:** I read #620's float64 chain, which falls back to the step's int64 twin on any non-finite, subnormal or overflowing coordinate, and #621's coverage change, which makes ATen norm scales required rows, a stricter check. Both are sound.
- **Do not merge:** `cursor/gemma2-commit-proof-987d` is the proving tree only.
