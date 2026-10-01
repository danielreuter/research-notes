---
id: 20261001T0205Z-handoff-from-bc-8412d697-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-8412d697 (approved-weights lane)
---

_Relayed verbatim from the Cursor store by old-accounting (bc-b729c175): the author's VM gets a 403 pushing to research-notes._

# Migration handoff from bc-8412d697, the approved-weights lane (7:05 PM PDT, 30 Sep)

To compute-accounting (bc-e90634dd), and my replacement; cc old-accounting (bc-b729c175).

**The lane in one line.** It designed and measured rung 3, the keyed 8-block rotation for registered weights, which Daniel adopted at 1:36 PM PDT for FP8 v1 and v2, with Pearl-C4 to follow once #580 lands. The report is the old store's `docs/pouw/approved-weights.md`. Nothing of the lane is goal-critical tonight.

## 1. Branches and PRs

- **`cursor/approved-weights-gpu-cc03`** (danielreuter/verity), head **`7225704b`**, on origin, clean, 44 commits over the `main` it forked from.
  - **No PR**: the old coordinator's instruction at 1:32 AM PDT was "no PR yet". No recorded `check` either.
  - **It holds research code only,** in `benchmarks/pouw/approved_weights/`:
    - the 70B and 7B harnesses (`aw_scale.py`, `aw_fold.py`, `aw_gpu.py`);
    - the census and registration checks (`aw_census.py`, `aw_zero_cover.py`);
    - item 4 (`aw_advdebit.py`) and the relation attack (`relation_attack.py`);
    - the fork-operand converter (`aw_fork_capture.py`);
    - the fill-queue tools (`submit_job.sh`, `repoint.sh`, `release_held.sh`);
    - one test, `benchmarks/pouw/tests/test_approved_weights_dups.py`, which needs the `torch-cpu` extra.
  - **What's left:** nothing goal-critical. If the code should land, open a PR, rebase on current `main`, and record `check`.
- **No other PRs of mine.** The production side of rung 3 (the registration checks and the V/O rule) is in other lanes' PRs, such as #580 (bc-71c6ab78).

## 2. Runs and jobs in flight

There are four CPU fill jobs on node 2 (`gpus=0`), still queued in the shared CPU queue. None is goal-critical; the backlog's row "approved-weights debits" marks it Daniel's call.

| Fill job | Output dir on node 2 | Progress | Ends |
|---|---|---|---|
| `aw-advdebit-a-0e4b2442.sh` | `/workspace/pouw/approved-weights/aw-advdebit-a-0e4b2442/out/` | 7 of 9 cells at k = 16,384 | about 10–15 CPU-minutes per cell, so 1–2 h at the queue's pace |
| `aw-advdebit-b-0e4b2442.sh` | `…/aw-advdebit-b-0e4b2442/out/` | 6 of 9 | the same |
| `aw-advdebit-c-0e4b2442.sh` | `…/aw-advdebit-c-0e4b2442/out/` | 6 of 9 | the same |
| `aw-debit7bfold-bbb9521d.sh` | `…/aw-debit7bfold-bbb9521d/out/` | 5 of 6 chunks | one more chunk, about 10 min |

- **They have no collector any more.** Their research runs (`r20260930-093222-d933`, `-093230-5fc1`, `-093237-12be`, `r20260930-105111-3b9c`) ended at their 12-hour stage timeout, before the jobs finished (STAGE_TIMEOUT, cancelled).
  - They had custody, but it covers only the run dirs, which never received the outputs. **So the outputs need preserving by hand,** once each job reaches node 2's `fill/done/`.
  - **To collect one,** re-run its submitter under the same job name, from the tree the name carries. `submit_job.sh` sees the job in `done/`, copies its out dir into the new run, and writes `result.json`:
    - `research run --on vy-nebius-2 --project verity --campaign pouw --source <a checkout at 0e4b2442> --timeout 3600 -- bash /workspace/research/src/0e4b2442d684ae547cd233285b9f2cd3051a156c/benchmarks/pouw/approved_weights/submit_job.sh advdebit-a 0 -- aw_advdebit.py --group a --max-seconds 300`, and the same for `b` and `c`;
    - for the debit: `… --source <a checkout at bbb9521d> … submit_job.sh debit7bfold 0 -- aw_debit.py --modes plain,rot,rot-fold,rotx --split-channels 458,2570,2718 --layer-stride 4 --max-seconds 300`.
  - **Or, if Daniel drops them,** move the four scripts from `/workspace/pouw/fill/queue/` to `/workspace/pouw/fill/withdrawn/`. Delete nothing.
- **Nothing else is in flight.**
  - Every GPU job of mine is done, published and copied to the store.
  - The optional change-probability job (`aw-change-prob-7225704b`) was withdrawn at 11:43 AM PDT, and its run cancelled.

## 3. Half-done state, and where everything is

**The old store** (`/cursor/stores/bc-b729c175-…`):
- **`docs/pouw/approved-weights.md`: the report.**
  - §4 is rung 3's adopted specification. §8 holds every measurement: §8a–8h scale, §8i the fork's debit and the registration zero-structure check, §8j the 8-block rotation, §8k the V/O candidate.
  - bc-6289d8b0 marks the V/O rotation plus head interleave adopted in it; I've made no edit there.
- **`internal/pouw/approved-weights-rows.md`: the assumption rows.**
  - FP8 `tt-out-aw` rows adopted; Pearl-C4's pending #580.
  - bc-69c09d42 copies them into `docs/pouw/assumptions.md`.
- **`internal/pouw/approved-weights/`:** the early scripts and outputs, and `scale/` with every scale run's outputs in subfolders:
  - `llama70b`, `census`, `census-blocks`, `item4`, `relation8k`, `relation8k-blocks`;
  - `debit7b`, `act7b*`, `folding`;
  - `nvfp4-scale-flatness`, `zero-cover`;
  - `vm-checks/`, this VM's small check and table scripts, copied today.
- **`internal/pouw/rtx-pro/workers/approved-weights.md`:** my status file and the node-2 lease log.
- **`internal/pouw/cheap-binding/pearlc4-fix/fork-7b/`:** bc-a8466279's fork-variant run on the fork operands, run by me.

**Node 2** (`/workspace/pouw/approved-weights/`, 5.1 GB). Keep these:
- `aw-fold-fix-fp8-899a48fa/out/calibration.json`: Qwen2.5-7B's massive channels (458, 2570, 2718) and its channel-magnitude profile.
- `aw-70b-rotb-fp8-d9fd73f7/out/split_channels.json`: Llama-3.1-70B's.
  - Every later job reads these two to build the same 8-block rotation.
- `fork-weights/Qwen--Qwen2.5-7B.npz` (+ `.json`): the fork's noiseless rotated operands, in `fp4_v3_real.py`'s cache format. bc-a8466279's and bc-6289d8b0's fork-variant checks read them.
- `pc4fix-run/`: bc-a8466279's scripts as staged, with their output.
- `held/hold.log`, `repoint-hold/`: empty now; history only.
- The `aw-*/out/` job dirs: every run's checkpoints and results, already copied to the store.

**This VM only:** nothing a successor needs.
- The branch is on origin. The report and outputs are in the store.
- `/tmp/aw` has working copies of the published files.

## 4. The next step for each kept item, and what I'd stop

- **The approved-weights debits** (the backlog's "Daniel decides"):
  - If kept, let them finish (CPU only, no GPU), collect them as in section 2, and fold them into `approved-weights.md`: §8c for item 4 at k = 16,384, which adds Haar cells for every family, and §8f for the real-activation debit with γ folded and the split rotation.
  - If dropped, withdraw them. Neither changes a headline; k = 8,192 and the assessor's runs already carry the claims.
- **Rung 3 for FP8 (adopted).** The next step is implementation, not this lane's:
  - The registration tool derives the deployed codes as `approved-weights.md` §4 specifies: γ folded per block, 8 keyed Haar blocks by calibrated activation magnitude, the massive channels off the chain, and round to nearest.
  - The verifier runs checks (a), (b) and (d). They compare codes regardless of scale bytes; (b) uses the best layout within each 16-block (§8i); max/RMS ≤ 16 is checked on credited rows. The reference implementations are `aw_census.py` and `aw_zero_cover.py`.
- **Pearl-C4 (pending #580).** When #580 merges, the report's status and Pearl-C4's rows move to adopted. With them goes the V/O rotation plus head interleave, inside the 8-block rotation only (Daniel, 5:52 PM PDT). bc-6289d8b0 owns those edits.
- **The V/O rotation's node-2 quality evals** are bc-6289d8b0's fill scripts. If Llama-3.1-70B shows a cost, the next job is glue recovery at lr 1e-4 in `aw_scale.py`, with the V/O fold and the interleave added (not written).
- **What I'd stop:**
  - the per-code change-probability check, since B-OVF covers the fork;
  - any more quality tests on the 0.5B and 1B stand-ins: rung 3 itself costs them several percent, which swamps anything a variant changes.

## 5. Traps

- **Store writes fail intermittently** with "Resource temporarily unavailable". Copy in a retry loop and compare afterwards.
- **Agent-VM git access.**
  - Pushes to danielreuter/verity sometimes fail authentication for a few minutes. Retry.
  - Pushes to research-notes get 403. Use `internal/pouw-fp8/accounting-outbox/`.
- **`research run --source` refuses a dirty tree.** Commit first. Edits made in the same batch of tool calls as the commit can miss it, so commit only after the edits land.
- **`submit_job.sh`'s collector run times out at its `--timeout`** (12 h here). CPU fill jobs can wait longer than that, as in section 2: give CPU jobs a longer timeout, or collect by hand.
- **The fill runner.**
  - Use `prio=10` and `max_min=8`, and keep chunks to about 7 minutes.
  - GPU 1 is kept free for its owner.
  - A 70B chunk spends 1–2 minutes rebuilding and re-projecting before it computes.
- **Keys depend on the device.** `aw_fold.block_rotation` draws its permutation from a torch generator on the device, so the same seed gives different rotations on CPU and CUDA.
  - The quality and census runs used CUDA keys. `aw_fork_capture.py` used the CPU's.
  - Any key is equally honest-typical, but don't mix two runs' keys in one comparison.
- **Recovery at 70B.** lr 1e-3 damages Llama-3.1-70B, which has memorized parts of WikiText-2; use lr 1e-4. Compare recovered with recovered: recovery also adapts to WikiText-2's domain.
- **Noise in comparisons.** One window of 1,024 tokens moves about 1% between two random rotations. Compare over the whole test split with paired per-window deltas.
- **The 2:4 rule's form.**
  - The census's 2:4 count in the codes' order (`aw_census.py`) undercounts what a prover can use. The registration check (b) must price the best layout within each 16-block (`aw_zero_cover.reading`).
  - On Qwen2.5-7B the code-order rule covers only 84% of the reading.
- **The massive channels' rows.** S's rows of o_proj and down_proj stay the registrant's own and unrotated (max/RMS up to 161). Exclude them from check (d). They are uncredited.
- **`aw_scale.py` needs about 74–77 GB** of one RTX PRO 6000 for Llama-3.1-70B. It runs on one GPU only.
