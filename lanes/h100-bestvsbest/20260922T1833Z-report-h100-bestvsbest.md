---
id: r21-bestvsbest/h100-bestvsbest/20260922T1833Z-report-h100-bestvsbest
campaign: r21-bestvsbest
lane: h100-bestvsbest
kind: report
status: closed
repo: verity-main@b48dfbb
branch: lane/h100-bestvsbest (off main 72e8c7a; commits c013f6f, b48dfbb; not pushed)
machine: vy-h100 (RunPod 4cp9bexmjfrpum, H100 80GB HBM3 SXM, EPYC 9554 224 threads, driver 570.211.01 / CUDA 12.8)
decision: r20 Q2 (same-card best-vs-best, B=4096 K=1536 2^-128)
---

# h100-bestvsbest: A (a-gpu2 GKR GPU) vs B-Ligero (b-zk-fix) on one H100, every proof independently verified

## 1. Answer to Q2

On one H100, the campaign's frozen `bench-instances/v1` (manifest `9128d2b6…`), B = 4096 VUs, K = 1536, target 2^-128,
median of 3 recorded reps after a warm-up, every proof checked by the independent Rust verifier on the same pod:

| | prover s (median/3) | Rust verifier s | proof MB | class |
|---|---|---|---|---|
| **B-Ligero non-ZK interactive** (control) | **1.034** | 2.606 (25 sub-batch proofs, sequential, 16 thr) | 110.8 | NON_ZK_PROOF_DIAGNOSTIC |
| **B-Ligero ZK interactive** | **1.117** | 2.629 | 122.4 | **COMPLETE_ZK_BACKEND** |
| **B-Ligero ZK Fiat-Shamir** (t = 288, D = 7) | **1.194** | 3.346 | 165.3 | **COMPLETE_HVZK_BACKEND** |
| A a-gpu2 v1 checker, packed + graphed | 1.770 | 0.800 (one proof, 16 thr) | 33.9 | NON_ZK_PROOF_DIAGNOSTIC |
| **A a-gpu2 checker-v2 (limb epilogue), packed + graphed** | **1.336** | 1.189 | 21.1 | NON_ZK_PROOF_DIAGNOSTIC |

**Prover, same card, best vs best: A v2 / B non-ZK = 1.336 / 1.034 = 1.29x** (A v1: 1.71x). B stays ahead even with a
complete privacy claim: A v2 (non-ZK, the best A has) is 1.20x slower than B's malicious-verifier-ZK interactive prover and
1.12x slower than B's transferable Fiat-Shamir HVZK prover. B's ZK costs +8.0% (interactive) / +15.4% (FS) over its own
non-ZK control on this card (b-zk-fix measured +2% / +9.8% on the L40S, without `--exclusive`; the larger relative ZK
cost here was not isolated to a phase -- the ZK-specific work simply shrank less than the encode did from L40S to H100).

Against the prior numbers: gate4's same-card pair was **2.386 vs 5.016 s (2.10x)** with the older provers; both moved --
B 2.386 -> 1.034 (2.31x, the b-zk-fix prover) and A 5.016 -> 1.770 (v1, 2.83x) -> 1.336 (v2, 3.76x, the a-gpu2 prover) --
and the gap closed from 2.10x to 1.29x. The cross-card **1.366 (L40S) vs 1.875 (H100)** ratio of 1.37x was not far off
the truth: B gains 1.32x from L40S to H100 (1.366 -> 1.034), and A's v1 here (1.770) is 5.6% under a-protocol-diff's
1.875 on the same card (fresh Triton cache under `--scratch triton`, `--exclusive`, no other tenant).

**End-to-end at 0 ms, prover + the independent Rust verifier, flips the order**: A v2 2.52 s and A v1 2.57 s vs
B 3.64 / 3.75 / 4.54 s, because `ligero-verify` (CPU) is 0.104-0.134 s per sub-batch proof x 25 proofs, invoked
sequentially, while `verity-gkr-verify` checks A's single 4096-VU proof in 0.80 s (v1) / 1.19 s (v2). Two things to weigh
before reading that as an A win: (i) the 25 sub-batch verifications are independent and the pod has 224 threads --
run in parallel they would be ~0.13 s of wall, but that was not measured here, so the table carries the sequential sum;
(ii) with the live Python GPU verifier that B actually runs (D7), B's e2e is 1.72 / 1.79 / 1.95 s vs A's 1.97 (v2) /
2.28 (v1) with its Python verifier. Prover-side, Q2 closes for B; e2e depends on how the 25 verifications are scheduled.

Replication: the three B rows were re-run 18 minutes later from commit b48dfbb (identical prover code; the re-run exists
because the first three fingerprints carried `commit: null`, see §5): 1.054 / 1.130 / 1.204 s, i.e. +1.9% / +1.1% / +0.9%,
75/75 Rust accepts each. All eight `bench-result/v1` artifacts are in the laptop store and labelled (§4).

## 2. The table

`prover s` = `prove_wall`, median of 3 recorded reps (A: 1 full warm-up rep excluded, it carries the Triton compile;
B: one warm-up sub-batch excluded). `Rust verifier s` = `verify_wall`: A = `verity-gkr-verify verify --threads 16` on the
rep's proof, median over the 3 reps; B = `ligero-verify verify --threads 16` on each of the rep's 25 sub-batch proofs
(`--coins` = the runner's step-0 coins in interactive mode), summed per rep, median over reps. `Py verifier s` = the
prover-side Python verifier (shares code with the prover; A: `gpu.prover.verify`; B: live per sub-batch). `e2e@0ms` =
`prove_wall + verify_wall` (Rust). `depth` = sequential transcript depth (A: GKR/LogUp rounds; B: 3 = coin commitment +
2 rounds interactive, 1 = Fiat-Shamir). `soundness` = the accountant's achieved bits (B: live `soundness()`, union over
25 proofs; A: recorded 127.7 from `security.accounting.account_candidate_a`, no live accountant in the GPU prover).

| # | design | mode | prover s median/3 [reps] | Rust verifier s (which) | Py verifier s | proof MB | depth | e2e@0ms s | soundness | label | run id | art id |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a | B-Ligero (b-zk-fix, `backends/direct/ligero`, v1 checker) | interactive, non-ZK | **1.034** [1.030, 1.034, 1.054] | 2.606 (`ligero-verify`, 25 x ~0.104 s, 16 thr, 75/75) | 0.686 | 110.77 | 3 | 3.641 | 2^-128.25 (stat., union/25, t=196, D=6) | NON_ZK_PROOF_DIAGNOSTIC | r20260922-180223-cda6 | art:dc0b4706b294465380d49099a86f6ab4ae594b52473f45a02367034d1f8e9f67 |
| b | B-Ligero | interactive, `--zk` | **1.117** [1.112, 1.117, 1.124] | 2.629 (`ligero-verify` + `--coins`, 75/75) | 0.670 | 122.44 | 3 | 3.747 | 2^-128.05 (stat., HM96 coin commitment, t=197, D=6, t_pad=256) | COMPLETE_ZK_BACKEND | r20260922-180414-0585 | art:f2b7b1701884b7fcc64e11cbabb67291ded4307b88c2551a1a8814aa494a402d |
| c | B-Ligero | fiat-shamir, `--zk` | **1.194** [1.186, 1.194, 1.195] | 3.346 (`ligero-verify`, 25 x ~0.134 s, 75/75) | 0.757 | 165.32 | 1 | 4.539 | 2^-128.04 (2^60 x eps, PROM, t=288, D=7, t_pad=512) | COMPLETE_HVZK_BACKEND | r20260922-180748-ba52 | art:651ac482b87fb1296d4b1b154f8e09bb1f05856428ea9c2643de2e892a4804af |
| d | A a-gpu2 (`backends/gkr/gpu`), v1 checker, `bb/pos4096` | non-interactive SHA-256 FS, non-ZK, packed + graphed, babybear6 | 1.770 [1.729, 1.770, 1.804] | 0.800 (`verity-gkr-verify`, 1 proof, 16 thr, 3/3) | 0.506 | 33.87 | 438 | 2.570 | 2^-127.7 (recorded; Ligero k=4096 n=16384 t=192) | NON_ZK_PROOF_DIAGNOSTIC | r20260922-180844-e013 | art:1d00e1331249eb294827feb4314785aa2fe5a24dd515a20f3cd263a6e9829d46 |
| e | A a-gpu2, checker-v2 (checker-min gadgets, limb epilogue), `v2l/pos4096` | same, packed + graphed | **1.336** [1.325, 1.336, 1.355] | 1.189 (`verity-gkr-verify`, 3/3) | 0.630 | 21.13 | 328 | 2.524 | 2^-127.7 (recorded) | NON_ZK_PROOF_DIAGNOSTIC | r20260922-181404-e39d | art:8b898a8a1eae5b76af1ea0ff74baa1195401a9dff9754b7651f7a0eb3fa3ed93 |
| a' | B-Ligero (re-run, b48dfbb) | interactive, non-ZK | 1.054 [1.052, 1.054, 1.065] | 2.650 (75/75) | 0.697 | 110.77 | 3 | 3.704 | 2^-128.25 | NON_ZK_PROOF_DIAGNOSTIC | r20260922-182131-5066 | art:0e871445e523a17a3ce1479c982b90e432053154b5589043896dff48847e3c17 |
| b' | B-Ligero (re-run) | interactive, `--zk` | 1.130 [1.124, 1.130, 1.133] | 2.644 (75/75) | 0.668 | 122.44 | 3 | 3.774 | 2^-128.05 | COMPLETE_ZK_BACKEND | r20260922-182217-284a | art:86aabd913a7f3255cf5d952cb6dba950eb9dc08295759ad465b9d169c934668a |
| c' | B-Ligero (re-run) | fiat-shamir, `--zk` | 1.204 [1.200, 1.204, 1.209] | 3.349 (75/75) | 0.785 | 165.32 | 1 | 4.554 | 2^-128.04 | COMPLETE_HVZK_BACKEND | r20260922-182302-3cb0 | art:b98c1f10dea90c2f371047ce208ceebd6a2e24f9cbe96901fbab0a7c44bda125 |

Per-VU: B 0.252 ms/VU (non-ZK), 0.273 (ZK int), 0.291 (ZK FS); A 0.432 (v1), 0.326 (v2). Peak device memory: B 4.0 /
5.4 / 5.4 GiB; A 44.6 GiB (v1) / 18.5 GiB (v2). A's phase split (median rep): v1 lookup 0.42 + arith 0.62 + open 0.56 +
commit 0.10; v2 lookup 0.53 + arith 0.24 + open 0.51 + commit 0.04 -- v2's limb epilogue takes 0.38 s out of arith and
0.06 s out of the Ligero commit, adds 0.11 s of LogUp, and its Rust verification is 0.39 s slower than v1's (not
isolated here; the v2 proof is smaller and shallower, so the extra verifier time sits in the checker-min gadget/lookup
checks, not in openings).

Ratios (prover): A v2 / B non-ZK 1.29; A v1 / B non-ZK 1.71; A v2 / B ZK-int 1.20; A v2 / B ZK-FS 1.12; A v1 / B ZK-int
1.58; A v1 / B ZK-FS 1.48. gate4 (same card, older provers): 5.016 / 2.386 = 2.10. Cross-card (a-protocol-diff H100 vs
b-zk-fix L40S): 1.875 / 1.366 = 1.37.

## 3. What ran (provenance)

Pod `vy-h100` was fresh (runpod/pytorch 2.4 cu12.4 devel) at 17:52Z. Everything below is a `research run --on vy-h100
--project verity --campaign r21-bestvsbest --source <worktree>` attempt in the store; the laptop never ran anything heavy.

**Bootstrap** (`r20260922-175324-8307`, 130.6 s wall, then idempotent re-run `r20260922-182103-69ec`, 14.4 s,
`BOOTSTRAP_OK`): `uv` -> Python 3.12.14 -> `/workspace/venv312` with **torch 2.6.0+cu124, Triton 3.2.0, numpy 2.5.3,
cupy-cuda12x, blake3 1.0.9** (exactly gate4's versions, installed without incident: torch in 18 s); `rustup` stable
(rustc 1.98.1); `cargo build --release` of `backends/gkr/verifier` -> `/workspace/bin/verity-gkr-verify` and
`backends/ligero-verify` -> `/workspace/bin/ligero-verify`; `verity_numerical.bench.instances build` ->
`/workspace/bench-instances/v1` (61.3 s, 64 procs, manifest sha256 `9128d2b6…`, `vu_hawkeye_disagreements: 0`, the same
manifest gate4 built); `gpu.bb_export` -> `/workspace/bb/pos4096` (A v1) and `gpu.v2.export` -> `/workspace/v2l/pos4096`
(A checker-v2), 48 procs each in parallel. The first attempt reported `rc=1` only because its final check ran the two
verifiers with `--help`, which both exit 2 by design; every artifact it built was used by rows a-e. The re-run rebuilt the
two verifier crates from the b48dfbb tree (crates unchanged since 72e8c7a: `git diff 72e8c7a..b48dfbb --
backends/gkr/verifier backends/ligero-verify` is empty), so `ligero-verify`'s sha256 differs between rows a-c
(`ff52539c…`, built from the 72e8c7a tree) and a'-c' (`22fefa0f…`); `verity-gkr-verify` used by d, e is `ee832e85…`.

**Tool declarations** (commit c013f6f): `backends/gkr/gpu/tool.py` -> `A_GPU_PROVE = Tool(name="a_gpu_prove", version="1",
closure backends/gkr/gpu/** + backends/gkr/packed/** + backends/gkr/bench_result.py + packages/verity/src/verity/**;
key_params dir (the exported instance, a param_artifact), vus (= batch), checker, path, field, clear; key_conditions
hw.family; caches triton; produces bench-result/v1, run-files/v1)`, registered in
`tools/research/src/research/store/tools_registry.py`;
`backends/direct/ligero/tool.py` (`bench_vu`) already keyed `mode`, `zk`, `batch`, `total_vus`, `target` and now also
parses `--dump-dir`, `--verifier`, `--threads`. Neither prover wrote `result.json` in the campaign schema with an
independent verification, so two thin wrappers do it without touching prover internals:

* `backends/gkr/bench_result.py DIR --vus 4096 --checker v1|v2 --path graphed|packed|torch --reps 3 --warmup 1 --verifier
  /workspace/bin/verity-gkr-verify --threads 16` -- runs `gpu.run.prove_once` warm-up + reps, dumps every rep's proof to
  `$RESEARCH_RUN_DIR/proofs/rep<i>.bin`, runs `verity-gkr-verify verify --dir DIR --proof … --threads 16 --json`, writes
  `$RESEARCH_RUN_DIR/result.json` (`research/result/v0.1`, kind `bench-result/v1`, measurements prove_wall/min/max,
  verify_wall, verify_python_wall, verifier_threads, proof_bytes, depth, soundness_bits, e2e_0ms, proofs_verified_independent,
  peak_device_bytes, split_*; `workload_fingerprint` with candidate, commit, protocol, mode, zk, proof_class, checker, path,
  field, batch, K, steps, export manifest, security, hardware, software, verifier name/path/sha256/threads).
* `backends/direct/ligero/bench_result.py bench-vu [--zk] --mode interactive|fiat-shamir --batch 16384 --total-vus 4096
  --reps 3 --root /workspace/bench-instances/v1 --device cuda --verifier /workspace/bin/ligero-verify --threads 16` -- runs
  `backends.direct.ligero.run bench-vu` with a new `--dump-dir` (added to `run.py`/`vu.py`: writes `system.bin`,
  `manifest.json` and per-rep, per-sub-batch `.stmt/.proof/.coins`), then `ligero-verify verify --system … --statement …
  --proof … --threads 16 [--coins …]` on all 75 proofs, same `result.json` shape (`depth` = `rounds.sequential_depth`,
  `soundness_bits` from the live accountant).

**Run commands** (rows a-c from the laptop shell, d-e via `/tmp/h100bvb/drive.sh`, a'-c' via `drive2.sh`; each
`--exclusive`, `--scratch triton` (fresh `TRITON_CACHE_DIR` per reuse_key -- the a-kernel-a100 F1 lesson), `--require-result`,
`--tool bench_vu|a_gpu_prove`, `--source .` = the clean worktree at c013f6f (a-d) / b48dfbb (e, a'-c')):

~~~
uv run research run --on vy-h100 --project verity --campaign r21-bestvsbest --scratch triton --source . --exclusive \
  --require-result --tool bench_vu --stage b_zk_fiat_shamir --env PYTHONPATH=packages/verity/src:backends/numerical/python:. -- \
  /workspace/venv312/bin/python backends/direct/ligero/bench_result.py bench-vu --zk --mode fiat-shamir --batch 16384 \
  --total-vus 4096 --reps 3 --root /workspace/bench-instances/v1 --device cuda --verifier /workspace/bin/ligero-verify --threads 16
uv run research run … --tool a_gpu_prove --stage a_v2_graphed --env PYTHONPATH=backends/gkr:packages/verity/src:backends/numerical/python:. -- \
  /workspace/venv312/bin/python backends/gkr/bench_result.py /workspace/v2l/pos4096 --vus 4096 --checker v2 --path graphed \
  --reps 3 --warmup 1 --device cuda --verifier /workspace/bin/verity-gkr-verify --threads 16
~~~

(`--path graphed` = packed kernels + CUDA graphs, i.e. neither `VERITY_GPU_TORCH_ONLY` nor `VERITY_GPU_NO_GRAPHS` set.)
Pulls: `research data pull --from vy-h100 <run> --project verity` for all ten attempts; each lands the attempt record, the
`bench-result/v1` artifact (result.json as manifest meta) and a `run-files/v1` tree.

## 4. The store: labels and selects

Every `bench-result/v1` artifact above carries, `--by h100-bestvsbest --ref <its run id>`: `proof_class`,
`independently_verified=true` (the ref is the run whose `stdout.log` / `verify/` dir holds the per-proof Rust verdicts and
whose result records `proofs_verified_independent = proofs_total`), `candidate` (`A` | `B-Ligero`), `hardware=h100`, `mode`,
`zk`, `campaign=r21-bestvsbest`. Checked selects (laptop store, `~/.research/store`):

~~~
research data select --kind bench-result/v1 --label candidate=B-Ligero        # 6 rows: a b c a' b' c'
research data select --kind bench-result/v1 --label candidate=A               # 2 rows: d e
research data select --kind bench-result/v1 --label proof_class=COMPLETE_ZK_BACKEND   # b b'
research data select --kind bench-result/v1 --label hardware=h100             # 8 rows
research data select --kind bench-result/v1 --tool a_gpu_prove                # d e   (derivation-side, no label needed)
research data select --kind bench-result/v1 --tool bench_vu --label zk=true   # b c b' c'
research data select --kind bench-result/v1 --where meta.workload_fingerprint.proof_class=COMPLETE_HVZK_BACKEND --label candidate=B-Ligero   # c c'
~~~

Store finding: `research data select` takes **one** `--label k=v` (argparse keeps the last; the README's `[--label k=v]`
is singular) -- `--label proof_class=… --label candidate=…` silently returns the candidate rows only. Conjunctions work via
`--where meta.workload_fingerprint.<key>=<value>` plus one `--label`, or `--tool`. Worth an `action="append"` in
`store/cli.py` later; not changed here (out of scope for a clean `--source` tree).

## 5. Caveats, and what was not run

* **Fingerprint `commit` is null in rows a-d.** `_git_commit()` runs in the shipped `git archive` tree, which has no
  `.git`; b48dfbb adds `source_commit()` (reads the `research/src/<sha>/` path or `RESEARCH_SOURCE_COMMIT`), so rows e and
  a'-c' carry `commit: b48dfbb…`. The attempt records always had it (`source.commit`, `dirty: false`) -- provenance is
  intact, only the in-artifact fingerprint was incomplete; a'-c' exist so that every B claim also has a complete
  fingerprint. Row d (A v1) was not re-run; its prover code is byte-identical at c013f6f and b48dfbb.
* **B interactive proofs and the Rust verifier.** `ligero-verify` is handed the runner's step-0 coins (`--coins`) and checks
  the transcript against them; that is a faithful independent recomputation of the verifier's checks, not a live
  interaction. The live verifier for rows a, b, a', b' is the Python one (D7), which ran on every sub-batch of every rep
  (`Py verifier s`). Fiat-Shamir proofs (c, c') are transferable and verified cold from files.
* **B verifier wall is a sequential sum** over 25 independent proofs (one `ligero-verify` process each, `--threads 16`,
  in-process `total`). No parallel-batch measurement was taken; `ligero-verify batch` exists and was not used.
* **A soundness is recorded, not live** (127.7 bits, SHA-256 collision term), as in gate4 and a-protocol-diff.
* **Not run**: A on the `torch`-only or un-graphed path (gate4-style comparators), B non-ZK Fiat-Shamir, a B checker-v2
  row (no such prover), 5-rep medians, A with `--threads` other than 16, the parallel B verification above.
* **Deviations from the brief**: none on versions -- torch 2.6.0+cu124 / Triton 3.2.0 installed first time. The bootstrap
  attempt is `rc=1 / UNKNOWN_EXIT` for the `--help` reason in §3 and was re-recorded as `BOOTSTRAP_OK`. `research data pull`
  hit one transient `attempt to write a readonly database` (retry succeeded) and needed `set -a; source
  ~/.config/verity/r2.env` because that file has no `export`s.
* No `.md` was added to the repo; `tests/test_repository.py` passes (5/5) on the worktree.

## 6. Pod time

Sum of `research inspect` cost estimates (rate x run wall, run occupancy only) over the ten attempts:

| attempt | what | wall s | est. $ |
|---|---|---|---|
| r20260922-175324-8307 | bootstrap (first, rc=1 on the help check) | 130.6 | 0.1266 |
| r20260922-180223-cda6 | a B non-ZK int | 34.8 | 0.0337 |
| r20260922-180414-0585 | b B ZK int | 30.2 | 0.0293 |
| r20260922-180748-ba52 | c B ZK FS | 33.9 | 0.0329 |
| r20260922-180844-e013 | d A v1 (incl. Triton compile warm-up) | 295.7 | 0.2866 |
| r20260922-181404-e39d | e A v2 (incl. Triton compile warm-up) | 352.4 | 0.3417 |
| r20260922-182103-69ec | bootstrap re-run (idempotent) | 14.4 | 0.0140 |
| r20260922-182131-5066 | a' | 30.6 | 0.0296 |
| r20260922-182217-284a | b' | 29.8 | 0.0289 |
| r20260922-182302-3cb0 | c' | 33.3 | 0.0323 |
| **total** | | **985.7 s = 16.4 min** | **$0.96** |

Pod wall-clock from creation (17:52Z) to this report (18:33Z) is 41 min = $2.38 at $3.49/h; the difference is idle time
between runs and the other lane's slot. `--exclusive` was never held across more than one run. The pod is left up with
`/workspace/venv312`, `/workspace/bin/{verity-gkr-verify,ligero-verify}`, `/workspace/bench-instances/v1`,
`/workspace/bb/pos4096`, `/workspace/v2l/pos4096` for the tensor-core lane.
