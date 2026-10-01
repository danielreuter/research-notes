---
id: 20261001T0209Z-handoff-from-bc-36186951-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-36186951 (GPU 4, FP4 tensor-core capture on sm_120)
---

_Relayed verbatim from the Cursor store by old-accounting (bc-b729c175): the author's VM gets a 403 pushing to research-notes._

# bc-36186951 (GPU 4, FP4 capture): migration handoff. Nothing is in flight; one draft PR (#525) is kept, and the node-2 captures need preserving

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. Times are UTC (PDT + 7). "Store" means the old PoUS
Project's Cursor store, `/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/`. My running log is the store's
`internal/pouw/rtx-pro/workers/4-fp4-capture.md` (Results §1–§13, Needs, Lessons).

## 1. Branches and PRs

- **Branch `cursor/fp4-capture-sm120-9ff9`, PR [#525](https://github.com/danielreuter/verity/pull/525):**
  - Head `6ed30ed684fc801f596dd063719d7900a2dd77a6`, pushed. State: draft, open, 37 commits ahead of base `29f691be`.
  - The backlog row (with #507, #545 and the others) is done-but-unmerged; keep it as evidence behind γ and the divisor.
  - No `check` recorded. It conflicts with `main` (`4860d817`) in `pyproject.toml` only; `uv.lock`, `verity/ml/tc/models.py`
    and `tools/research/src/research/store/tools_registry.py` auto-merge.
  - It holds `tools/tc_probe_fp4/` (the probe, captures, prices, the     recheck and sparse tools and their CPU tests).
  - Locally the whole test file passed at `c2e83fda` (78 passed, 1 skipped), and the changed sparse test at `6ed30ed6`.
  - It also adds the core model object `BLACKWELL_SM120_E2M1_M16N8K32` in `verity.ml.tc.models`, with its replay test and
    fixture `art:cc1f274f…`. That one needs a core reviewer.
- No other branch or PR is mine.

## 2. Runs and jobs in flight

- **None.** Every job of mine on node 2 is done (rc 0), and no research run of mine is running.
- **The last fill jobs** (at `6ed30ed6`, prio 10, GPU 7 = GPU-af0bf9e0), all done by 23:47 yesterday:
  - `fp4-recheck3-6ed30ed6.sh` (gpus=1)
  - `fp4-sp-e4m3-6ed30ed6.sh` (gpus=1)
  - `fp4-recheck3-verify-6ed30ed6.sh`, `fp4-sp-e4m3-verify-6ed30ed6.sh`, `fp4-recheck2-reverify-6ed30ed6.sh` (gpus=0)
- **No custody.** They are fill jobs, so nothing has `--custody-r2`; the outputs are on node 2 only:
  - `/workspace/pouw/fill-out/fp4-recheck3/6ed30ed6/` (2.6 GB): NVFP4 and E2M1 seeds 20261103 and 20261104, with `verify/`.
  - `/workspace/pouw/fill-out/fp4-sp-e4m3/6ed30ed6/` (2.0 GB): sparse E4M3 seeds 20261201 and 20261202, with `verify/`.
  - `/workspace/pouw/fill-out/fp4-recheck2/d3b846cf/` (2.3 GB): seeds 20261101 and 20261102, with `verify/` (the first,
    wrongly gated pass) and `verify-6ed30ed6/` (the re-verify).
  - Earlier fill outputs, already cited in my log: `/workspace/pouw/fill-out/fp4-*`.
- **Preserved by hand today:** every verdict and capture record (194 JSON files, no word arrays) is in the store at
  `internal/pouw/rtx-pro/fp4-capture/fp4-verdicts-6ed30ed6.tgz` (sha256 `f2a90978…`). The word arrays (`*.npy`, about
  6.9 GB) are on node 2 only.
- **Research runs, all done:**
  - `r20260930-213931-c27c`: the sparse library, `libsp_e4m3_sm_120a.so`.
  - `r20260930-213945-8f13`: the FP4 library for the new capture.
  - `r20260930-183411-4dc5`: the FP4 library for the `d3b846cf` capture.
  - `r20260930-212100-4805`: an unused build.
  - Earlier cited runs are listed in my log.

## 3. Half-done state

- **Nothing exists only on my VM:** the checkout is clean and pushed, and the log is in the store. My VM reset twice today
  and lost `/tmp` and `~/.research` each time.
- **Results not yet under a research run id** (Measured; the verifies ran as CPU fill jobs, so they wrote no `result.json`):
  - **(a) The FP4 recheck beyond the gate, fresh seeds:** 0 misses on every gated word, 0 failures. Per seed:

    | Instruction | Seed | Gated words | Pinned model |
    |---|---|---|---|
    | NVFP4 | 20261101 | 173,170,688 | `verity` |
    | NVFP4 | 20261102 | 173,170,688 | `verity` |
    | NVFP4 | 20261103 | 197,918,720 | `verity` |
    | NVFP4 | 20261104 | 197,918,720 | `verity` |
    | E2M1 (`f8f6f4`) | 20261101 | 131,104,768 | `gs32_w26_native` |
    | E2M1 (`f8f6f4`) | 20261102 | 131,104,768 | `gs32_w26_native` |
    | E2M1 (`f8f6f4`) | 20261103 | 136,314,880 | `gs32_w26_native` |
    | E2M1 (`f8f6f4`) | 20261104 | 136,314,880 | `gs32_w26_native` |

    - `gs32_w26_native` has `BLACKWELL_SM120_E2M1_M16N8K32`'s parameters.
    - Seeds 20261103/4 run at `--fixed-mult 160`, so every gated family has at least 5.24M words per seed.
    - The controls miss, so the gate discriminates: on E2M1, `bsaa_g16` misses about 15.4M words per seed.
  - **(b) Sparse FP8 `mma.sp` (E4M3, m16n8k64, 2:4 along k) on the same operands as the dense k32 chain,
    `tc-model/sm120-e4m3-sp-k64`:**
    - Two seeds of 83,886,080 words each.
    - The sparse words are **one dense k32 atom on the 32 kept products**. The candidate `gather_g32` (one `GroupSum`
      (32,)/26/−133) misses 0 words. The dense twin on the compressed operands differs on 0 of 15,728,640 words.
    - They are **not** two chained dense k32 atoms on the logical operands: those differ on 22,120,370 and 22,114,536
      words (about 26%). In swapped order they differ on 22,118,611 and 22,119,094.
    - The two agree only on `one_half_live` (one logical half zero) and `signed_zero`.
    - Every dense twin is reproduced by its own model on every word (the control).
    - The device layout check settled the packing: metadata `row_q1_groups_q2`, B `k_4q_16r`.
- **A shortcut to flag:** `c4d5e0b7` holds two changes in one commit: the E2M1 gate fix, and `--fixed-mult`.

## 4. Next step for each kept item, and what I'd stop

- **#525:**
  1. Resolve `pyproject.toml` against `main` and regenerate `uv.lock`.
  2. Run `check` (`uv run --extra torch-cpu python tools/check/check.py --record --on <CPU pod>`) and have a core reviewer
     read `verity.ml.tc.models`.
  3. Mark the PR ready; the research coordinator merges it with `research merge`.
- **Publish (a) and (b) under run ids.** One CPU research run per seed on vy-nebius-2 (`--tool tc_recheck_fp4`, or
  `tools.tc_probe_fp4.tool:TC_SPARSE_E4M3`, `--source .` at `6ed30ed6`). It runs the same `verify` command the fill jobs
  ran, with `--capture`, `--prebuilt` and `--fixed-mult` as in each job script (the scripts are in
  `/workspace/pouw/fill/done/`), and writes `result.json`.
  - Cost: about 15–23 min per seed at `--procs 16` (Measured in fill).
  - Or put the capture trees into the evidence store with `research data put --tree … --preserve`.
  - Either way, the word arrays should leave node 2 before it is torn down.
- **Hand (b) to the approved-weights doc's owner, through the coordinator:**
  - `docs/pouw/approved-weights.md`'s open question is "Does `mma.sp` E4M3 m16n8k64 equal the dense chain on 2:4
    operands?" (its line 322, with line 93's "the FP8 capture is open"). The answer is no, measured: it equals one k32
    atom on the compressed operands.
  - §5 makes the 2:4-sparse exclusion conditional on exactly this, and the owner decides what follows.
- **The registry, if its owner wants it:** `sm120.mma.m16n8k32.e2m1.f8f6f4` now has four more fresh seeds and 534.8M
  zero-miss E2M1 words (Derived sum of the four E2M1 rows), far past P2's 1e7. A pinned entry still needs
  `tools/tc_probe/trust.py` P1–P5 and a dossier.
- **For the Lean lane, through the coordinator:** the store's `internal/pouw/rtx-pro/fp4-capture/sm120-fp4-step-for-lean.md`
  has an open question: a new `BlockScaledAlignAdd`, or `Pipeline` extended by six fields?
- **I'd stop:**
  - more FP4 recheck seeds (eight seeds, 0 misses; more words add nothing);
  - any attempt to size these captures as GPU-hours (they are host-bound);
  - rerunning the W1, F1, F2 and F3 price captures (settled in my log's §2 and §9–§11).

## 5. Traps

- **Unscaled and UE8M0-1X E2M1 on QMMA is not the block-scaled adder.**
  - `f8f6f4` and `mxf8f6f4` with E2M1 are `GroupSum` (32,)/26/−133; only `mxf4nvf4` (OMMA) is `BlockScaledAlignAdd`.
  - `recheck.py` once fell back to `bsaa_g16` and failed a sound capture. It now pins `gs32_w26_native`, and exits if its
    parameters drift from the registry model.
- **Fixed-size families:** `signed_zero`, `signed_zero_matrix` and `anchor_participation` ignore `--n-random`; use
  `--fixed-mult`. A verify must pass the same `--fixed-mult` as its capture, or it fails.
- **A verify must load the library its capture loaded.** Each research-run tree's build hashes differently, even from the
  same `.cu`. The `d3b846cf` capture pairs with `r20260930-183411-4dc5`; the `6ed30ed6` captures pair with `…-8f13` (FP4)
  and `…-c27c` (sparse).
- **These captures are host-bound:** the GPU was busy 36%, 3% and 0% of the lease in the three chunks (gpu-lease's
  sampler). For anything larger, generate and pack the operands in a gpus=0 job first.
- **The fill runner has no dependencies.**
  - My GPU jobs chained by `mv`-ing the next script from a staging dir (`/workspace/pouw/fill-out/fp4-jobs/6ed30ed6/`, now
    empty) into `queue/` on success.
  - Never queue two GPU jobs at once: one GPU at a time.
- **CPU fill jobs share 32 cores (96–127) across 4 slots.**
  - A `recheck.py verify` isn't checkpointed per family. One went past its 25-minute `max_min` under contention, was killed
    (rc −15) and redone from the top.
  - `sp_e4m3.py verify` checkpoints per family (`--budget-s`, exit 99); give `recheck.py` the same before a bigger run.
- **NVFP4 and FP8 sparse differ:**
  - The NVFP4 2:4 atom writes the dense atom's words.
  - The MXFP4 sparse atom does not: one 2X scale spans 64 columns.
  - The FP8 E4M3 sparse atom equals one k32 atom on the compressed operands, not two chained ones.
  - Don't carry one row's answer to another.
- **The registry's pinned NVF4 entry** cites autoproof's unscaled probe (`_AUTOPROOF_UNSCALED`) as evidence for the
  align-add. Those 1,400 words fit three rival models, so it supports nothing; I left it unedited.
- **This VM's environment** (old Project; may not apply in the new one):
  - Raw `ssh` to node 2 fails host-key verification. Use `research.pods.runpod.ssh_command("81.85.2.121", 22,
    user="research")`, which brings its own key and known_hosts.
  - `research status <id>` isn't a command; use `research fetch <id>` and `research inspect <id>`.
  - The notes repo is `danielreuter/research-notes`, read through a credential helper that reads
    `$RESEARCH_NOTES_TOKEN` when called.
- **The store's filesystem is flaky:** write a `.tmp`, `mv` it, and re-hash after the copy lands.
