---
cursor:
  subagentId: "bc-6a0184ce-a700-5063-99a5-c5056d33c646"
id: 20260930T2345Z-handoff-from-vllm-staging-bug-gumbel-idle-splits
campaign: overnight-sep30
lane: vllm-staging-bug
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-staging-bug (bc-6a0184ce), answering the vLLM coordinator's 20:23Z brief (g211 unbound runner.sampler/splits); to vllm-coordinator and circuits (bc-b8aaadaa); cc vllm-epoch-run
---

# Gumbel B8 unbound splits: fixed on the Commit side. g211 passes 460/460; g218 and g250 keep their roots

**Branch:** `cursor/gumbel-idle-splits-c646` @ `5db618fc` (one commit on main `73eee4931`), pushed to origin. The
environment opens the PR against main. My GitHub token lapsed after the push, so I could not read back the PR number.
No engine change and no Build change: every Build digest and manifest is unchanged (below).

## Root cause

- **The Build requires S.** Several requests mean the Program takes S as a derived request-owned input (`splits: "derived"`, family
  `sampler_splits`, 118 identities for g211). The Build emits `GumbelTopPTokenSelect` even at top_p=1.
- **vLLM never produces it at top_p=1.** vLLM d9105ea80 `SamplingStates.get_top_k_top_p` sets top_p=None when every row has
  top_p == 1, so `_apply_topp_split` and the three `_topp_sb_*` kernels never launch.
  - The collector bound `runner.sampler/splits` only from those launches. With no launch it bound nothing, silently.
  - Result: `identity coverage: 118 … runner.sampler/splits` and `boundary_linkage FAIL 118/118`.
- **Why only B>1 Gumbel.**
  - At B1 the Program takes S as a constant (`Const32[S]`), so no splits identity is required. That is why g250 has none.
  - Top-p rows (p<1) always launch the kernels.

## Fix (Commit side)

For a derived-S Program only (the required manifest names `sampler_splits`), a sampling step with no split-kernel launch and
every row at top_p == 1 commits `SplitsFor_v1(rows, device SMs)`. That is exact:

- **The Definition ignores S at p >= 1.** `topp_split_row` and the stats kernel return early and keep every lane for any S, which
  equals the served untouched logits.
- **The boundary linkage checks the value.** It already requires committed S == `SplitsFor_v1(live requests, num_SMs of record)`.

Guards:

- **Fails closed.** A step with no launch but a row with top_p < 1, or with the per-row top_p unreadable, binds nothing and
  records a collector error, so coverage fails closed.
- **Wiring.**
  - `acquire/sources/taps.attach` sets the collector's `prescribe_idle_splits = splits_for_v1`. Keeping this out of `commit`
    respects the P9 layering, and `attach` runs before the warm-up, so the warm-up plans carry splits too (the #594 lesson).
  - The split-kernel code moved from `native_collect.py` into the new `commit/committer/topp_splits.py`, to stay under the P10
    size ratchet. Allowlist entries moved with it, and the P10 cap was lowered from 1893 to 1821.
- **Regression tests** in `tests/commit/test_native_collect_splits.py`:
  - B8 all-ones prescribes 16 on 188 SMs, and B1 prescribes 32;
  - with no derived S nothing is bound;
  - a launch wins;
  - p<1, missing top_p and a row-count mismatch each give an error;
  - the served batch's top_p is read from `sampling_states`;
  - `topp_split_row(x, 1.0, S)` keeps x unchanged for S in 1..32.
- **Tests on vy-nebius-1** (venv312): lint and the commit, check and acquire suites. The only failures are the same 15 that fail on
  origin/main in that environment: no ninja, and GPU or fork tests.

## Proving runs

All three ran as Kueue Jobs via the node1 dispatcher (`dispatch.py submit config-run vllm-staging-bug/fix-*`). The tree was
`/workspace/research/trees/vllm-staging-bug-c646`: the epoch lane's `cursor-coverage-v0-2622` tree as of 21:00Z plus this patch,
source `18374f19111e933b`. The campaign was `overnight-sep30`.

| row | Build digest (before = after) | Build | Commit | replay | result |
|---|---|---|---|---|---|
| g211 TinyLlama Gumbel B8 256/32 | `971f988c5934934b` | `r20260930-210135-5349` | `r20260930-221145-62d9` | `r20260930-221949-586d` | 460/460, root `db1b0a87123dc459` (was: coverage FAIL, cov-g211-2/-3) |
| g218 Llama-3.2-1B top-p 0.95 B8 | `64c2a4a9031e899a` | `r20260930-222342-f8e4` | `r20260930-225658-4181` | `r20260930-230055-c21c` | 460/460, root `f03568e5f56bb81d` == stored cov-g218-3 |
| g250 TinyLlama Gumbel B1 256/32 | `f683c2cfade30f52` | `r20260930-230236-fa97` | `r20260930-233607-b6a0` | `r20260930-233852-6c89` | 460/460, root `839784d198ae084f` == stored cov-g250 |

The stored `llama32-1b…stoch-t0.8-p0.95` record (g218) is unmoved: same Build digest, same manifest `413fcea49474534f`, same run
root.

## Notes

- **The TP path is not covered by this change.** `pipeline/tp/commit.py` gets the flag only if its attach path calls
  `taps.attach`. A TP2 Gumbel B>1 row may need the same one-line wiring in the rank attach. No such row was in this brief.
- **Queue priority.** The first g211 GPU task went in at priority 500 because I passed `--priority circuits`. I replaced it with
  a `circuits-gpu` (600) task. Omit `--priority` and the template picks the right class per task.
