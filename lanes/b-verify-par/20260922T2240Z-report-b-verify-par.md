---
id: r21-bestvsbest/b-verify-par/20260922T2240Z-report-b-verify-par
campaign: r21-bestvsbest
lane: b-verify-par
kind: report
status: closed
repo: verity-main@5f2dc17
branch: lane/b-verify-par (off 4987a47; one commit 5f2dc17; not merged, not pushed)
machine: vy-bvp (RunPod bda9qtiicgy0od, H100 80GB HBM3 SECURE EUR-IS-3, Xeon Platinum 8468, nproc 160 but cgroup cpu quota 17, driver 570.195.03 / CUDA 12.8; created 21:33Z, terminated 22:33Z)
decision: r20 Q2 e2e (prover + independent Rust verifier), B-Ligero side
---

# b-verify-par: `ligero-verify batch --jobs N` -- the 25 sub-batch proofs of a B-Ligero batch verified concurrently

## 1. Answer

B-Ligero's only end-to-end loss in h100-bestvsbest came from `ligero-verify` being invoked 25 times in sequence
(2.606 s non-ZK / 3.346 s FS-ZK at 16 threads each). With the sub-batch proofs verified concurrently the independent
Rust verification of the whole B=4096 K=1536 2^-128 batch takes **0.54 s (non-ZK interactive) / 0.70 s (ZK Fiat-Shamir)**
of wall on a pod whose CPU quota is 17 cores, and the implied e2e at 0 ms is

| | prover s | Rust verifier s (25 sub-batches) | e2e@0ms s | vs A v2 2.524 s |
|---|---|---|---|---|
| B non-ZK interactive, Q2 prover number (vy-h100) + this verifier | 1.034 | 0.542 (jobs=25) | **1.576** | A/B = 1.60 |
| B non-ZK interactive, today's prover on vy-bvp + this verifier | 1.072 | 0.542 | **1.614** | 1.56 |
| B ZK Fiat-Shamir, Q2 prover number + this verifier | 1.194 | 0.704 (jobs=25) | **1.898** | 1.33 |
| B ZK Fiat-Shamir, today's prover on vy-bvp + this verifier | 1.351 | 0.704 | **2.055** | 1.23 |
| A a-gpu2 checker-v2 (Q2 row e; one proof, `verity-gkr-verify --threads 16`) | 1.336 | 1.189 | 2.524 | -- |
| A a-gpu2 v1 (Q2 row d) | 1.770 | 0.800 | 2.570 | -- |

So the order flips back: B wins e2e as well as prover, by 1.6x (non-ZK) and 1.2-1.3x (complete HVZK FS) against A's
best non-ZK number. Nothing about what is verified changed (§2); every one of the 2 x 3 x 25 = 150 recorded proofs
(plus the warm-ups) was accepted by the Rust verifier at every `--jobs` setting, and the 2 new tests pin that the batch
verdict, the per-sub-batch reason strings and the parsed statements are identical at `--jobs 1` and `--jobs N`.

Caveats on the comparison: (i) the CPU differs from vy-h100 (EPYC 9554, 224 threads, no visible quota) -- this pod is
a Xeon 8468 with a 17-core cgroup quota (`nproc` says 160; `available_parallelism()` correctly says 17). The sequential
16-thread control on this pod (`--jobs 1 --threads 16`: 2.466 s non-ZK / 3.467 s FS) is within -5% / +4% of the Q2
numbers, so the verifier rows are comparable to within that. (ii) Today's prover is 3.7% (non-ZK) / 13% (FS) slower
than the Q2 medians on the same commit lineage -- not isolated; the host CPU is slower and the FS prover has more
CPU-side hashing (t=288, D=7) -- so both "Q2 prover + this verifier" and "today's prover + this verifier" are given.
(iii) 25 jobs on a 17-core quota oversubscribes; the per-proof time goes from 0.255 s (alone) to ~0.48 s at jobs=25,
but wall still drops because all 25 finish in one wave. On the 224-thread vy-h100 the jobs=25 wall would be nearer the
single-proof time (~0.26 s / ~0.33 s). Not measured; the table carries what was measured.

## 2. Design: what is parallel, what is shared, what is unchanged

Commit 5f2dc17 (`backends/ligero-verify/src/{verify.rs,main.rs}`, `tests/fixture.rs`, `README.md`; plus the timing
wrapper `backends/direct/ligero/verify_result.py`, its `Tool` in `backends/direct/ligero/tool.py` and one registry line).
`std::thread::scope` -- no rayon (pods have no registry access; the crate keeps its zero-dependency build).

**Parallel.** `ligero-verify batch --dir D [--jobs N] [--threads T]` puts the sub-batch proof paths (sorted by name, as
before) behind an `AtomicUsize` work counter and spawns `min(N, n_proofs)` OS threads; each thread pops the next index
and runs exactly the single-proof `verify_with(&shared, proof, statement, &opts)` that `ligero-verify verify` runs --
same parser, same BabyBear/NTT, same BLAKE3/BLAKE2b/SHAKE-256 transcript, same `reject()` points and reason strings.
`--jobs` defaults to `std::thread::available_parallelism()` (cgroup-aware: 17 on this pod). `--threads T` is unchanged
and still the intra-proof NTT/Merkle thread count (default 1 in batch mode; the per-proof `verify` default is what it
was). Results are written into a pre-sized `Vec<Option<BatchItem>>` at the proof's index and reported in proof order,
so the JSON, the per-proof lines and the exit code do not depend on scheduling.

**Shared, computed once per batch** (`verify::Shared`): the parsed `system.json` (chain, digests, pinned-digest check --
previously re-parsed and re-checked per invocation) and the NTT twiddle / coset tables per `(l, n)` dimension pair,
behind a `Mutex<HashMap<(l, n), Arc<Tables>>>` (the first proof with a given `(l, n)` builds them; a batch has one pair).
The hash constants are compile-time. `shared_seconds` is reported separately (0.9 ms here); it was inside each
proof's `ntt` timing before and is subtracted there so per-proof timings stay comparable to the old ones.

**Unchanged.** Per-sub-batch verification is byte-for-byte the same code path; `verify` (single proof) still builds its
own `Shared` and reports the same verdict. The batch is accepted iff every sub-batch is accepted (`batch_accepted`,
`batch_reason: "accept: all 25 sub-batches accepted"` or `"sub_03.proof: <that proof's reason>"` -- the first rejected
proof in name order, so the reason is deterministic; `"<k> sub-batch file(s) could not be read"` when I/O failed). There is no cross-sub-batch binding check to hoist:
PROTOCOL.md has no §12; the batch statement (§3/§8c) is the multiset of independently committed sub-batch statements,
and the only field a sub-batch statement carries about the batch is `n_proofs`, which enters the union-bound soundness
accounting (`union_log2 = per_proof_log2 + log2(n_proofs)`, checked per proof against the target as before). I did not
add a check that all sub-batches agree on `n_proofs` (they do here) because the task said the cross-sub-batch checks
stay exactly as they are; adding one is a protocol decision, noted in §6. Interactive mode (D7): batch mode now reads a
per-proof `sub_XX.coins` sidecar (128 raw bytes or 256 hex chars = r1||s1||r2||s2) and passes it as `--coins`, so each
sub-batch is checked against *its* verifier's step-0 coins exactly as `verify --coins` does; the reason string stays
"accept (interactive: coins are this verifier's step-0 coins)" and `own_coins` counts how many proofs had one. Without
a sidecar an interactive proof gets the verdict it got before: "accept (interactive: coins replayed from the transcript;
sound only if they were the verifier's step-0 coins)", i.e. the D7 caveat is still carried in the reason. Python-verdict agreement
(`manifest.json` `python_verdict`, when present) is unchanged and still gates exit code 3.

Exit codes: 0 all accepted; 1 some sub-batch rejected; 2 unreadable proof/statement/coins; 3 Python disagreement.

## 3. Tests (on the pod, `cargo test --release`, bootstrap attempt r20260922-214833-a311)

~~~
running 8 tests   (field: coset_encode, ntt_matches_naive_and_inverts, barrett; hash: blake2b x2, shake256 x2, blake3)
test result: ok. 8 passed; 0 failed
running 6 tests
test a_flipped_public_word_is_rejected ... ok
test honest_b1_zk_proof_is_accepted ... ok
test every_region_of_the_proof_is_bound ... ok
test interactive_mode_own_coins_are_checked ... ok
test batch_verdict_and_statement_do_not_depend_on_jobs ... ok          (new)
test a_corrupted_sub_batch_rejects_the_batch_with_the_same_error_on_any_jobs ... ok   (new)
test result: ok. 6 passed; 0 failed; finished in 0.67s
~~~

`batch_verdict_and_statement_do_not_depend_on_jobs`: six honest sub-batches built from the fixture B1 ZK interactive
proof, three with a `.coins` sidecar and three without, verified at `--jobs 1` and `--jobs 8` (clamped to 6): both exit
0 with `batch_accepted`, 6 accepted, `own_coins` 3, 3 x "coins are this verifier's step-0 coins" + 3 x "coins replayed
from the transcript"; the JSON with timing / jobs / threads fields stripped (`signature()`) is byte-identical between
the two, and every item reports the same parsed statement (`l=256 n=2048 D=6 t=189 zk mode=interactive n_proofs=1`,
identical BLAKE2b statement digests).
`a_corrupted_sub_batch_rejects_the_batch_with_the_same_error_on_any_jobs`: same six, with one byte flipped in
`sub_03.proof`'s opened columns; `--jobs 1` and `--jobs 8` both exit 1, 5 accepted / 1 rejected, identical
`batch_reason` starting `"sub_03.proof: merkle path "`, identical stripped JSON. Then, at `--jobs 4`: a wrong
`sub_00.coins` is a rejection of that sub-batch ("coins are not this verifier's step-0 coins", 2 rejected, exit 1, not a
crash), and a deleted `sub_05.stmt` is an operator error (exit 2) reported after the other verdicts.

Local laptop: only `python -m pytest` of the unchanged store/harness tests was run (no Rust build, per the rule).

## 4. Verifier seconds by `--jobs` (vy-bvp, `ligero-verify batch`, `--threads 1` unless stated, median of 3 reps, each rep = 1 warm-up + 3 batch verifications)

`wall` = `wall_seconds` from the batch JSON (process-internal, from after arg parsing to after the last join); `sum` =
`verify_seconds_sum` (the per-proof `total` timings added up = CPU-side work, which inflates under oversubscription);
`e2e` = today's `prove_wall` + `wall`. All 75/75 accepted in every run. `jobs=160` is `--jobs $(nproc)`; the binary
clamps to `n_proofs` = 25 so it is a replicate of jobs=25 (`verifier_jobs` measurement 25, `jobs_requested` 160 in the
fingerprint). `jobs=17` is the default (`--jobs` omitted = `available_parallelism()` = the cgroup quota).

**Non-ZK interactive** (dump r20260922-215131-f3ca, prover 1.072 s, 110.77 MB, 25 x 170 VUs, t=196 D=6, 2^-128.25):

| jobs | threads | wall s | min | sum s | e2e@0ms s | speedup | run id | art id |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 6.394 | 6.301 | 6.365 | 7.466 | 1.00 | r20260922-220530-a696 | art:9f10431a750f72e96859a95bf5d1a83803aa645575f83677e57a7ccfb1eb6d0f |
| 2 | 1 | 3.346 | 3.267 | 6.409 | 4.418 | 1.91 | r20260922-220712-0af1 | art:a01ee23fb1f7b2811c8237679916f23c21016e3c9f9bebed35294190e2ee5ad7 |
| 4 | 1 | 1.792 | 1.776 | 6.442 | 2.863 | 3.57 | r20260922-220812-27e6 | art:32188396badb0a761b1eaf116af3cd11a1a2e49ae54b6a4e65bf8e9682178ad2 |
| 8 | 1 | 1.065 | 1.058 | 6.895 | 2.137 | 6.00 | r20260922-220857-6767 | art:98a7fcc83ba1b3abd3147d18363893842d0062bdf03cf5cfdb738d305dc8338c |
| 16 | 1 | 0.630 | 0.622 | 7.863 | 1.702 | 10.1 | r20260922-220936-8cca | art:0f61336a3dd0a768059570ce9b913b6eb3486c5df1ae2577bfe055cc9e4d7d99 |
| 17 (default) | 1 | 0.631 | 0.619 | 7.910 | 1.703 | 10.1 | r20260922-223037-ca70 | art:380a403286a983a6cd83ebccfe6de5927fe67ac5f90b0f5119211acb9527d3f3 |
| **25** | 1 | **0.542** | 0.521 | 12.129 | **1.614** | 11.8 | r20260922-221005-3284 | art:314253bbd9731f4e0297a27cff91c106bca030a366b98b0eff58772f4c2a50d0 |
| 160 (nproc -> 25) | 1 | 0.545 | 0.519 | 12.112 | 1.617 | 11.7 | r20260922-221033-a4d7 | art:b91d2c94bce60289f12d9f740a73acb55f0bf12b77fc5708d5a426f0fbc2c40a |
| 8 | 2 | 0.750 | 0.739 | 4.943 | 1.822 | 8.5 | r20260922-221152-05c0 | art:01a900152829fbcd312dee926c1d5309a2eb6a8431d6b8d509215058a22ec877 |
| 1 (Q2 method) | 16 | 2.466 | 2.439 | 2.443 | 3.538 | 2.59 | r20260922-221102-5538 | art:9d41ca0d73bb1aa561d8c7529edc2adf01b02aa1f8869b25bed0f36d568fff91 |

**ZK Fiat-Shamir** (dump r20260922-215602-220d, prover 1.351 s, 165.32 MB, t=288 D=7 t_pad=512, 2^-128.04, COMPLETE_HVZK_BACKEND):

| jobs | threads | wall s | min | sum s | e2e@0ms s | speedup | run id | art id |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 8.152 | 8.053 | 8.051 | 9.503 | 1.00 | r20260922-221222-a870 | art:b9eb431bddbdf4b20b0d64ec508950c78e0fb0eacc6e8e5e27cd6fbfe516d294 |
| 2 | 1 | 4.276 | 4.219 | 8.179 | 5.627 | 1.91 | r20260922-221425-73c8 | art:4a6b829123636d1081118a0ec10dc04c82161608c81104b7c791582e3786a67b |
| 4 | 1 | 2.344 | 2.295 | 8.369 | 3.695 | 3.48 | r20260922-221539-ecb8 | art:462c1e5234a5ba932a5489a9fea733b3b53a5e0f81dab1ee31d9312ae52b490b |
| 8 | 1 | 1.350 | 1.342 | 8.720 | 2.701 | 6.04 | r20260922-221629-dc8f | art:5a99d1d6096259b8396dee8343f5fdaa659ef54cc29946f51ea01bec8f14b66a |
| 16 | 1 | 0.806 | 0.786 | 9.804 | 2.157 | 10.1 | r20260922-221708-c924 | art:1d325c33da9ec81d842c035a59b0d7af3c84a20a35a07f088ccb484512d31545 |
| 17 (default) | 1 | 0.784 | 0.774 | 9.628 | 2.135 | 10.4 | r20260922-223106-c501 | art:fb5614852ad02f87c5c08a32d5d357f0d85b2152b3af55e6ca9e480309aa4a69 |
| **25** | 1 | **0.704** | 0.678 | 15.735 | **2.055** | 11.6 | r20260922-221737-12a6 | art:64b8c4f6222d3accee55e614b82d4d2aa76c1643beb0858745e72546269dba2c |
| 160 (nproc -> 25) | 1 | 0.689 | 0.655 | 15.260 | 2.040 | 11.8 | r20260922-221806-a529 | art:eaea5ca285c22d7220b112bf37d423567af72cb84415ac81b658df56b7cf62d6 |
| 8 | 2 | 0.993 | 0.960 | 6.303 | 2.344 | 8.2 | r20260922-221941-4882 | art:cbcfdba297e64c5f395791bd6b4eab351f2f33b4b8323550315796ebe391a953 |
| 1 (Q2 method) | 16 | 3.467 | 3.438 | 3.375 | 4.818 | 2.35 | r20260922-221835-7f63 | art:658dc60fc5d7aeb1b6407cadb299076a2bf8e35b3d66687d7801aa2ec6c3e6cf |

Reading: near-linear to 8 jobs (6.0x), 10x at 16-17 (the quota), 11.7x at 25 where every proof is in flight at once on 17
cores. One proof alone is 0.255 s non-ZK / 0.322 s FS at one thread; the per-proof `total` at jobs=25 is ~0.48 / ~0.61 s
(oversubscription plus NTT memory traffic -- `ntt` is 0.19-0.27 s of the 0.48). Intra-proof threading is the worse use
of the same cores: `--jobs 1 --threads 16` gets 2.6x / 2.35x from 16 threads, `--jobs 8 --threads 2` is 0.75 / 0.99 s
against 0.63 / 0.81 s for `--jobs 16 --threads 1`. Recommendation for the e2e table: `ligero-verify batch` with the
default `--jobs` (available parallelism) and `--threads 1`; on a machine with >= 25 free cores that is the ~0.26 / ~0.33 s
single-proof time.

## 5. Provenance

Pod `vy-bvp` created 21:33:38Z (runpod/pytorch 2.4 cu12.4 devel, H100 80GB HBM3, $3.49/h), terminated 22:33:21Z: **59.7
min, ~$3.47**, one pod-hour of the <= 1.5 budget. Everything is a `research run --on vy-bvp --project verity --campaign
r21-bestvsbest --source . --exclusive --require-result` attempt from the 5f2dc17 tree; the laptop edited, launched,
polled and pulled (`research data pull --from vy-bvp <run> --project verity`, 23 attempts in the laptop store).

**Bootstrap** (`/tmp/bvp/bootstrap.sh`, the h100-bestvsbest recipe minus the A exports): r20260922-214127-1f90 aborted
early (launch-side), r20260922-214443-8ca9 built everything -- `uv` -> Python 3.12.14 -> `/workspace/venv312` (torch
2.6.0+cu124, Triton 3.2.0, numpy, cupy-cuda12x, blake3), rustup stable, `cargo build --release` + `cargo test --release`
of `backends/ligero-verify` -> `/workspace/bin/ligero-verify` sha256 `8d4aa961…`, `verity_numerical.bench.instances
build` -> `/workspace/bench-instances/v1` -- but printed `BOOTSTRAP_FAILED` because its final check grepped `failed` and
matched `0 failed` in the cargo output; r20260922-214833-a311 is the idempotent re-run with the fixed check (4.0 s,
`BOOTSTRAP_OK`, the test log in §3 is from 8ca9/a311 -- identical binary).

**Prover dumps** (`bench_vu` tool, `backends/direct/ligero/bench_result.py bench-vu --batch 16384 --total-vus 4096
--reps 3 --root /workspace/bench-instances/v1 --device cuda --verifier /workspace/bin/ligero-verify --threads 16`,
`--scratch triton`; the h100-bestvsbest wrapper, which also runs the sequential 16-thread Rust verification = the Q2
method, so each dump run is itself a Q2-style row):

| mode | prover s (median/3) | seq. Rust verify s (25 x `verify --threads 16`) | Py verifier s | run id | art id |
|---|---|---|---|---|---|
| interactive non-ZK | 1.072 | 2.643 | 0.756 | r20260922-215131-f3ca | art:56dbfbe30f48122d4f4d30e88d12b09615affb16e951eb28d85a26b6893647e7 |
| fiat-shamir `--zk` | 1.351 | 3.685 | 0.938 | r20260922-215602-220d | art:b2bb25da39c57c98dc21252fad1f3aeb67beb9516898b90669084ad2a48a2c33 |

Dumps live in the run dirs (`proofs/rep{1,2,3}/sub_XX.{proof,statement,coins}` + `manifest.json`) and are in the pulled
`run-files/v1` trees; they were not artifacts in the store before (checked: h100-bestvsbest's dumps were run files too),
so they were regenerated with today's prover (same prover code as Q2's b48dfbb lineage; the commit differs only by this
lane's verifier/wrapper files).

**Verifier attempts** (`ligero_verify_batch` tool = `backends/direct/ligero/verify_result.py --dir <dump>/proofs --jobs N
--threads T --reps 3 --verifier /workspace/bin/ligero-verify --prover-result <dump>/result.json`): for each of the 3 reps,
one warm-up batch verification then 3 timed ones; `verify_wall` = median over reps of the per-rep median wall; the
result carries `verifier_jobs`, `verifier_threads`, `available_parallelism`, `proofs_total = proofs_verified_independent
= 25`, `prove_wall` (copied from the dump's result), `e2e_0ms`, the batch JSONs under `verify/`, and a fingerprint with
the dump's run id / manifest set, the verifier sha256, `jobs_requested`, `hw.cpu`.

**Labels** (laptop store, `--by b-verify-par --ref <run>`): every verifier `bench-result/v1` carries `candidate=B-Ligero`,
`component=verifier`, `jobs=<requested>`, `threads=<T>`, `mode`, `zk`, `hardware=h100`, `campaign=r21-bestvsbest`,
`independently_verified=true`, `lane=b-verify-par`; the two prover artifacts carry `component=prover`, `proof_class`
(NON_ZK_PROOF_DIAGNOSTIC / COMPLETE_HVZK_BACKEND) and the same candidate/mode/zk/hardware/campaign labels.
`research data select --kind bench-result/v1 --label component=verifier --label lane=b-verify-par` -> 20 artifacts.

## 6. Spec issues / things to weigh

* **PROTOCOL.md has no §12.** Statement binding is §3 (per-proof statement hash into the transcript) and the batch is
  §8c; there is no batch-level statement or binding check in the protocol or in either verifier beyond each sub-batch
  carrying `n_proofs` for the union bound. So "done once" had nothing to apply to. Open protocol question (not changed
  here): should the batch verifier require all sub-batches to carry the same `n_proofs` >= the actual count? Today a
  batch of 25 proofs each claiming `n_proofs = 1` would be accepted with each proof's own 2^-132.9, i.e. the union-bound
  2^-128.25 claim is not enforced across the directory. A one-line check in `batch`; wants a DISCREPANCIES/PROTOCOL entry.
* **`nproc` is not the CPU budget on RunPod.** `nproc` = 160 (host) while the cgroup quota is 17 cores (`cpu.max
  1700000 100000`); the pod is sold as "20 vCPU". `available_parallelism()` reads the quota, so the default `--jobs` is
  right and `--jobs $(nproc)` is just "all 25 at once". Record the quota, not `nproc`, for verifier timings.
* **Different CPU from vy-h100.** Verifier seconds across the two pods are comparable to ~5% via the sequential
  16-thread control (§1). A same-pod A-vs-B e2e rerun (A's `verity-gkr-verify` and B's `ligero-verify batch` on one
  machine) would remove that; ~10 pod-minutes.
* `rayon` was ruled out by the no-registry constraint, so the crate stays dependency-free; `std::thread::scope` is enough
  for 25 independent tasks.
* `DISCREPANCIES.md` unchanged: no Python-vs-Rust difference surfaced (Rust 75/75 = Python 75/75 on both dumps; the
  batch JSON's `python_agree` is 0 only because bench-vu's `manifest.json` carries no `python_verdict` entries -- the
  agreement was checked per proof by `bench_result.py` in the dump runs).
* Laptop-side driver hiccups, none affecting results: the first driver died silently twice (Cursor shell session
  cleanup killed the backgrounded process; re-run as a tool-managed background job), one `research run` was refused
  with "pod has no ssh port mapped yet" (transient RunPod API read; retried), and macOS bash 3.2 has no `declare -A` /
  `setsid`.
