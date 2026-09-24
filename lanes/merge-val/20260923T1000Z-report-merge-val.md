---
id: r21-night2/merge-val/20260923T1000Z-report-merge-val
campaign: r21-night2
lane: merge-val
kind: report
status: closed
repo: verity-main-wt/merge-val@a55b3fc (main; fix committed as 538801e on branch lane/merge-val, NOT on main)
origin: https://github.com/danielreuter/verity.git
---

VERDICT: FAIL — main a55b3fc passes the bare/hashed gates, the hashed bench and the live verifier at pipeline depth 1, but `--pipeline >= 2` crashes (hash-relation's `chain.py:161 .tolist()` inside hp2-host's tests-stage CUDA-graph capture; 3-line fix on `lane/merge-val` 538801e restores (e)/(g): live ACCEPT + Rust ACCEPT), the fp8-ada-v3 gate dies with the same RNG/graph error at its first negative (honest 25/25 ok), and all four privsel v3 differential tests fail on CPU (relmin-lookup's post-branch pubsel commits under relmin-private's v3 units; fp8-ada-v3 already failed on relmin-private's own 9a42e39).

# merge-val: GPU validation of main a55b3fc (hp2-host + enc-hopper + fp4-fast + relmin-lookup v2 + relmin-private v3 + hash-relation + live-pipeline)

Pod `vy-merge-val` = RunPod `uwovuyy842njoj`, RTX 4090 **49140 MiB variant** (EU-CZ-1, SECURE, EPYC 7763 host, $0.74/h).  EU-RO-1 had
no capacity (`POST /pods -> HTTP 500 "There are no instances currently available"`); the second create (any DC) returned the 48 GB
variant and `--require-reference-part` exited 3 as designed.  I kept it: this lane is a functional PASS/FAIL gate, not evidence, and
the 45-minute deadline did not leave room for a third create.  Nothing here should be labelled or pushed as a measurement.
Tree shipped by `tar | ssh` (no rsync on the image) to `/workspace/src`; bootstrap = the hash-relation recipe
(`evidence/bootstrap.sh`: venv312 torch 2.6.0+cu124, cupy-cuda12x, blake3, pytest 9.1.1; rustup 1.98.1, `cargo build --release` of
`backends/ligero-verify` in-tree -> `target/release/ligero-verify` sha256 db4ec096…; BOOTSTRAP_OK in ~90 s).  `PYTHONPATH =
packages/verity/src:backends/numerical/python:.`.  Every command + exit code: `evidence/commands.log`; per-item stdout/stderr
`evidence/<item>.log` (the (e)/(g) logs are from the re-runs with the fix; the failing text is quoted verbatim below).
Driver: `evidence/items.sh` (items a-g, `rust_*`, and the diagnostic variants e1 / g1 / g_nozk).

## Per-item table

| item | command (on the pod, `/workspace/src`, `PY=/workspace/venv312/bin/python`) | exit | result | notes |
|---|---|---|---|---|
| (a) | `$PY -m pytest -q backends/direct/ligero -x -p no:cacheprovider` | 1 | **FAIL** — `1 failed, 80 passed, 1 skipped in 121.78s`, stopped at `privsel/relation_test.py::test_differential_v1_v3[bf16-hopper-v3]` | Re-run without `-x` (a2): **4 failed, 165 passed, 1 skipped in 331 s** — the four failures are exactly `test_differential_v1_v3[{bf16-hopper,bf16-ampere,fp8-hopper,fp8-ada}-v3]`; everything else in the directory (witness_device_test, encode_simt_test, hashchain_test, live_test, pubsel/, fp4/) passes.  Real merge break, not env — diagnosis below. |
| (b) | `$PY -m backends.direct.ligero.run --relation fp8-ada gate-vu --device cuda --vus 2048 --batch 4096 --instance-procs 8 --instances-cache /workspace/instances-cache` | 0 | **PASS** — `fp8-ada gate: 25 honest sub-batches, 92 negatives, 0 failures` (62 s) | first sub-batch 49.9 s (kernel compile), then 0.04 s each |
| (b) | same, `--relation bf16-hopper` | 0 | **PASS** — `bf16-hopper gate: 49 honest sub-batches, 87 negatives, 0 failures` (220 s) | 3 min of single-thread CPU before the first sub-batch (torch inductor compile workers spawned), then 0.03 s each |
| (c) | `… --relation fp8-ada gate-vu --device cuda --vus 2048 --batch 16384 --auth included-hash …` | 0 | **PASS** — `fp8-ada hashed gate: 7 honest sub-batches, 86 negatives, 0 failures` (49 s) | first hashed sub-batch 33.9 s (NVRTC fused witness kernel), then 0.14 s (+hints 0.02 s) |
| (d) | `… --relation fp8-ada-v3 gate-vu --device cuda --vus 2048 --batch 4096 …` | 1 | **FAIL** — all **25 honest sub-batches accepted** (first one ~11 min: v3 hint-program compile; then 0.02 s each), then the negatives phase crashed before any negative was tried: `relchain.py:541 negatives -> :240 prove_vus -> pipeline.py:293 run_to_completion -> protocol.py:1233 _prove_stages -> relchain.py:249 hints_fn -> relations.py:316 _v3_hints -> privsel/hints.py:197 hints_v3 -> :223 run -> torch CUDAGraph.replay: RuntimeError: Offset increment outside graph capture encountered unexpectedly.` (710 s) | Same error class as Break 1 (a swallowed failed CUDA-graph capture leaves torch's RNG generator in capture state; the next graph replay — here the v3 hint program's own CUDA graph in `privsel/hints.py:223` — raises).  Run on the UNFIXED chain.py; not re-run with 538801e (no time: the 11-min compile).  Negatives untested. |
| (e) | `… --relation fp8-ada bench-vu --zk --mode interactive --batch 16384 --total-vus 1024 --reps 1 --target -128 --device cuda --pipeline 2 --verifier tcp://213.173.105.69:30899 … --out /tmp/mv/bare/result.json --dump-dir /tmp/mv/bare/proofs --dump-reps 1` | 1 | **FAIL on a55b3fc** — `RuntimeError: Offset increment outside graph capture encountered unexpectedly.` (traceback below), 12 s in, no dumps written | **PASS with the fix** (538801e): live verifier `ACCEPTED 4/4`, `t.total 0.4577 s`, `t.total_live 0.730 s`, validation `passed`; Rust `batch`: `4 accepted, 0 rejected … batch ACCEPT … system pinned (fp8-ada)`.  Control e1 = same with `--pipeline 1` on the unfixed tree: exit 0, live `ACCEPTED 4/4`, `t.total 1.1841 s`, `t.total_live 1.5868 s`, Rust ACCEPT — so the live-pipeline plumbing itself is fine; the break is pipeline depth >= 2. |
| (f) | same as (e) with `--auth included-hash`, no `--pipeline`, out `/tmp/mv/hash/` | 1 | **PASS (expected live reject)** — `rep 1: live verifier REJECTED 0/4 (4 sub-batch(es) rejected: sub_00: system file: not a ligero-system/v1 or /v2 file; sub_01: system file: not a ligero-system/v1 or /v2 file; sub_02: system file:)`; `t.total 1.4763 s`, `t.total_live 2.0864 s`, validation `failed` (because of the live verdict); dumps written and `4/4 accepted cold from bytes by the Python file verifier` | Local fresh Rust `ligero-verify batch --dir /tmp/mv/hash/proofs/rep1 --system /tmp/mv/hash/proofs/system.bin --target-bits 128`: exit 0, `4 accepted, 0 rejected … batch ACCEPT … **system pinned (fp8-ada+hash)**; python agreement 4/4` (sys_id c4c4b403…, table digest c0e2f481…).  The live pod's pre-hash-relation binary cannot parse the hashed system — exactly the anticipated failure. |
| (g) | `… --relation fp8-ada bench-vu --zk --mode interactive --batch 16384 --total-vus 1024 --reps 1 --target -128 --device cuda --pipeline 2 …` (no `--verifier`) | 1 | **FAIL on a55b3fc** — identical `RuntimeError: Offset increment outside graph capture encountered unexpectedly.` (9 s) | **PASS with the fix**: exit 0 (11 s), Rust ACCEPT (`system pinned (fp8-ada)`).  `g_nozk` (same without `--zk`) also fails on a55b3fc and passes with the fix — the bug is not ZK-specific. |
| Rust on (e) dumps | `ligero-verify batch --dir /tmp/mv/bare/proofs/rep1 --system …/system.bin --target-bits 128` | 0 | ACCEPT 4/4, `system pinned (fp8-ada)`, batch bits 128.67 | on the fixed-tree (e) dumps and on the e1 dumps (unfixed tree, pipeline 1): both ACCEPT |
| Rust on (f) dumps | as above, `/tmp/mv/hash/proofs` | 0 | ACCEPT 4/4, `system pinned (fp8-ada+hash)` | |
| Rust on (g) dumps | as above, `/tmp/mv/local/proofs` (+ `/tmp/mv/local_nozk/proofs`) | 0 | ACCEPT 4/4, `system pinned (fp8-ada)` | |

## Break 1 — `--pipeline >= 2` crashes (hash-relation x hp2-host semantic conflict; fixed on `lane/merge-val` 538801e)

Symptom (a55b3fc, items (e) and (g), with or without `--zk`, with or without `--verifier`):

~~~
  File "/workspace/src/backends/direct/ligero/relchain.py", line 920, in bench_vu_rel
    R.prove_vus_many([data[lo_:hi_] for lo_, hi_ in warm],
  File "/workspace/src/backends/direct/ligero/relchain.py", line 283, in prove_vus_many
    proofs, wall = prove_many([starter(i) for i in range(len(batches))], self.device, depth=depth)
  File "/workspace/src/backends/direct/ligero/pipeline.py", line 356, in prove_many
    job.step()
  File "/workspace/src/backends/direct/ligero/pipeline.py", line 313, in step
    self.waitable = self.gen.send(None) if self.started else next(self.gen)
  File "/workspace/src/backends/direct/ligero/protocol.py", line 1289, in _prove_stages
    _graph_run(st, "commit_graph", commit_body, device)
  File "/workspace/src/backends/direct/ligero/protocol.py", line 1078, in _graph_run
    g.replay()
RuntimeError: Offset increment outside graph capture encountered unexpectedly.
~~~

Root cause (found by making `_graph_run` / `_tests_graph_run` print the exception they swallow — pod-local instrumentation only):

~~~
[MV-DEBUG] graph capture failed: RuntimeError('CUDA error: operation failed due to a previous error during capture ...
  File "/workspace/src/backends/direct/ligero/protocol.py", line 1149, in _tests_graph_run
    body()
  File "/workspace/src/backends/direct/ligero/protocol.py", line 1123, in body
    w, h, q, v = _tests_compute(sys, tb, cfg, x, st.coefs, st.U, st.W, None, st.pubmat, st.y16, layout, mr,
  File "/workspace/src/backends/direct/ligero/protocol.py", line 999, in _tests_compute
    cc = chain_coefs(sys, layout, rc, y16_pub)
  File "/workspace/src/backends/direct/ligero/chain.py", line 161, in chain_coefs
    link_fams = tabs["link_fams"].tolist()
RuntimeError: CUDA error: operation not permitted when stream is capturing
~~~

* `backends/direct/ligero/chain.py:161` `link_fams = tabs["link_fams"].tolist()` is from hash-relation commit **8c75847** (the extra
  linked families of the hashed relation): a device->host sync in `chain_coefs`.
* hp2-host's pipelined prover (`protocol.py:1140-1155 _tests_graph_run`, used by `pipeline.py prove_many` at depth >= 2) captures
  `_tests_compute` -> `chain_coefs` in a CUDA graph.  The sync invalidates the capture; `_tests_graph_run` swallows the exception
  (`except Exception: g = False`, `protocol.py:1150`) and falls back to eager — but torch's `capture_end` had already thrown *before*
  `capture_epilogue`, so the default CUDA generator is left in "capturing" state, and the next `commit_graph.replay()` of the other
  in-flight job (`protocol.py:1078`) raises the RNG error above.  Two lanes that were each green in isolation (hash-relation never
  pipelines; hp2-host never ran `chain_coefs` with `link_fams`) — no textual conflict, so the merge was silent.
* Fix (branch `lane/merge-val`, commit **538801e**, `chain.py` only, 3 lines): `_chain_tables` stores the Python list next to the
  tensor (`"link_fams_list": list(link_fams)`) and `chain_coefs` reads that — no device sync inside the capture.  Verified on the
  pod with the exact committed file: (g) zk pipeline 2 exit 0 + Rust ACCEPT; `g_nozk` pipeline 2 exit 0 + Rust ACCEPT; (e) zk
  pipeline 2 + LIVE verifier `ACCEPTED 4/4`, `t.total 0.4577 s` / `t.total_live 0.730 s`, Rust ACCEPT `system pinned (fp8-ada)`;
  `pytest -q backends/direct/ligero -k chain` on the fixed tree: `47 passed, 123 deselected` (a4).  Transcripts are unaffected
  (the list has the same values).
* Worth a follow-up regardless: both `except Exception` fallbacks in `_graph_run` / `_tests_graph_run` hide capture failures, and a
  failed capture leaves torch's RNG generator unusable — the fallback should at least log, and probably `torch.cuda.synchronize()` +
  re-check before going eager.

## Break 2 — privsel v3 differential (relmin-lookup post-branch pubsel commits under relmin-private's v3 units)

`pytest backends/direct/ligero/privsel/relation_test.py::test_differential_v1_v3` on a55b3fc (CPU test, 3000 units per relation):

~~~
AssertionError: bf16-hopper-v3 honest: v3 accepts != (claim == model) at [9, 24, 66, 81, 82]
AssertionError: bf16-ampere-v3 honest: v3 accepts != (claim == model) at [9, 24, 66, 81, 82]
AssertionError: fp8-hopper-v3 honest: v3 accepts != (claim == model) at [15, 27, 35, 108, 111]
AssertionError: fp8-ada-v3 honest: v3 accepts != (claim == model) at [15, 27, 35, 108, 111]
~~~

i.e. the v3 (private-operand) units **reject honest claims** (`ok3` False where the claim equals the model) at ~0.2 % of units.
Control on the pod (a3): the same test on relmin-private's own tip **9a42e39** (git-archived to `/workspace/src-rp`, same venv):
`1 failed, 3 passed` — bf16-hopper-v3 / bf16-ampere-v3 / fp8-hopper-v3 pass, **fp8-ada-v3 fails there too**
(`fp8-ada-v3 honest: v3 accepts != (claim == model) at [874]`).  So:

* three of the four failures are merge-induced.  `privsel/` is byte-identical between 9a42e39 and a55b3fc; what changed underneath
  it is `pubsel/relation.py` + `pubsel/hints.py` from relmin-lookup commits that post-date relmin-private's branch point
  (merge-base 0055c41): **9a869b3** (v2 zero-sum completeness), **6ef1d3d** (v2 last group without fraction bits, epilogue picked from
  the sum's bits), d4ef0f9, **c7d32e0** (`public_vectors_v2` extra shifts in one broadcast).  `privsel/relation.py:46` imports
  `ACC_FRAC, CMP_BITS, LIMB, Y_PACK_BITS, Plan, _bit_exprs, _clamp_table, _hint, _norm_window, …` and `privsel/hints.py:9`
  `ACC_FRAC, LIMB, Plan, aligned_product, operand_decode_int, plan` from `pubsel.relation`, and `relations.py:353` builds
  `fp8-ada-v3 = _v3_of(FP8_ADA_V2_RELATION, …)` — v3 inherits v2's plan / windows / last-group layout, which 6ef1d3d changed.
  Likely hunk: `pubsel/relation.py` as of 6ef1d3d (the fraction-bit-free last group + epilogue) consumed by `privsel/relation.py`'s
  digit / normalisation windows written against the pre-6ef1d3d v2.  Owner: relmin-private (re-derive the v3 hull intervals /
  windows on the merged v2), or pin v3 to the v2 plan it was built on.
* the fp8-ada-v3 failure at 1 of 3000 units is **pre-existing on 9a42e39** (relmin-private's report lists its own 3000-unit
  differential and the fp8-ada-v3 GPU gate as RUNNING at checkpoint time — not yet green there either).
* The pinned systems' `sys_id`s did not change in the merge (Rust `system pinned` for fp8-ada/bf16-hopper), but the v3 pins were not
  checked by this lane.

## (d) fp8-ada-v3 GPU gate — FAIL in the negatives phase (honest 25/25 accepted)

`--relation fp8-ada-v3 gate-vu --device cuda --vus 2048 --batch 4096 --instance-procs 8 --instances-cache …` (09:49-10:01Z, 710 s):
census `rows 1806, hint 1491, bit 169, inv 71, prod 23, pin 22, sel 30; linear 130, quadratic 2542`; the first sub-batch took ~11 min
at 100 % of one core (the v3 hint program's compile — relmin-private's report quotes ~25 min per v3 relation for the whole gate), then
the remaining 24 honest sub-batches at 0.02 s prover each: **25/25 honest accepted, including the l=512 tail**.  The negatives phase
then died on its first proof:

~~~
  File "/workspace/src/backends/direct/ligero/relchain.py", line 780, in gate_vu_rel
  File "/workspace/src/backends/direct/ligero/relchain.py", line 541, in negatives
  File "/workspace/src/backends/direct/ligero/relchain.py", line 240, in prove_vus
  File "/workspace/src/backends/direct/ligero/pipeline.py", line 293, in run_to_completion
  File "/workspace/src/backends/direct/ligero/protocol.py", line 1233, in _prove_stages
  File "/workspace/src/backends/direct/ligero/relchain.py", line 249, in hints_fn
  File "/workspace/src/backends/direct/ligero/relations.py", line 316, in _v3_hints
  File "/workspace/src/backends/direct/ligero/privsel/hints.py", line 197, in hints_v3
  File "/workspace/src/backends/direct/ligero/privsel/hints.py", line 223, in run
  File "/workspace/venv312/lib/python3.12/site-packages/torch/cuda/graphs.py", line 88, in replay
RuntimeError: Offset increment outside graph capture encountered unexpectedly.
~~~

Same mechanism as Break 1: some CUDA-graph capture failed and was swallowed between the last honest sub-batch and the first negative
(candidates: the `_tests_graph_run` re-capture for the tail layout — `protocol.py:1132` "the pinned buffer moved (grown): re-capture" —
tripping over `chain.py:161`, or a capture inside `privsel/hints.py` itself), leaving torch's default CUDA generator in capture state;
the v3 hint program is itself a replayed CUDA graph (`privsel/hints.py:223`), so it is the first thing to raise.  fp8-ada / bf16-hopper
(b) do not replay a hint graph and went through their negatives fine on the same unfixed tree.  This run used the UNFIXED `chain.py`;
I could not afford the 11-min compile to re-run it with 538801e.  **Next pod: re-run (d) on `lane/merge-val` with the two
`except Exception` fallbacks in `protocol.py` printing their exception** (the pod-local instrumentation from Break 1) — if it still
fails, the swallowed capture is in privsel's hint graph and belongs to relmin-private.  The v3 negatives are therefore untested by this
lane; the honest path (prover + Python verifier, 25 sub-batches) works on the GPU.

## What passed cleanly (no action)

hp2-host staged prover at pipeline depth 1 (e1) and depth 2 with the fix; enc-hopper encode_simt v3 + `coefs_out` (ZK runs (e)/(g)
bit-verified by Rust); hash-relation (`--auth included-hash` gate (c) 0 failures incl. 86 negatives, hashed bench (f) verified by the
fresh Rust with `system pinned (fp8-ada+hash)`); live-pipeline (`--pipeline 2 --verifier tcp://` together: ACCEPTED 4/4 with the fix;
`--pipeline 1 --verifier` ACCEPTED 4/4 unfixed); fp4-fast: `backends/direct/ligero/fp4` tests pass in (a2) (no fp4 GPU gate was in
scope — the 4090 is not sm_120); relmin-lookup v2: `pubsel/` tests pass in (a2).

## Pod accounting

`uwovuyy842njoj` created 09:39:01Z, `research pods terminate` 10:06Z (`pods list` confirms it is gone): 27 pod-minutes at $0.74/h
≈ **$0.33** (budget $1.50).  No other pod touched; nothing pushed to the data store.

## Files

* `~/.research/notes/lanes/merge-val/evidence/` — `commands.log` (every command + exit + elapsed), `a.log` / `a2.log` (pytest -x /
  full), `a3.log` (privsel differential on 9a42e39), `a4_chain.log`, `b1.log`, `b2.log`, `c.log`, `d.log`, `e.log` / `g.log`
  (fixed-tree re-runs), `e1.log`, `f.log`, `g_nozk.log`, `rust_*.log`, `bootstrap.log`, `bootstrap.sh`, `items.sh`.
* Repo: worktree `~/projects/verity-main-wt/merge-val` on branch `lane/merge-val` = main a55b3fc + **538801e** (chain.py fix).  main
  untouched.  No .md written into the repo.
