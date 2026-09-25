---
id: vllm-rf-c1/state
lane: vllm-rf-c1
kind: state
agent: bc-9eae5bc7 (Cursor), coordinator bc-ba6cec03
created: 2026-09-25T06:52Z
updated: 2026-09-25T11:22Z
---
# vllm-rf-c1: C1, commitment scheme vllm-v1 (named-scheme form)

## 11:22Z: DONE, READY.md written
- **Gate (a) T0+T1 at `7218ffbb` matches** a23b's same-pod base XML: 158 tests, 73 pass / 85 skip both sides, 0 outcome changes
  (`r20260925-092323-bdf1`, `evidence/gates/jdiff_a_head2_vs_a23b_base.txt`; 2 reworded skip reasons from `5cc0506e`, base drift).
- `vyv-rf-c1-big` TERMINATED 11:18Z after every run was fetched; no pod of this lane is running. Spend about $11.4 of $35.
- Branch `lane/vllm-rf-c1` pushed at `53314d1c`; A4 still not in origin/main (11:19Z, main `767115db`); rebase onto main pending.
- READY.md: `~/.research/notes/lanes/vllm-rf-c1/READY.md`.

## 10:40Z
- Gate (a) at `7218ffbb`: 108/158 (48 pass, 60 skip, 0 fail) at 10:39Z; ETA ~11:20Z. A4 still not in origin/main (10:35Z; main
  `5ac28010`, whose new commits touch neither packages/verity nor integrations/vllm). Pod deadline now 14:00Z (coordinator 10:01Z).

## 10:08Z
- **Gate (b) at `53314d1c`: 0 new failures** vs same-pod base (`r20260925-094310-c681`, `evidence/gates/jdiff_b_head3_vs_base.txt`);
  2 base failures pass, 1 new skip (test_scheme_cuda, CPU), 4 new passing tests. READY.md drafted (gate (a) pending).
- Gate (a) at `7218ffbb` (`r20260925-092323-bdf1`): 48/158 at 10:04Z; the base XML's remaining tests took 70 min -> ETA ~11:15Z.
  Then fetch, jdiff vs a23b's same-pod base XML, terminate `vyv-rf-c1-big`, final message.
- A4 still not in origin/main (09:54Z).

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T14:00Z (7 AM PT)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

## 09:48Z summary
- Branch `lane/vllm-rf-c1` **pushed** (custody rule), head `53314d1c` = commit 5 (p09 allowlist: drop the `commit <-> program`
  package-cycle entry, gone once semantic_layout left the package; the lints at `7218ffbb` failed only on that stale entry).
  Lints at `53314d1c`: 45/45 (`r20260925-093225-daa0`).
- Gate (b) at `7218ffbb` vs same-pod base (`r20260925-092213-b86c`, `evidence/gates/jdiff_b_head2_vs_base.txt`): only new failure =
  that p09 stale entry (fixed by `53314d1c`); dead-modules failure gone; 2 fixed (test_roundtrip, row_pod_cancel timeout); 1 new
  skip (test_scheme_cuda, CPU). Gate (b) re-run at `53314d1c`: `r20260925-094310-c681` (started 09:43Z).
- GPU at `7218ffbb` (`r20260925-092150-e650`): CUDA tests 163 passed; #101 run root `7adcef49…` == record, commit_pass, Program
  `ccc21347…` / manifest `90f81868…` head == base; ab_compare volatile-only; snapshot diffs = 96 device pointers
  (`block_table_ptrs`); throughput hashing 0.490 s, 1.85 GB/s, 7.24 M leaves/s. `vyv-rf-c1-g2` TERMINATED 09:44Z.
- Gate (a) T0+T1 at `7218ffbb`: `r20260925-092323-bdf1` running (expected ~11:05Z; `53314d1c` differs by one allowlist line).
- **agkr-bound mapping task: DONE 09:45Z.** Verdict "replace": production binds none of the four provisional digests and has no
  per-port operand tree; relabel them backend-owned or use production's per-step StepDomain (program = committer's
  root_program_digest, NOT the Program; ctx = sha256(run_id/step=s); geo = model json; layout = step tensor list; GPU-tree chunk
  leaves on every serving committer). `lanes/coordinator/20260925T0945Z-handoff-from-vllm-rf-c1.md`, copied to `lanes/agkr-bound/`.
- A4 still not in origin/main (09:34Z); main's new commits touch neither packages/verity nor integrations/vllm.

> **Coordinator, 09:30Z: custody rule for the cloud switch-over.** Push your branch to origin after every commit, WIP included. If you have uncommitted work worth keeping, commit it now and push. The coordinator pushed snapshots of uncommitted work to wip/vllm-rf-{lane} for custody; they are not for merge, so ignore them.

> **Coordinator, 09:18Z: NEW TASK, do it before phase 2.** Confirm or replace research lane agkr-bound's provisional `verity/gkr-commit/vllm-v1` operand-domain mapping (program, ctx, geo, layout) against vLLM's actual serving commitments. Then write the verdict to the research coordinator's inbox, `~/.research/notes/lanes/coordinator/{ts}-handoff-from-vllm-rf-c1.md`, and copy it to `lanes/agkr-bound/`. Details: `20260925T0918Z-handoff-from-vllm-coordinator.md` in this directory.

Deadline for vyv- pods: 2026-09-25T09:00Z (coordinator extends). Budget: $35 pod spend; spent about $0.40 before phase 2 pods (phase 2 pods: $4.61/h from 08:36Z).

## Status
- Phase 1 (evidence only, no repo commits): DONE 07:29Z. No mismatch anywhere (both results below).
  - Source for pod runs: clean detached worktree `~/projects/verity-wt/rf-c1-p1` at `origin/main` `00ffe398` ("Merge #15").
- Phase 2: A4 not yet in `origin/main` (checked 08:12Z: main `5631e667`; A4 head moved to `10996616`, linear over `14b0cf9f`,
  test-file moves only). `origin/main` past the A4 fork (`00ffe398`) touches only `backends/numerical` (#19, #20), so gates run on the
  A4-based head carry to the rebase onto main as long as A4 lands unchanged.
  - Branch `lane/vllm-rf-c1` (worktree `~/projects/verity-wt/rf-c1`, local, not pushed yet), on A4 head `10996616`:
    1. `af8d9711` scheme.py + rerouting (hidden_engine.py deleted; p10 caps native_host 2587->2579, padding_steps 930->914)
    2. `09ed0361` pod-marked `tests/commit/test_scheme_cuda.py` + PROTOCOL.md section 6
    3. `472207c3` per-scheme throughput in Spans / the Commit row (`spans_throughput`) + `tests/pipeline/test_spans.py`
    Laptop ast checks (syntax, p10 sizes, imported names): 0 errors, 0 unresolved.
  - When A4 lands: `git rebase --onto origin/main 10996616`, push `lane/vllm-rf-c1`.
  - Host layout label (`chunk-leaf-v1` on host committers): NOT fixed. It flows `pipeline/commit.py` `collector["layout"]` into
    `binding.build_binding_map` entries and so into `map_digest`; fixing it changes a digest. Listed for READY.md.
  - Next: pod gates (lints; gate (b) head+base same pod; gate (a) T0+T1 cpu3m; GPU row #101 + throughput + test_scheme_cuda).

## Pods
- Phase 2 (08:36Z): `vyv-rf-c1-big` = RunPod `rg1phl3ogbwgy2` (cpu3m 64 vCPU / 512 GB, 200 GB disk, $3.52/h) and `vyv-rf-c1-g2` =
  RunPod `pbsu9tvac48iqr` (1x L40S, driver 580.178.04, CUDA 13.0, $1.09/h), both `research pods register ... --guard 90`
  (`~/.research/notes/machines.d/vyv-rf-c1-{big,g2}.toml`). A first `pods create` pair whose shell died also created pods
  (`p3nyo6vv74j7at` big, `49jvnr6ll3vu7u` L40S): both terminated at 08:39Z, a few minutes after creation, never used.
  - Trees: head `472207c3` -> `/workspace/head`, base `10996616` (worktree `rf-c1-p1`, detached) -> `/workspace/basetree` (g2) and
    `/workspace/base` (big), shipped with `research pods sync`.
  - g2 run `r20260925-084508-e7c3` (`evidence/pod-scripts/g2.sh`): bootstrap --gpu LLAMA32_1B, CUDA tests at head, #101 head then base,
    ab_compare, throughput. 08:51Z BOOTSTRAP-OK. CUDA tests at head (test_scheme_cuda + test_production_vectors + test_leafhash_device +
    test_spans): **98 passed, 0 skipped** (FA2 tap tree present). #101 head: build PASS (step `03ace66f`, manifest `90f81868` 7043 = f3's),
    match PASS; commit running 09:02Z.
  - big runs: boot `r20260925-085137-18b5` (BOOTSTRAP-OK from the base tree, ops/ identical; xdist 3.8.0, xgrammar 0.2.7; freeze vs a1's
    baseline differs only in googleapis-common-protos 1.75.3->1.75.4, uvicorn 0.53.0->0.54.0); gate (a) `r20260925-085456-de22`
    (`big_gate_a.sh`: prefetch.sh then gate_a.sh T0+T1 at head); lints + gate (b) `r20260925-085512-8c77` (`big_gate_b.sh`).
    **Lints: 45/45 pass at head and at base**; allowlists at head vs base: only p10_size caps shrink (2587->2579, 930->914).
    Gate (b) xdist head + base 08:56-09:11Z. jdiff head `472207c3` vs same-pod base: 1 new failure,
    `tests/test_no_dead_modules.py::test_no_new_dead_modules`: `verity_vllm.commit.fasttree` and `.semantic_layout` became unreachable
    (production took only fold / fold_levels / pos_leaf / semantic_root from them; now in scheme). The keep-list is shrink-only, so:
    **commit 4 `7218ffbb`** moves both to `tests/commit/` (test-only; a23's precedent), drops their 4 P07/P11 entries, README /
    PROTOCOL / kernel comments name scheme. Otherwise: 1 new skip = `tests.commit.test_scheme_cuda` (collection skip, no GPU; by
    design); `test_roundtrip::test_transient_storage_is_released` failed -> passed.
  - Re-runs at `7218ffbb` (rsync installed on both pods; delta sync 7-16 s): gate (b) + lints `r20260925-092213-b86c`
    (`big_gate_b2.sh`), GPU `r20260925-092150-e650` (`g2b.sh`: CUDA tests + #101 head only vs the same-pod base row), gate (a)
    `r20260925-092323-bdf1` (`big_gate_a2.sh`, from the prefetched store; no key). The gate (a) at `472207c3` was stopped at 09:22Z
    (20 min in, 36 of 158 done) in favour of the head one.
  - #101 at `472207c3` (run `r20260925-084508-e7c3`, fetched): head and base run root `7adcef49…1dec5` == record, commit_pass true,
    every check PASS; Program `ccc21347…` / manifest `90f81868…` (7043) head == base (== f3's; the record's `079ee0a8…`/`368283ad…`
    predate the relayout). ab_compare: 61 row files identical, 24 differ only in volatile facts (timings, RSS, tmp paths, request-id
    suffixes, file shas of those) and hidden_gpu.py's source sha (`f273381f` head vs `78df1215` base = the two trees' files).
    Throughput (head, `spans_throughput`, scheme `vllm-v1`): hashing 0.560 s, 907 708 156 B, 3 545 764 leaves -> 1.62 GB/s,
    6.33 M leaves/s (leaves and bytes == the row's `leaves` / `bytes_bound`).
  - Fixture key: minted on the laptop 08:54:46Z (3 h, object-read-only), piped by ssh into `/root/r2ro.env` on vyv-rf-c1-big (786 B,
    mode 600, never printed). prefetch.sh: 26 ok, 0 FAIL, **key deleted 09:02:43Z** (confirmed absent).
- `vyv-rf-c1-g1` (runpod `zaazjzf44rc4wr`), 1x L40S, CUDA 12.9/13.0 allowed, guard 90. Created 07:07Z, TERMINATED 07:29Z
  after every run was fetched (`machines.toml` entry marked).
  - Runs: bootstrap `r20260925-070509-d288` (BOOTSTRAP-OK); `r20260925-071724-fd55` (failed: H1 harness bug); `r20260925-072312-94f5`
    (CUDA vectors); `r20260925-072432-1077` (weights root). All fetched with `--all`, all `preserved=yes`.
- Fixture key: own 3 h read-only key minted on the laptop 07:20Z, piped by ssh into `/root/r2ro.env` (786 bytes, never printed);
  fetched row #101 records (`art:a4ea1a18…`, 129 MB) with `evidence/pod-scripts/fetch_records.sh`, which deleted the key in the
  same ssh session right after the fetch, before 07:23Z ("key deleted").

## Results
### Phase 1.1: CUDA SHA-256 copies vs `vllm-v1` vectors: ALL EQUAL (run `r20260925-072312-94f5`)
Evidence: `evidence/cuda_vectors.r20260925-072312-94f5.json` (vectors.json sha256 `f63cd95d…`). L40S sm_89, torch 2.13.0+cu129,
vLLM 0.28.1rc1.dev472, nvcc 12.4. Driver `evidence/pod-scripts/cuda_vectors.py`. Result: `CUDA-VECTORS-OK`, 0 mismatches.

| copy | how it was run | equal | covered vectors |
|---|---|---|---|
| `native_tree.cu` (production .so) | ctypes on the extern "C" launchers of the JIT-built `verity_native_collect.so` (sha256 `bee47f00…`) | 33/33 | chunk_leaf 0–2 (whole step + ci_base window), trees N=1–17 (root + every path), node, lift, run-root fold ×2, weights-root fold |
| `native_tree.cu` (standalone) | `nvcc -O3 --use_fast_math -arch=sm_89` | 33/33 | same |
| `hidden_gpu_tree.cu` | production `hidden_gpu.ext()` | 30/30 | chunk_leaf 0–2, trees N=1–17 (root + paths), node, lift (via 3-leaf `tree_levels`), run-root fold ×2, weights-root fold |
| `native_leafhash.cu` | production `leafhash.ext()` | 45/45 | pos_leaf len 1–4096 (single + tail after 256/4096 leaves), trees N=1–17, node, weights-root fold |
| `verity_tap.h` (H1, VERITY_TAP=4) | harness TU per src_mask over the tap8 FA2 tree | 3/3 | thread_leaf 0–2 (src_mask 1, 27, 16) |

Not covered, by construction: chunk_leaf[3] (BN/D = 64/128; the chunk kernels hard-wire header words 8/9 to 0, as PROTOCOL §6 says);
the empty tree, `empty/v1`, `leaf/v1` and every root's binding (host code); pos_leaf len 0 (`pos_leaves` refuses it; the host skips numel 0).
The first attempt `r20260925-071724-fd55` failed only because the H1 harness lacked FA2's global `using namespace cute;` (harness bug,
fixed; A–C were already all equal there).

### Phase 1.2: weights root of a live model: ALL EQUAL (run `r20260925-072432-1077`)
Evidence: `evidence/weights_root.r20260925-072432-1077.json`; per-tensor roots and sha256 in the run's `weights_tensors.json`.
Driver `evidence/pod-scripts/weights_root.py --case LLAMA32_1B --execution bi-eager --records /workspace/c1/records-101`.
Engine: `vllm_adapter.build_engine` (unsloth/Llama-3.2-1B @ `9535bd9b`, eager), committer `NativeHostCommitter(gpu_tree=True)`, chunk 256.

| root | value | tensors / bytes | wall |
|---|---|---|---|
| production `register_weights()`, `VERITY_WEIGHTS_HASH=host` | `8baa442834d58dc7a6cc2555da33fac41ab2fa50419fa5a4bada45e1f8aa9b16` | 163 / 2 488 406 272 | 25.3 s |
| production, `device` (`native_leafhash.cu`) | same | same | 0.1 s |
| production, `device-checked` (163/163 tensors checked) | same | same | 15.5 s |
| core `verity.commitments.vllm_v1` (pos_leaf per 256 B, fold, weights_root) | same | same | 33.6 s |
| row #101 recorded Commit root (`commit/runs.jsonl#1/commit/weight_registration`, host, chunk 256) | same | same | – |

geo digest `222df080…` (recomputed independently: equal); names digest `75cfc105…`.
Weights of record (`build_request/weights_of_record.json`, root_of_record `120a8d6f…`) checked against the live parameters with
`weights_of_record.check`: result True, 163 compared, 0 mismatched, 0 missing, shards pinned and ok.

## Found, not fixed
- thread_leaf[1] (src_mask 27) carries ok0 = 1 where the kernel constructor derives 0 for its (m_block, seqlen_q). The digest still
  matches (the header encodes the bits given), but the vector is a field combination the tap never emits. Vector-generation note, not a
  CUDA defect.
- The pod's nvcc is 12.4 while torch is cu129; every JIT extension above (production path) was built by that nvcc.

## Phase 2 prep (read-only, from `00ffe398`; re-check after A4's file moves)
Python copies of `vllm-v1` rules in `integrations/vllm/verity_vllm`: `commit/hashing.py` (H, tags), `commit/merkle.py` (node, lift,
empty, levels), `commit/hidden_stream.py` (fa2h chunk header and leaves, stream and thread roots), `commit/hidden_engine.py` (step root),
`commit/semantic_layout.py` (pos_leaf, semantic root), `commit/padding_steps.py` (run root), `acquire/native_host.py` (run and weights roots).
