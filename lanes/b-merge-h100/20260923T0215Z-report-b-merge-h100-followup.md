CHECKPOINT 0b40ae8a (05:54Z) [superseded] closed by coordinator 2026-09-25 05:55Z for the cloud switch-over: no sign of life >24 h; branch lane/b-merge-h100 pushed to origin; uncommitted work (if any) saved in evidence/uncommitted-0554Z*
# Lane b-merge-h100 -- follow-up: merge main into lane/b-merge-h100, D10 for every relation, validated

Date: 2026-09-23 01:35Z .. 02:15Z. Worktree `~/projects/verity-main-wt/b-merge-h100`, branch `lane/b-merge-h100`.
HEAD **53f90ff** (`git merge-base --is-ancestor main HEAD` holds: main ffc8287 fast-forwards to it). Not merged into main.

## 1. Merge

* **5caa7df** = `git merge main` at main **710e851** (b-batch-bound 1dcba68, tcgen05 e059f14, ligero-verify-relations a5d018e,
  the two tables.py/target.py coordinator commits) + this lane's D10 / memory_bytes changes, in the merge commit itself.
* **53f90ff** = `git merge --no-ff main` at main **ffc8287** (store: labels-backup/v1 kind, 2 lines in
  `tools/research/src/research/store/kinds.py`) -- main moved while the pod ran; without this second merge main could not
  fast-forward. No conflicts; the laptop `tools/research/tests` + `backends/numerical/tests` were re-run after it (below).
* Rust (`backends/ligero-verify`): **no conflicts**, auto-merged (src/format.rs, main.rs, verify.rs, tests/fixture.rs, new
  src/relation.rs + tests/relations.rs + fixtures); `git merge-tree --write-tree HEAD main` clean afterwards too.
* The three one-hunk union conflicts, both sides kept:
  1. `backends/direct/ligero/run.py`: bench-vu `--target-bits` (b-batch-bound) **and** gate/bench `--instance-procs` /
     `--instances-cache` with the non-bf16 `--row-negatives` help (generic runner).
  2. `backends/direct/ligero/serialize.py`: verify `--relation` help in the relations.py wording **and** the `verify-batch`
     subparser (`--dir/--device/--target-bits/--json`; dispatch to `cmd_verify_batch` was outside the hunk and auto-merged, as
     were `verify_batch_dir` / `own_coins`).
  3. `backends/direct/ligero/vu.py`: dump manifest `set` with `dump_reps` / `tier_n` / `ids_recycled_mod_tier_n` /
     `authentication` **and** `target_bits = ... ; batch = None` (cfgs_seen / batch verdict / achieved_log2 from the batch
     were outside the hunk and auto-merged).
* No merge markers (`rg -l '^<<<<<<< '` empty), `git status --short` clean, no `.md` added by this lane.

## 2. D10 for every relation (`backends/direct/ligero/relchain.py`)

b-batch-bound applied the batch verdict only in `vu.ChainRunner` / `vu.bench_vu` (Ampere BF16). Now:

* `RelationChainRunner.batch_bound(cfgs, n_proofs_claimed, target_bits, names)` and `.verify_batch(items, ...)` -- the same
  rule (`protocol.batch_bound`: union bound of the verifier's OWN per-proof bounds <= 2^-target, every claimed `n_proofs` == N)
  and the same reason strings as `ChainRunner` / `ligero-verify batch`.
* `bench_vu_rel`: `--target-bits` read (default 128), `cfgs_seen` per rep, `batch = R.batch_bound(...)` per recorded rep inside
  the verifier time, `assert batch["accepted"]`; `security.achieved_log2` / `achieved_bits` now come from the batch verdict
  (asserted equal to `soundness(cfg, n_proofs)["total_log2"]` to 1e-6), `security.verifier_target_bits`, and
  `validation.evidence.batch` + `detail` "...; batch <reason>" as in vu.py.
* The cold dump self-check `_verify_dumps` additionally runs the per-rep batch verdict on the dumped STATEMENTS' configs and
  `n_proofs` (what `serialize.verify_batch_dir` / `ligero-verify batch` recompute on the same tree); `evidence.dumps.batch`
  / `batch_accepted`; a rejected batch fails the run.
* `serialize.verify_batch_dir` (b-batch-bound) already dispatches through `_runner(device, st)` to `RelationChainRunner` for
  v4 statements, so `verify-batch` works on non-Ampere trees without change (proved on the pod, below).
* `packages/verity/src/verity/verification/target.py`: `H100_BF16_PEAK` (BF16_HOPPER's NativePeak) has `memory_bytes=80 * 2**30`.

## 3. Laptop

* `uv sync -q`; `uv run -q pytest tests packages/verity/tests tools/research/tests backends/numerical/tests -q` at 5caa7df:
  **1232 passed, 15 skipped** (134 s).
* After 53f90ff: `tools/research/tests backends/numerical/tests` -> first run **1 failed, 777 passed, 9 skipped**; two
  immediate re-runs (one with `-x`) **778 passed, 9 skipped** both times. The failing test's name was not captured (the
  summary line was tailed); it did not reproduce -- a flake in a suite untouched by 53f90ff (2 lines in store/kinds.py).
  Coordinator: run the suite once more before the fast-forward if you want a third clean data point.
* Rust: `cd backends/ligero-verify && CARGO_TARGET_DIR=/tmp/lvr-bm cargo test --release -q`: **17 + 7 + 6 = 30 passed**, 0 failed.
* Renderer at merged HEAD (`verity_numerical.bench.tables --root ~/.research/store --format md`): both Hopper rows render
  (BF16 sm90.mma bf16-hopper-mma-draft, E4M3 sm90.wgmma fp8-hopper-wgmma-draft) with measured peaks 722 T / 1125 T; the BF16
  Hopper B-Ligero cell is populated by art:799bddfe (the coordinator's verification label), the FP8 Hopper cell is not yet.

## 4. Pod validation (`vy-bm-val`, RunPod 1nzit4kcj3qeab, RTX 4090 24 GB SECURE, AMD EPYC 7642 host, $0.74/h)

Created 01:38:13Z, **terminated 02:04:46Z by this lane** (`runpod.py terminate` -> "terminated"; not in `runpod.py list`):
**26.6 min, ~$0.33**. Laptop watchdog 1.0 h (killed after termination). machines.toml has the `vy-bm-val` entry + TERMINATED line.
No other pod touched.

* Shipping: the pod's SSH ingress ran at ~60 KB/s (laptop upload to Cloudflare 4 MB/s; 94 MB `git archive` would have taken
  ~25 min), so the `research run --source .` upload was killed and the tree went `git archive HEAD | gzip -1` (32 MB) ->
  R2 `verity-dev:scratch/b-merge-h100/src-5caa7df.tar.gz` (store's own `S3Remote.put`) -> pod (`S3Remote.get` with a 1 h
  read-only credential from `research data mint-credential --prefix scratch/b-merge-h100/`; sha256 32f3b3c1 matched) into
  `/workspace/research/src/5caa7df.../` + `.complete`; the harness then found the source slot complete and ran normally, so
  the attempts carry tree_sha 5caa7df. Same route for the dump tree (`scratch/b-merge-h100/dumps-831f.tar.gz`, 74 MB).
  **Two scratch objects (~106 MB) remain in the bucket under `scratch/b-merge-h100/`** (S3Remote has no delete) -- coordinator
  may remove them.
* Bootstrap `r20260923-015337-d6ba` (BOOTSTRAP_OK, 5 min: venv312 torch 2.6.0+cu124 / Triton 3.2.0 / cupy-cuda12x / blake3 /
  pytest, rustc 1.98.1 `ligero-verify` sha256 2a8825b5, bench-instances/v1). A first launch `r20260923-015003-e396` failed
  instantly (`$RESEARCH_RUN_DIR` is not expanded in the argv; re-launched with `--id` and the literal path).
* Validate `r20260923-015910-b89f` (VALIDATE_OK, 4.7 min), at tree 5caa7df:
  * `pytest backends/direct/ligero -q` (torch present): **43 passed** (168 s).
  * Gates, 64 VUs: **bf16-ampere** OK (52/52 negatives, 252/252 mutations rejected); **bf16-hopper** OK (2 honest sub-batches,
    87 negatives, 0 failures); **fp8-hopper** OK (1 honest, 92 negatives, 0 failures); **fp8-ada** OK (1 honest, 92 negatives,
    0 failures).
  * **verify-batch on a non-Ampere tree works.** `python -m backends.direct.ligero.serialize verify-batch --dir
    dumps/proofs/rep1 --device cuda --target-bits 128` on art:831f1f9a20262ea2781f46ab82f9f5fa96e610db0163d07319592bf5514f7f1b
    (fp8-hopper interactive ZK, rep1 = 13 sub-batch proofs, `ligero-statement/v4`, own coins): **13/13 ACCEPT, batch ACCEPT
    "all 13 sub-batches accepted; union bound 2^-128.32 <= 2^-128"**, per-proof 2^-132.02, n_proofs=13 each, 5.2 s (3.9 s of
    it the first proof's compile). Note: the subcommand lives in `serialize.py` (`run.py` has no `verify-batch`).
  * Rust `ligero-verify batch --system system.bin --dir rep1 --jobs 4 --threads 8 --target-bits 128` on the same tree:
    **13/13 ACCEPT (13 against their own coins), batch ACCEPT, batch bits 128.319381, system pinned (fp8-hopper), python
    agreement 13/13**; verify sum 3.88 s, wall 1.14 s. Both verdict JSONs at `/tmp/bmval/verify_batch_{python,rust}.json`.
  These are the producer's own self-checks on a 4090 (not the `verify` lane's independent judgement).
* Records-only pulls of the two attempts into the laptop store (`research data pull --from vy-bm-val`); laptop fetched from
  the pod: < 1 MB (records + two JSONs). Laptop upload to R2: 106 MB; nothing large downloaded to the laptop.

## 5. Decisions for the coordinator

1. Merged main **twice** (710e851 as asked, then ffc8287 which landed at 01:38Z) so the branch fast-forwards now; 53f90ff is a
   trivial 2-line union in store/kinds.py, validated on the laptop only (the pod ran 5caa7df; backends/direct/ligero unchanged).
2. D10 in the generic runner changes `relchain.bench_vu_rel`'s `security.achieved_log2` source (batch verdict instead of
   `soundness()` directly; asserted equal) and adds `achieved_bits` / `verifier_target_bits` / `evidence.batch` -- the six H100
   rows of 01fc64f predate this and do not carry those fields (their numbers are unchanged).
3. `--target-bits` is now also honoured by `--relation R bench-vu`; `fp8/tool.py`'s parser was not changed (target-bits is not a
   key param there, same as vu.py's tool declaration on main).
4. Pod source shipping via the R2 scratch prefix was a workaround for this pod's SSH ingress; the harness's `--source` path
   itself is untouched.
5. One laptop test flake after 53f90ff (name not captured; two clean re-runs) -- see §3.

Scripts and logs: `/tmp/bmval/` (bootstrap.sh, validate.sh, validate_stdout.log, verify_batch_*.json, create.json).
