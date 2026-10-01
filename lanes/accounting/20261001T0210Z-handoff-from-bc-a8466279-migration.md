---
id: 20261001T0210Z-handoff-from-bc-a8466279-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-a8466279
---

_Relayed verbatim from the Cursor store by old-accounting (bc-b729c175): the author's VM gets a 403 pushing to research-notes._

# Migration handoff from bc-a8466279, the Pearl-C4 (NVFP4 on sm_120) theory and domain lane

Replying to `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. Written at 7:10 PM PDT. I'm starting no new work.

"The store" below means the Cursor store `/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/`.

## 1. Branches and PRs

All three are open drafts, stacked in this order, and green on their suites. Merging is Daniel's decision, through the merge train.

| PR | Branch | Head | State |
|---|---|---|---|
| #534 | `cursor/pearl-c4-salt-keyed-b-2cf6` (base `cursor/pearl-c-fp4-3084`, #548) | `b466fd9ef` | green; D-SK, the low-7-bit scale decode, D-NF 0x08–0x7E |
| #556 | `cursor/pearl-c4-f1prime-f2-2cf6` (base #534) | `9363e5012` | green; the assessor's GO under its FP4 conditions |
| #602 | `cursor/pearl-c-beacon-quicknet-2cf6` (base #556) | `8a322b297` | green; `beacon-unpredictability` rated A; **on hold** |

- **#534:** 242 pouw tests and 57 benchmark tests pass.
- **#556:** F1′, F2 with c_L pinned, R1, item 3 per element, item 4 on the witness, B-OVF with n ≥ 128, and V-EX. The `verity-pouw` and `verity-pouw-benchmarks` suites pass. GPU 5's #580 takes #556 whole at this head.
- **#602:** the drand quicknet beacon, verified in pure stdlib. 286 pouw tests and 62 benchmark tests pass, and the vLLM `test_pouw.py` passes.

**What's left:**
- **The #602 hold:** compute-accounting's 6:49 PM PDT order holds #534, #556 and #602 until accounting-merge (bc-2a5f14cf) posts #602's tip with #572 at `9288c339` merged in.
- **That merge needs five fixes beyond its three text conflicts:** see `20261001T0200Z-reply-from-bc-a8466279-hold-602-merge-fixes`.
  - The store's `internal/pouw/cheap-binding/pearlc4-fix/merge-572-into-602-fixes.py` applies all of them.
  - Its result matched my tested trial tree file for file: 304 pouw, 166 benchmark and 111 vLLM `protocol_options` tests pass.
- **Then the merge train:** #449, #548, #534, #556 and #602 together.
- **`check --record`:** not run from this VM, which has no `research run`. The stack check `r20261001-002356-2595` is the research coordinator's.

## 2. Runs and jobs in flight

I have no research runs. Two node-2 CPU fill jobs are mine. bc-2aa33ad8 queues them, and I can't see node 2 from this VM. Neither job has custody (`--custody-r2`), so both need their outputs preserved by hand with `research data put`.

- **`pearlc4-bovf-strong-search.sh`:**
  - Annealing plus exact block optimisation at n = 256 and 512 over B-OVF's families: about 8 CPU-h, self-contained (gcc and numpy).
  - Output: `/workspace/pouw/pearlc4-cpu-fill/bovf-strong-search/`.
  - The backlog lists it as queued since 3:22 PM PDT.
- **`pearlc4-vex-coverage.sh`:**
  - V-EX's coverage on the Qwen2.5-3B and 7B captures: about 4 CPU-h, needing `TREE` (#556) and `CAPTURES`.
  - Output: `/workspace/pouw/pearlc4-cpu-fill/vex-coverage/<capture>/`.
  - The backlog lists it as running since 4:44 PM PDT, with 112 tile results on 3B. Started then, it should end around 8:45 PM PDT; fill leases (exit 99, rerun) stretch that.
- **Both are clear of the MKL race:**
  - V-EX coverage imports no torch.
  - The B-OVF script's only torch import is under `dnc2.py`'s `__main__`, which the job never runs, since it imports only `window_saving`. It also sets `OMP_NUM_THREADS=1`.

  This closes the backlog's MKL-race row for my two jobs.

## 3. Half-done state

**In the store** (all mine unless noted):
- `internal/pouw/rtx-pro/theory-pearl-c4-domain.md`: the domain and theory document, §1 through §6.13.
- `internal/pouw/cheap-binding/pearlc4-fix/`:
  - the B-OVF evidence: `strong_search.{c,py}`, `strong_analysis.py`, `beta_table.py`, `bucket_cost.py`, `strong*.jsonl`, `exact256.*` and `exact_starts.*`;
  - 10×'s honest cost: `btilde_honest_shards.py` and the honest7b/72b logs;
  - c_L: `c_L_table.py`, `c_L_module.py` and `c_L_table.json`;
  - `gpu5-verifier-handoff.md`, for GPU 5's port;
  - `merge-572-into-602-fixes.py`.
- `internal/pouw/rtx-pro/cpu-fill/pearlc4-bovf-strong-search.sh` and `pearlc4-vex-coverage.sh`.
- `internal/pouw/rtx-pro/pearl-c4-btilde-overfit-rating-request.md`.
- `internal/pouw/fp4-forming-lean/README.md`.
- **Copied from this VM at 7:10 PM PDT:** `internal/pouw/cheap-binding/pearlc4-fix/vm-scratch-a8466279/`, 26 entries, 821 KB. They are probes, smoke tests of the fill jobs, `all.jsonl` (the strong search's raw draws), `cat.py` (an early catalogue check) and copies of old repo files. Nothing in it is needed to continue.

**Only on this VM, none of it needed:**
- `/tmp/pr534`, `/tmp/seedb` and `/tmp/pr602`: the PR worktrees, clean and pushed.
- `/tmp/trial602`: the uncommitted trial merge, which the script above reproduces.
- `/tmp/pc4` and `/tmp/emu`: read-only copies of other lanes' trees.

## 4. The next step for each kept item

- **#534, #556 and #602:**
  - When accounting-merge posts #602's tip, check that it has the five fixes, and rerun the three suites with the tree's own packages first on `PYTHONPATH`.
  - Then send the stack to the merge train. No code change is owed.
- **The small-width FP4 grant:** for widths 128 ≤ n < 4,096 it waits on B-OVF's table being carried in the statement's credit, Lean side and #580. That is GPU 5 and the Lean lanes' work, not this lane's. B-OVF itself is #556's `a097a30e`.
- **The B-OVF strong search:** preserve its output. Then check that annealing plus exact optimisation stays within the measured β table, β = 2.00% at 256 and 1.11% at 512, with the 1.5× margin (`beta_table.py --mu 1.5`).
  - If it exceeds the table, β must rise, which re-opens the grant (its re-grant clause).
  - The earlier sample already had exact within 1.014× of annealing (`exact256.jsonl`).
- **V-EX coverage:** preserve its output, then report how many voluntary rows an honest prover needs on 3B and 7B. bc-f5bf55c8's census says 0.
- **The rotated-weights re-read** (waiting on an order): re-read two figures on keyed-V/O-rotated weights, on CPU with the V-EX coverage script: 10×'s honest cost (0.088% of rows on 7B, 0.078% on 72B) and V-EX's 0 voluntary rows. Do it only if a rotated registered checkpoint is going to cite them.
- **The "layout-after-salt break" row:** I read it as the B̃-side shared-layout overfit (§6.12b): worth up to +1.06 points net at n = 128, rated D for 10× alone at 11:45 AM PDT (ratings.md 18:45Z).
  - B-OVF (rated B) answers it. Its open parts are the strong-search job above and GPU 5's port. Nothing else is running on it.
  - If the assessor meant a newer finding, ask bc-d7d4b0d1. ratings.md has no entry under that name.
- **What I'd stop:** none of my work is speculative. I'd leave MXFP4 alone (contrast only, by Daniel's 8:34 AM PDT ruling).

## 5. Traps

- **The beacon API change** (#602), which git won't flag on a merge:
  - `Epoch.start` takes a verified quicknet `Round` and `recorded_at`. Bare bytes are `Epoch.unverified`, with the same salt.
  - `pearl_c_work.audit` takes `recorded_at` and a verified round. The old form is `audit_replay`.
  - Any branch merged into #602's stack that calls the old forms fails at runtime, not at the merge.
- **`PearlC4` has neither `device` nor `forming`.** Shared `pearl_c_work` code must read them with `getattr`, or every Pearl-C4 audit raises `AttributeError`.
- **#572 changed `_pearl_c`'s second positional argument to `device`**, so the hashing variant must be passed as `hashing=`.
- **Measured constants need the assessor:** the β table, `F1_B_OVERFIT = 10`, `B_OVF_MIN_N = 128`, the c_L table and `F1_EPS` / `R1_TOLERANCE` are pinned. The 6:36 PM PDT grant names each in its re-grant clause, so changing any of them needs a new rating.
- **D-NF's bytes:** the grant's text writes D-NF as `8 ≤ e4m3(β) < 128`. The code and Lean accept bytes 0x08–0x7E: a NaN β casts to 0x7F, and refusing it was bc-22298e90's nit. Don't "fix" the code to `< 0x80`.
- **The production pinned vector's unit is 64 × 1024 × 128**, because n ≥ 128. Test schemes use `n_min=16`.
- **Running suites by hand:**
  - Put the tree's own packages first on `PYTHONPATH`, per command. A stray `PYTHONPATH` once tested another PR's code.
  - `/tmp/seedb/.venv` has no torch; `/usr/bin/python3` has torch 2.14 CPU.
  - The vLLM tests need `protocols/pous` and `protocols/sampled_proofs` on the path, or about 20 fail on imports.
  - `suites.py` reports cache hits when a suite's inputs are unchanged. That is a pass, not a skip.
- **The store:** writes race, and edits by two tools to one file have reverted each other. Re-read after writing. `server.md` is rewritten by others, and a line of mine there was lost.
- **research-notes:** Cursor VMs get a 403 on push, and the Verity broker only serves `danielreuter/verity`. Use the outbox.
- **`Fp4FormingCode.lean`** was bc-ae19a858's to rebase. Check that rebase has landed before editing it.
