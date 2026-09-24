---
id: r23-wave2/pipe-race/20260923T1120Z-report-pipe-race
campaign: r23-wave2
lane: pipe-race
kind: report (final)
status: done
repo: verity-main-wt/pipe-race @ 64c00bd + 5a569ab (branch lane/pipe-race, 1 commit, `git status --short` clean, no conflict markers)
pod: vy-pipe-race = RunPod t5gcn5oo50xgsb (RTX 4090 24564 MiB, EUR-IS-2 -- EU-RO-1 had no 4090 at 11:12Z; host AMD EPYC 7402 24-Core, 48 vCPU; $0.74/h), created 11:12:17Z, TERMINATED 11:48:45Z (37 min, ~$0.46 of the $1.50)
---

CHECKPOINT 5a569ab (11:50Z, final) -- **root cause found, fixed additively in `encode_simt.py`, proven: kernel-level reproduction 20/20 wrong -> 0/20; after the fix 0 rejections in 143/143 depth >= 3 sub-batches by Rust `ligero-verify batch` (p4 104, p3 39) + 0 / 780 by the prover's verifier at depths 4 and 3 (25 + 5 runs x 13 each) + depth-4/3 proof bytes == depth-1 bytes for the same coins (no-ZK, 3 x 13 x 3) + `pytest backends/direct/ligero --ignore=privsel` **142 passed** on the fixed tree (dev-4090's 140 + the 2 pipeline tests of the new file's first version) + the final `pipeline_race_test.py` 6/6 on the fix while 3 of its 4 encoder cases FAIL on 64c00bd.  `t.total` p4 0.201-0.208 s vs p2 0.328 s: depth 4 still buys ~37 %.  Recommendation: keep `--pipeline 4` as the default WITH this fix; without it, no depth > 2.**
The bug is NOT in `pipeline.py` / `protocol.py`: it is the SIMT encoder's per-CTA global scratch (`encode_simt.py:462-463` on 64c00bd, `self.cf_scratch` / `self.stg`, enc-hopper `af3b7de` + `15d370e`), one buffer per encoder OBJECT, and `encoder_for()` caches one object per (l, n, t_pad, device) -- so every pipeline slot's stream launches the same kernel on the SAME scratch.  Fix: allocate the scratch per launch on the launch stream (torch's stream-ordered caching allocator; the graph's private pool under capture).  Transcript unchanged.

Earlier: CHECKPOINT 5a569ab (11:40Z) -- root cause found and fixed; kernel-level reproduction 20/20 -> 0/20; prover-level 0 rejections in 195 sub-batches at depths 4/3/2 after the fix; Rust batch verify + byte identity + pytest running.

# pipe-race: honest depth-4 proofs rejected by the verifier (frozen main 64c00bd)

## 0. Pod and bootstrap

* `python -m research.pods.runpod create --name vy-pipe-race --gpu "NVIDIA GeForce RTX 4090" --disk 60 --data-center EU-RO-1` -> `HTTP 500 There are no instances currently available` (11:12Z); without `--data-center`: `t5gcn5oo50xgsb` in **EUR-IS-2**, `NVIDIA GeForce RTX 4090, 24564 MiB` (the reference size; `--require-reference-part` not used, as briefed), host **AMD EPYC 7402 24-Core (48 vCPU)** -- NOT dev-4090's Ryzen 9 7950X; this matters for §2.
* Tree: `git archive 64c00bd` subset (`backends/direct backends/numerical backends/shared backends/ligero-verify/{src,tests,Cargo.*} packages/verity/src tools/research pyproject.toml uv.lock fixtures/bench-instances fixtures/tc`, 3.1 MB gz) -> `/workspace/src` (unfixed baseline) and `/workspace/fix` (+ this lane's two files).  Upload took 193 s (laptop uplink).  `backends/shared` shipped (dev-4090's host-Merkle gotcha avoided).
* Bootstrap = dev-4090's `/tmp/d4090/bootstrap.sh` minus the live probe and the v2 cache (`evidence/bootstrap.sh`): venv312, torch 2.6.0+cu124, cupy-cuda12x, blake3, pytest; `cargo build --release` of `backends/ligero-verify` -> `/workspace/bin/ligero-verify`; fp8-ada 4096-VU instance cache.  `BOOTSTRAP_OK` at 11:25:44Z.
* Worktree `~/projects/verity-main-wt/pipe-race` = `lane/pipe-race` from 64c00bd; main untouched.

## 1. Root cause (file:line on 64c00bd)

`backends/direct/ligero/encode_simt.py`:

* `:462` `self.cf_scratch = cp.empty(self.blocks * l if self.cf_global else 1)` -- the CF_GLOBAL variant (enc-hopper `af3b7de`): on parts whose shared memory per block cannot hold x + cf (Ada / consumer Blackwell, 99 KiB: `4 * 2 * l > sharedMemPerBlockOptin`, i.e. **l = 16384 on the RTX 4090**) the coefficient buffer of each CTA lives in a per-CTA L2 scratch, indexed `cf_scratch + blockIdx.x * K` (`:187`).
* `:463` `self.stg = cp.empty(self.blocks * 3 * l if self.stage else 1)` -- the STAGE store (enc-hopper `15d370e`, default on sm_80+, i.e. **every l on Ada/Hopper/Ampere**): cosets 0-2 of a row are parked in a per-CTA staging buffer `stg + blockIdx.x * 3K` (`:312`) and read back for the 16-byte stores.
* `:552-561` `_ENC` / `encoder_for(l, n, t_pad, device)`: ONE `LigeroEncoderSIMT` object per configuration, shared by every caller.  `protocol._simt_encoder` (`protocol.py:772`) returns that object to every sub-batch, on every slot's stream (`pipeline.slot_for`), and both the commit graph (`protocol.py:1291` `enc.encode(Wg, Sg["W"], want_coefs=True, out=st.U[:m])`) and the tests graph (`protocol.py:1017-1019` `penc.encode(cc.coef.reshape(D * R, l))` -- the chain rows, the t_pad = 0 object) capture launches that carry the object's scratch pointers as kernel arguments.

The pipelined prover (`pipeline.prove_many`, hp2-host) keeps `depth` sub-batches in flight on their own streams; a stage's device work is only stream-ordered against the same slot.  When two sub-batches' encoder kernels of the same object are on the device at once, their CTAs of equal `blockIdx.x` write the same scratch words.  Because the STAGE grid is exactly the resident CTAs (one 1024-thread CTA per SM at l = 16384: `blocks = 128`, grid-stride over the 3769 rows), kernel B's first CTAs are dispatched onto the SMs freed by kernel A's CTAs that had one row fewer -- exactly while A's CTAs `0 .. (R mod 128) - 1` are still on their last row, with the same block ids: the collision is not a rare interleaving, it happens whenever two encodes overlap at all.  A corrupted witness row breaks `U[:m]` against `coefs` (the verifier's **proximity test**); a corrupted chain row R_i breaks `q` (**chain constraints failed (sum over H)**) -- the two error texts dev-4090 saw.  hp2-host's design ("slots, streams, pinned buffers; anything a stage writes must be per slot") was correct for the encoder it was written against (shared memory only, per-call outputs); enc-hopper's two later kernel variants added the only global mutable scratch in the prover, and merge-val validated the merge at depth 2 -- where two commits (or two tests graphs) almost never overlap: at depth 2 a new sub-batch starts only when the other one finishes, so the in-flight pair is (commit, tests/openings); at depth >= 3 two sub-batches can be in the same stage.

Other candidates checked and cleared (all per call or per stream): `_TESTS_STATIC` / `_TGRAPHS` / commit graph keyed per stream (`protocol.py:856, 1118`); `Slot.pinned` buffers per slot and each awaited before the slot is reused (`c1`, `mkey`, `root`, `msgs`, `cols`, `open`); `tests_fused.lincomb` `partial = torch.empty` per call; `witness_device.run` `W = torch.empty` per call; `mask_sampler.stream` `out_t = torch.empty` per call (the pinned key ring is not used with `key_dev`); `openings_device` / `hash_gpu.merkle.commit` cupy allocations per call (cupy's pool is stream-keyed); `chain.chain_coefs` new tensors per call, `_TABLES` / `_GINV` / `_CONST_CACHE` / twiddles read-only.  `LIGERO_GRAPH_STRICT=1` not needed: the kernel-level test below reproduces the corruption with no graphs at all.

## 2. Reproduction

**Kernel level (deterministic; `evidence/enc_race.py`)**: the same encoder object launched on two streams at once, each trial compared with the sequential reference (`torch.equal`), RTX 4090:

| tree | l | t_pad | cf_global | stage | trials with a wrong codeword | wrong rows |
|---|---|---|---|---|---|---|
| 64c00bd (base) | 16384 | 0 (chain encoder) | True | True | **20/20** | **1886 / 150760 (1.25 %)** |
| 64c00bd + 5a569ab (fix) | 16384 | 0 | True | True | 0/20 | 0 |
| fix | 16384 | 256 (ZK witness encoder) | True | True | 0/20 | 0 |
| fix | 8192 | 0 / 256 | False | True | 0/20, 0/20 | 0 |
| fix | 4096 | 0 / 256 | False | True | 0/20, 0/20 | 0 |
| base | 16384 | 256 (ZK witness encoder) | True | True | **20/20** | 1691 |
| base | 8192 | 0 / 256 | False | True | 0/20, 0/20 | 0 |
| base | 4096 | 0 / 256 | False | True | **20/20, 20/20** | 1957, 1430 |

The base rows match dev-4090's sweep exactly: `--batch 8192` (l = 8192) was the ONE p4 cell that passed (25/25), `--batch 4096` (l = 4096, STAGE scratch only) and `--batch 16384` (l = 16384, both scratches) lost sub-batches.  At l = 8192 the STAGE kernel runs two 512-thread CTAs per SM and the two kernels' equal block ids happen not to coincide in time on this part; at l = 4096 / 16384 they do.

**Prover level (`pipeline_race_test.py` harness = `prove_vus_many` at depth d + `verify_vus` per sub-batch, the same check `bench_vu_rel` asserts on; fp8-ada, 4096 VUs, `--batch 16384` = 13 sub-batches of <= 341 VUs, l = 16384, ZK interactive, local coins)**:

| tree | depth | runs x sub-batches | rejected | median pass wall |
|---|---|---|---|---|
| base | 4 | 5 x 13 + 25 x 13 | 0 / 390 | 0.185-0.190 s |
| base, `run.py bench-vu --pipeline 4 --reps 3` (dev-4090's line minus the live verifier) | 4 | 3 x 13 | 0 / 39 (`validation: passed`) | prover 0.173-0.201 s |
| **fix** | **4** | 5 x 13 + 25 x 13 | **0 / 390** | 0.193 s |
| fix | 3 | 5 x 13 + 25 x 13 | 0 / 390 | 0.225 s |
| fix | 2 | 5 x 13 | 0 / 65 | 0.315 s |
| fix, no ZK, depth 1 / 4 / 3 | 1, 4, 3 | 3 x 13 each | 0 / 39 each; **proof bytes of depth 4 and depth 3 == depth 1 for the same coins, all 13 x 3 x 3** | 0.587 / 0.196 / 0.202 s |

**The prover-level race did not fire on this pod's host even on the unfixed tree (0 / 429)**, while dev-4090's Ryzen 9 7950X host lost 1-2 of 13 sub-batches in 5 of 6 depth-4 attempts.  Whether two encodes overlap on the device is a matter of host timing: two sub-batches enter the same stage back-to-back when the driver finds two jobs ready in one `prove_many` loop iteration (two finished sub-batches -> two commit graphs launched within a millisecond; two squeezes done -> two tests graphs), which depends on how fast the main thread launches relative to the GPU -- a 7950X (fast cores) keeps more jobs ready at once than this loaded EPYC 7402 (load average 11-15 from neighbours during the whole session).  The kernel-level test removes the timing from the picture: it forces the overlap and shows the corruption on every trial, and its absence after the fix.  So the reproduction table does NOT show "depth > 2 fails here"; it shows the mechanism directly and the fix's effect on it.

## 3. The fix (commit `5a569ab` on `lane/pipe-race`, additive, `encode_simt.py` + a new test file)

`LigeroEncoderSIMT.__init__` no longer allocates `cf_scratch` / `stg`; it records their sizes (`cf_words`, `stg_words`).  `_launch` calls `_scratch(stream)`, which allocates the two buffers with `torch.empty` **on the launch stream** and appends their pointers to the kernel arguments; the tensors are dropped right after the launch.  Why this is race-free: torch's caching allocator is stream-ordered -- a block freed on stream A is only handed to a later allocation on stream A, i.e. after the kernel that used it in stream order -- so two launches on different streams never hold the same block at once; inside a CUDA-graph capture (the commit and tests graphs) the allocation comes from that graph's private pool and stays owned by the graph, so each slot's graph has its own scratch.  Cost: two pool hits per launch (the 25 MB staging block is cached per stream after the first launch); no kernel change; the codeword bytes are unchanged (kernel test above; byte identity §5).  Nothing else in the prover changed; `prove` / `prove_many` / the protocol are untouched.

## 4. Regression test (`backends/direct/ligero/pipeline_race_test.py`, GPU only, skipped on CPU)

* `test_encoder_scratch_not_shared_across_streams[l,t_pad]` for (16384, 0), (16384, 256), (8192, 256), (4096, 0): two concurrent encodes of one object bit-exact with the sequential reference (10 trials each).  Fails on 64c00bd at l = 16384 (20/20 above), passes with the fix.
* `test_pipeline_depth4_accepted_and_byte_identical[zk]`: 8 sub-batches of fp8-ada at l = 16384 proved at depth 4 and 3 (2 runs each), every proof accepted by `verify_vus`; without ZK (deterministic transcript: no mask key) the depth-4 and depth-3 proof bytes equal the depth-1 bytes for the same (fixed) coins.
* As a script it is the reproduction harness of §2: `python -m backends.direct.ligero.pipeline_race_test --relation fp8-ada --total-vus 4096 --batch 16384 --depth 4 3 2 --runs 5 [--no-zk]` (`LIGERO_INSTANCES_CACHE` for the instance cache).

## 5. Evidence (pod `/workspace/prace`, copied as text under `evidence/`; no dump trees pulled to the laptop)

All on the FIXED tree (`/workspace/fix` = 64c00bd + 5a569ab) unless marked base.  fp8-ada, 4096 VUs, `--batch 16384`, ZK interactive, `--target -128`, `--instance-procs 16`.

| what | command | result | file |
|---|---|---|---|
| kernel race, base vs fix | `enc_race.py <l> 3769 20 <t_pad>` | base 20/20 wrong at l = 16384 / 4096 (both t_pad), 0/20 at l = 8192; fix 0/20 everywhere (6 configurations) | `evidence/evidence2_base_and_fix.log`, `evidence/fix_evidence1.log` |
| prover harness zk, depth 4 / 3 / 2 | `pipeline_race_test --depth 4 3 2 --runs 5`, then `--depth 4 3 --runs 25` | **0 rejected of 390 (d4), 390 (d3), 65 (d2)** by `verify_vus`; median pass wall 0.193 / 0.225 / 0.315 s | same |
| prover harness no-zk, byte identity | `pipeline_race_test --depth 1 4 3 --runs 3 --no-zk` | 0 / 39 rejected at each depth; `identity ok` = the sha256 of `proof_bytes()` of every sub-batch equals the depth-1 run-1 digest at depth 4 and depth 3 (fixed coins) | `evidence/fix_evidence1.log` |
| `run.py bench-vu --pipeline 4 --reps 3 --dump-reps 3` | dev-4090's command line (no live verifier) | exit 0, `validation: passed`; **Rust `ligero-verify batch` (built from the tree, sha256 of the binary in `evidence/`): rep1-3 `13 accepted, 0 rejected ... batch ACCEPT ... python agreement 13/13`** = 39/39 | `evidence/fix_evidence1.log`, pod `/workspace/prace/fix/{p4.log,p4.json,dumps_p4}` |
| `run.py bench-vu --pipeline 4 --reps 5 --dump-reps 5` | | exit 0; Rust batch rep1-5 13/13 each = **65/65** | `evidence/evidence2_base_and_fix.log`, pod `p4b.*` |
| `run.py bench-vu --pipeline 3 --reps 3 --dump-reps 3` | | exit 0; Rust batch rep1-3 13/13 each = **39/39** | same, pod `p3.*` |
| `run.py bench-vu --pipeline 2 --reps 3` | | exit 0, `validation: passed` (in-process verifier 39/39) | pod `p2.*` |
| Rust-verified depth >= 3 sub-batches, total | | **143 / 143 accepted** (p4: 104, p3: 39), plus 39 (p2) and 429 + 39 (harness) by the Python verifier | |
| `pytest backends/direct/ligero -q -x --ignore=backends/direct/ligero/privsel` on the fixed tree | 11:34-11:45Z (this host is 4x slower than dev-4090's for the CPU tests) | **142 passed, 0 failed** (dev-4090: 140 on 64c00bd; +2 = the pipeline tests of the first version of the new file) | `evidence/pytest_fix.log` |
| `pytest backends/direct/ligero/pipeline_race_test.py` (final file: 4 encoder cases + 2 pipeline cases) | fix tree; then the same file on the BASE tree with `-k encoder` | fix **6 passed in 21 s**; base **3 failed, 1 passed**: `l=16384 t_pad=0/256` and `l=4096 t_pad=0` `10/10 concurrent trials wrote wrong codewords`, `l=8192` passes (as dev-4090's `--batch 8192` p4 cell did) | same |
| Rust verifier binary | `cargo build --release` from the shipped tree | sha256 `315ba10986091264a500dfea170e6f7861a5afd92138001308aeba99b5bab6bb` = dev-4090's binary byte for byte | |

`t.total` after the fix (median over reps, `result.json` `measurements[t.total]`; this EPYC 7402 host, load 11-25 from neighbours -- compare depths, not hosts):

| `--pipeline` | reps | `t.total` | vs depth 2 |
|---|---|---|---|
| 4 | 3 (p4) / 5 (p4b) | **0.2081 s / 0.2005 s** | -37 % / -39 % |
| 3 | 3 | 0.2299 s | -30 % |
| 2 | 3 | 0.3278 s | -- |
| harness pass wall (13 sub-batches, zk) | 25 | d4 0.193 s, d3 0.228 s, d2 0.315 s | d4 -39 % |

So depth 4 still buys a third over depth 2 on this host (dev-4090 saw 0.207 vs 0.291 s at `--batch 8192` where p4 happened to work), and with the fix it is as safe as depth 2.  Peak device memory at p4: 6.15 GB (`peak_device_bytes` 6148892672; dev-4090: 6.8 GB) -- the per-launch scratch adds ~33 MB per stream / captured graph at l = 16384.

## 6. Recommendation for the coordinator

* **Merge `5a569ab` (two files, additive) into the tree the campaign measures with; with it `--pipeline 4` can stay `run.py`'s default** -- 143/143 Rust-verified depth >= 3 sub-batches, byte-identical transcripts, `t.total` -37 % vs depth 2 on this host.  **Without it, no bench line may run deeper than `--pipeline 2`** (dev-4090's conclusion stands for 64c00bd: the race is in every depth >= 3 pass whenever two encodes overlap, and whether they overlap is host timing).
* Every result already recorded at `--pipeline 1` / `2` on 64c00bd is unaffected: at depth 2 the two in-flight sub-batches are in different stages (their proofs were verified anyway; a corrupted proof is rejected, never silently accepted -- the failure mode is a REJECTED honest prover, not a wrong number).
* Worth a follow-up (not done here, not needed for the fix): `_TESTS_STATIC` / `_TGRAPHS` / `_scratch` are keyed by or allocated per `torch.cuda.Stream`; torch hands out streams from a pool of 32 per device, so a run that creates > 32 `torch.cuda.Stream` objects (slots + one side stream per captured graph: `_TensorGraph`, `_graph_run`, `_tests_graph_run`, per slot and per chain layout) sees `cuda_stream` handles repeat -- at depth 4 the count is ~28-32.  Nothing in this lane's evidence points at it, but a side stream that aliases another slot's stream during a capture would capture (or refuse) that slot's launches; `pipeline.slot_for` could assert that the `depth` slot handles are pairwise distinct and the capture helpers could reuse ONE side stream per slot instead of a fresh one per graph.
* Tooling gotcha for other lanes: `tar` from macOS ships AppleDouble `._*.py` files; pytest tries to collect `._pipeline_race_test.py` and stops at `-x`.  `COPYFILE_DISABLE=1 tar ...` (or `find -name '._*' -delete` on the pod).

## 7. What could not be established

* The prover-level failure itself did not reproduce on this pod's host (0 / 429 sub-batches rejected on the unfixed tree at depth 4, harness + `bench-vu`); the causal chain is the kernel test (deterministic corruption whenever two encodes of one object overlap; the exact l values of dev-4090's failing cells and only those) + code reading (the encoder scratch is the only cross-stream mutable device state a stage writes; §1 lists what was cleared) + dev-4090's two error texts (the two verifier tests a corrupted witness row / chain row breaks).  A depth-4 run of the fixed tree on a 7950X-class host (dev-4090's pod class) would close that last gap; a `pytest backends/direct/ligero/pipeline_race_test.py` on any 4090 shows the base failing and the fix passing in 25 s.
* `bf16-hopper` and `--zk` off were not tabulated at the prover level on the base tree (time); the encoder object is the same code for every relation and the no-ZK path calls the same `_launch`, so the fix is relation- and mode-independent (the no-ZK path was exercised by the byte-identity runs).
* Not measured: whether the per-launch `torch.empty` costs anything measurable on the H100 (two pool hits per encode; the 25 MB STAGE block is cached per stream after the first launch).  On this 4090 `t.total` at p4 (0.20 s) is at dev-4090's p4-where-it-worked level (0.207 s at `--batch 8192`).

## 8. Pod accounting / timeline

vy-pipe-race `t5gcn5oo50xgsb` $0.74/h, 11:12:17Z -> terminated 11:48:45Z (`GET /pods/... -> 404 pod not found` confirmed): 37 min ≈ **$0.46**.  No `research data pull` of dump trees; evidence as text under `evidence/`.

11:11Z brief read; 11:12Z pod created (EUR-IS-2; EU-RO-1 had no 4090); 11:15-11:18Z tree upload (193 s); 11:18-11:25Z bootstrap; 11:20Z root cause identified by reading (`encode_simt.py:462-463` vs `_ENC`); 11:23Z fix written; 11:24Z baseline harness 0/65; 11:25Z kernel-level test: base 20/20 wrong, fix 0/20; 11:26-11:28Z evidence campaign 1 (fix: harness d4/3/2, no-ZK identity, bench p4 + Rust 39/39, bench p2); 11:29-11:32Z evidence campaign 2 (base kernel table, base harness 0/325, fix harness 0/325 x 2, bench p3 + Rust 39/39, bench p4 x 5 + Rust 65/65); 11:34-11:45Z pytest 142 passed; 11:38Z commit `5a569ab`; 11:40Z checkpoint; 11:47Z final test file 6/6 on fix, 3 failed / 1 passed on base; 11:48Z pod terminated; 11:52Z report final.
