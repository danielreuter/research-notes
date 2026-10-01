---
id: 20261001T0201Z-handoff-from-bc-6289d8b0-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-6289d8b0, keyed transforms
---

_Relayed verbatim from the Cursor store by old-accounting (bc-b729c175): the author's VM gets a 403 pushing to research-notes._

# bc-6289d8b0 (keyed transforms): migration handoff. Nothing is in flight, nothing is unpreserved, and no branch or PR is mine

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. Times are PDT. "Store" means the old PoUS Project's
Cursor store: every path below is under `/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/`.

**1. Branches and PRs.** None. I opened no branch and no PR. My work changed rung 3's specification in two docs (below), and GPU 5
(bc-71c6ab78) carries it in code on #580 (`639128c8`, done but unmerged).

**2. Runs and jobs in flight.** None.
- All my node-2 fill jobs are done:
  - the eight `kt-e7b-*` and eight `kt-e70b-*` perplexity evals;
  - `kt-fork7b-voi` (job 3);
  - the two `kt-prep-*`.
- They were fill jobs, not research runs, so they have no `--custody-r2`. Their outputs were preserved by hand into the store, at `internal/pouw/keyed-transforms/out/node2/`:
  - `s7b/`: 8 variants × 146 windows;
  - `s70b/`: 8 × 141 windows, hash-checked by bc-2aa33ad8, with node 2's `summary.txt`. The broken unfolded `none_pc` groups are in `s70b/out-broken-unfolded/`;
  - `fork7b-voi-output.txt`.
- The originals stay on node 2 under `/workspace/pouw/keyed-transforms/` (`src/`, `s7b/`, `s70b/`, `fork7b-voi.npz`).
- Nothing runs on my VM.

**3. Half-done state.** Nothing exists only on my VM. My scripts and every result are in the store, apart from smoke tests and two regenerable `prep.npz` files.
- **The doc:** `docs/pouw/keyed-transforms.md`. It holds the shortlist, every measurement, the assessor's 17:25Z ratings with their conditions (§13), and the 7B and 70B results (§14).
  - The adoption is marked in it and in `docs/pouw/approved-weights.md` (§4 step 3 is the spec; §8k).
- **Scripts:** `internal/pouw/keyed-transforms/`.
  - `kt_coverage.py`: the transforms and the F1′ + F2 coverage.
  - `kt_stream_ppl.py`: the layer-major evaluator node 2 ran.
  - `kt_regcheck.py`, `kt_regtable.py`: the registration checks on deployed codes.
  - `kt_clause_b.py`, `kt_clause_c.py`: the clause tests.
  - `kt_quality.py`, `kt_fold_quality.py`, `kt_oproj_error.py`: the quality runs and proxy.
  - `kt_70b_diag.py`, `kt_70b_diverge.py`, `kt_70b_layer0.py`: the 70B cast-fault diagnosis.
  - `kt_fold_check.py`, `kt_fork7b_voi.py`.
- **Elsewhere in that folder:** the fill scripts in `fill/` (22), every CPU result in `out/` (JSON plus `logs/`), and my `status.md`.
- **Dependencies:**
  - `aw_gpu.py`, `aw_fold.py`, `aw_census.py` and `aw_zero_cover.py` from `internal/pouw/approved-weights/scale/` (bc-8412d697's);
  - `fp4_f1_pricing.py` at `6a6d1a24`, on branch `cursor/fp4-emulation-cf5b`, on origin.

**4. Next step for each kept item.**
- **The V/O + head-interleave rule** (backlog: done, unmerged): nothing from me. It lands with #580's merge (bc-71c6ab78). Its spec is `approved-weights.md` §4 step 3. The reference code is `kt_coverage.py`'s `Transforms.o_in` kind `voi` and `Transforms.v_rows` kind `vo`, plus `kt_regcheck.py` for the deployed codes.
- **"70B must fold γ"** (with bc-a8466279; done, unmerged): lands with #580. The evidence is `keyed-transforms.md` §14 and `kt_70b_layer0.py`: the fork's cast moves layer 0's update by 158% on an unfolded 70B, and by 0.8–3.5% with γ folded.
- **Rank 2, 16-aligned placement plus zero-fill dither** (clause (b) as a transform claim): it waits on Daniel ("time model and dither" in the backlog).
  - The assessor rated it B. It costs +0.02% ± 0.11 at 7B and +0.14% ± 0.19 at 70B, and saves about 0.11 point of Pearl-C4's γ at 7B.
  - If adopted, the registration spec gains the chunk-granular placement and the 2⁻¹⁶ dither (`keyed-transforms.md` §5, §13). The per-row FP32 scale is already pinned.
- **Stop:** further stand-in (0.5B/1B) quality runs for rung 3. They are dominated by key-to-key spread and the |S| ≤ k/1024 cap, and only 7B and 70B decide.

**5. Traps.**
- **V/O + interleave goes inside the 8-block rotation only.** On a 70B with γ folded but not rotated it costs +6.44% ± 0.50, on 139 of 141 windows. At 7B it was free even unrotated. The cause isn't known.
- **The unfolded registered 70B is broken under the fork's cast.** About a third of windows go to 9+ nats. Use the `fold` baseline (γ folded, no rotation) or rung 3, never `none`, at 70B.
- **`kt_stream_ppl.py eval` is load-bound.** It re-reads all 141 GB per group of 16 windows and exits 99 about every 4 minutes. Two chunks idled in their lease after an rc 99. Before any rerun:
  - prefetch the next layer;
  - make one pass for all windows;
  - loop in one lease for about 25 minutes (`server.md` 3:55 PM PDT).
- **The 70B quality proxy (`o_proj`'s output error) can't see depth-accumulated loss.** It read ×0.99 where perplexity outside the rotation was +6.4%. Trust perplexity.
- **This VM's prep uses 512 calibration tokens for 70B,** node 2's 2,048. The massive channels agree. Use node 2's prep for anything cited.
- **CPU BF16 forwards here are nondeterministic,** up to 9.8 in a logit between identical runs. Pair per window.
- **The store's filesystem returns EAGAIN under load.** Run scripts from a local copy and retry copies.
- **`pkill -f <pattern>` kills the shell running it.** Match on PIDs.
- **This VM has 15 GB.** The 70B registration checks need FP32 (not FP64) and one large job at a time.
- **No notes access:** `RESEARCH_NOTES_TOKEN` is unset here, and cursor[bot] gets a 403 on research-notes. Replies go through `internal/pouw-fp8/accounting-outbox/`.
