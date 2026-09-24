---
id: r21-bestvsbest/b-batch-bound/20260922T2350Z-report-b-batch-bound
campaign: r21-bestvsbest
lane: b-batch-bound
kind: report
status: closed
repo: verity-main@40786ce
branch: lane/b-batch-bound (off 5a89d9d; two commits c426cb6, 40786ce; not merged, not pushed)
machine: vy-bbb (RunPod crit63dwu5sgo7, RTX 4090 24 GB, 12 vCPU but cgroup cpu quota 10.2 -> available_parallelism 10, 31 GB, $0.74/h, runpod/pytorch 2.4 cu12.4 devel; created 23:18:00Z, terminated 23:48:43Z)
decision: soundness accounting of a B-Ligero batch is a verifier check in both verifiers (finding from b-verify-par)
---

# b-batch-bound: the batch verifier enforces the union bound over the sub-batches presented, and `n_proofs = N`

## 1. Answer

Before this lane no verifier checked the accounting that makes "the 4096-VU batch is sound to 2^-128" true: a batch
of `N` independently committed sub-batch proofs was accepted iff every sub-batch proof verified on its own, each gated
(Rust) on its OWN `per_proof_log2 + log2(n_proofs)` with `n_proofs` a prover-supplied header field outside the
statement digest, or (Python `bench-vu`, `serialize verify`) not gated at all -- the union bound was *reported*, never
*checked*. Now both verifiers apply the same rule (PROTOCOL.md 8c, "Batch verification", 24 lines) with the same
reason strings, agree on the batch bits to < 1e-9 at B = 4 and B = 4096, and the check costs nothing measurable.

Honest B = 4096 ZK interactive batch (25 x 170 VUs, `l = 16384`, `t = 197`, `n_proofs = 25`): every sub-batch
**2^-132.693391037**, batch **2^-128.049534847** (Rust `128.049534847`, Python `128.049534847`, |diff| 1.2e-10),
accepted at `--target-bits 128`. The BEFORE binary accepted four `n_proofs = 1` proofs presented together (the gap);
the AFTER binary and the Python verifier both reject them with `batch: n_proofs mismatch (sub_00.proof: n_proofs = 1,
4 sub-batches presented)`.

## 2. The rule as written (PROTOCOL.md 8c, "Batch verification: the union bound is a verifier check")

> A batch verifier with target `t` bits accepts iff
> 1. every sub-batch proof verifies against its own statement, with the shared system (sections 3-8c as before);
> 2. `sum_i 2^-b_i <= 2^-t`, where `b_i` is the verifier's OWN recomputation of proof `i`'s bound from that proof's
>    parameters `(n, k, l, t, D, mode, zk)` -- never a prover-supplied field -- and `t` is the verifier's parameter
>    (`--target-bits`, default 128); the batch bits reported are `-log2 sum_i 2^-b_i`;
> 3. every proof's `n_proofs` equals `N`, the number of sub-batches presented (a proof sized for a smaller batch is
>    rejected, reason `batch: n_proofs mismatch`; so is one sized for a larger batch -- it belongs to another batch).
>
> Rule 2 is the accounting; rule 3 is what makes a sub-batch proof's `t` a commitment to its batch rather than a
> coincidence. [...] Soundness is a parameter, not a constant.

Statement binding is unchanged: section 3/4's digest is recomputed by the verifier from its own configuration and
the shared system is pinned as before; the rule adds to it, weakens nothing. Reason precedence (both verifiers):
unreadable input < a rejected sub-batch (`<name>: <reason>`) < `batch: n_proofs mismatch (<name>: n_proofs = k, N
sub-batches presented)` < `batch: union bound 2^-x over N sub-batches exceeds the target 2^-t`; the accept reason is
`accept: all N sub-batches accepted; union bound 2^-x <= 2^-t` (`t` printed as an integer when it is one, else two
decimals).

## 3. What changed (12 files, +636/-55 against 5a89d9d)

* **Python.** `protocol.log2_sum` / `protocol.batch_bound(per_proof_log2, n_proofs_claimed, target_bits, names)` --
  the rule as arithmetic on the verifier's own `soundness(cfg_i)["per_proof_total_log2"]`. `vu.ChainRunner.batch_bound`
  / `verify_batch(items, target_bits)` (in-memory sub-batch proofs; `bench-vu` verifies every rep's sub-batches through
  it and *asserts* the verdict); `run.py bench-vu --target-bits` (default 128; `--target` stays the prover's);
  `serialize.verify_batch_dir(dir, device, target_bits)` + CLI `serialize verify-batch --dir DIR --target-bits T` (the
  file-level Python batch verifier, the cross-check of `ligero-verify batch`; reads `.coins` when present via the new
  `read_coins`); `verify_result.py --target-bits` passes through to the Rust binary and records `batch_bits` as a
  measurement. `bench-vu`'s `security.achieved_log2` is now the verifier's `batch_log2` (asserted equal to
  `soundness()`'s union to 1e-6) with `achieved_bits` (= `-batch_log2`) and `verifier_target_bits` beside it; the
  full batch verdict is in `validation.evidence.batch`.
* **Rust.** `verify::Options.soundness_bits: Option<f64>` (`Some(128)` in `verify`, `None` in `batch`: the per-proof
  gate over a proof's OWN `n_proofs` is replaced by the batch gate); `verify::batch_bound(...) -> BatchBound {accepted,
  reason, batch_log2}` (same strings; `log2_sum` in the log domain). `ligero-verify batch --target-bits T` (default
  128; `--soundness-bits` is its alias in batch mode), computed inside the timed wall after all sub-batches; JSON gains
  `target_bits`, `batch_log2`, `batch_bits` (9 decimals), `per_proof_bits[]`, `n_proofs_claimed[]`; `batch_accepted`
  / `batch_reason` carry the verdict; exit 1 unless the batch is accepted. Sub-batches are still verified concurrently
  (`--jobs`), results collected in name order, so the verdict, reason and bits do not depend on `--jobs` (tested at 1
  and 4).
* **Docs.** PROTOCOL.md 8c (the rule, 24 lines); DISCREPANCIES.md D9 (the gap, the fix, verifier agreement);
  ligero-verify/README.md (`batch` usage, the flags, the JSON fields).
* **Tests.** `tests/test_ligero_batch_bound.py` (2 tests; `pytest.importorskip("torch")`): the arithmetic and the
  reason strings of `protocol.batch_bound`; `serialize.verify_batch_dir` on 4 copies of the committed `l = 256`
  fixture with `n_proofs` patched (honest-at-126 accepted with bits, rejected at 128 with the union-bound string,
  `n_proofs = 1` copies rejected with the mismatch string, a corrupted sub-batch takes precedence).
  `backends/ligero-verify/tests/fixture.rs`: `the_batch_union_bound_and_n_proofs_are_enforced` (a, b, c, alias,
  fractional target, larger-batch `n_proofs = 25`, corrupted sub-batch precedence, `--jobs` 1 vs 4) and
  `batch_verdict_and_statement_do_not_depend_on_jobs` extended with the batch bits and `n_proofs_claimed`.

## 4. Tests (pod, attempts r20260922-233058-2276 `cargo test --release`, r20260922-233238-e544 matrix)

`cargo test --release` (backends/ligero-verify, after two iterations fixed on the pod: a simultaneous borrow in the
new test, and a JSON helper that cut the reason string at its first comma -> `sfield`): **8 unit + 7 integration
passed, 0 failed**. `tests/test_ligero_batch_bound.py` on the pod (CPU): 2 passed.

Matrix (`/tmp/bbb/matrix.sh`; fixtures generated by the prover on the 4090, `l = 256`, ZK interactive):

| case | fixture | Rust `ligero-verify batch` | Python (`serialize verify-batch`, cuda; `bench-vu` in-memory for (a)) |
|---|---|---|---|
| (a) honest 4-batch at `--target-bits 128` | `bench-vu --batch 192 --total-vus 8 --zk` -> 4 sub-batches of 2 VUs, `n_proofs = 4`, per-proof 2^-130.189806 | exit 0, `accept: all 4 sub-batches accepted; union bound 2^-128.19 <= 2^-128`, `batch_bits 128.189805782` | same verdict, same string, bits 128.189805782 (|diff| 3.7e-10); `bench-vu security.achieved_bits` 128.18980578162632 |
| (b) same proofs, `--target-bits 130` | same | exit 1, `batch: union bound 2^-128.19 over 4 sub-batches exceeds the target 2^-130` | same string, same verdict |
| (b2) same proofs, `--target-bits 128.191` (achieved + 0.001) | same | exit 1, `... exceeds the target 2^-128.19` | same |
| (c) four proofs each proved at `n_proofs = 1` (`gen-set --total-vus 2` x 4), presented together | per-proof 2^-128.155590, batch 2^-126.155590 | exit 1, `batch: n_proofs mismatch (sub_00.proof: n_proofs = 1, 4 sub-batches presented)` at `--jobs 1` and `4` | same string, same verdict, bits 126.155590066 (|diff| 2.9e-10) |
| (c) on the BEFORE binary (5a89d9d) | same | exit 0, `accept: all 4 sub-batches accepted` -- **the gap** | -- |
| (d) agreement | (a) (b) (b2) (c) | verdicts, reason strings identical; batch bits agree to < 4e-10 (tolerance 1e-6) | |

Laptop: `uv run -q pytest backends/numerical/tests/bench tests -q` -> 165 passed, 9 skipped (torch tests skip).
`rg -l '^<<<<<<< '` empty.

## 5. B = 4096: the check is free (attempts r20260922-233616-f94b prover, -233810-5553 before, -233942-6b77 after, -234136-46f4 interleaved A/B)

Batch regenerated on the 4090 with today's prover (`bench_result.py bench-vu --zk --mode interactive --batch 16384
--total-vus 4096 --reps 2 --device cuda --threads 8 --target-bits 128`; prover 1.427 s, 122.4 MB, `soundness_bits`
128.0495, `bench-vu`'s own batch verdict accepted). `ligero-verify batch --jobs 25 --threads 1` on rep2's 25
sub-batches (`verify_result.py`: per rep 1 warm-up + 5 timed; `verify_wall` = median):

| binary | sha256 | verify_wall s (median of 5) | min | verify_seconds_sum | verdict |
|---|---|---|---|---|---|
| before (5a89d9d, no batch check) | 2a769b67... | 1.7215 | 1.5811 | 39.66 | `accept: all 25 sub-batches accepted`, `batch_bits` absent |
| after (lane, `--target-bits 128`) | c9e589ca... | 1.5716 | 1.4277 | 36.30 | `accept: all 25 sub-batches accepted; union bound 2^-128.05 <= 2^-128`, `batch_bits 128.049534847` |

Interleaved A/B on rep1 (1 warm-up each, then 10 x before/after alternating): before median **1.558 s** (1.469-1.776),
after median **1.583 s** (1.460-1.801); the +25 ms median / -9 ms min difference is inside the run-to-run spread on a
10-core quota running 25 jobs. The added work is `soundness()` on 25 statements (already computed per proof before)
plus a 25-term log-sum-exp. Python file batch verifier on the same 25 proofs (cuda): accepted, 5.54 s, bits
128.049534847, reason string identical to Rust's, `n_proofs_claimed` all 25. (Absolute walls are 4090-pod numbers on a
10-core quota; the b-verify-par H100 figures at 17 cores were 0.54 / 0.70 s.)

## 6. Provenance

Pod `vy-bbb` created 23:18:00Z, terminated 23:48:43Z: **30.7 min, ~$0.38** ($0.74/h) of the <= 1 pod-hour budget.
Attempts (`research run --on vy-bbb --project verity --campaign r21-bestvsbest --source . --exclusive`, tree
c426cb6 then 40786ce): r20260922-231923-d915 bootstrap (`/tmp/bbb/bootstrap.sh`: uv -> /workspace/venv312 with torch
cu124 / numpy / cupy / blake3, rustup, `cargo build --release` -> /workspace/bin/ligero-verify, `bench-instances/v1`),
-232603-a76e `build_before.sh` (5a89d9d's `backends/ligero-verify` -> /workspace/bin/ligero-verify-before),
-232841-1fb8 / -232852-60cc / -233058-2276 `cargo test --release` (two fixes, then green), -233214-4f5c /
-233238-e544 matrix, -233616-f94b prover B = 4096, -233810-5553 / -233942-6b77 timing before/after,
-234136-46f4 interleaved A/B + Python B = 4096 agreement. All pulled into the laptop store
(`research data pull --from vy-bbb <run> --project verity`).

**Labels.** The 20 b-verify-par verifier `bench-result/v1` artifacts (`--label component=verifier --label
lane=b-verify-par`) carry `finding=batch-union-bound-unenforced-before-c426cb6` by `b-batch-bound` (ref
`lane/b-batch-bound`; labels only). This lane's three result artifacts (prover art:34cf7371..., verifier before
art:ec9087e6..., after art:0def7ba5...) carry `candidate=B-Ligero`, `component=prover|verifier`, `lane=b-batch-bound`,
`campaign=r21-bestvsbest`, `hardware=rtx4090`, `mode=interactive`, `zk=true`, and for the verifier rows `jobs=25`,
`threads=1`, `verified=accepted`, `verifier=ligero-verify batch @5a89d9d|@c426cb6 ...`, `verifier_seconds`; the prover
row `proof_class=COMPLETE_ZK_BACKEND`, `B=4096`, `soundness=2^-128.05 batch union bound over 25 sub-batches`.

## 7. Spec issues / things to weigh

* **The contract field is `security.achieved_log2`, not `soundness.achieved_bits`.** `contract.py` has no
  `soundness.*` fields; the fingerprint carries `security.achieved_log2` (the batch bound as a log2), with
  `N_subbatches` and `B_proof` already present (`vu.py` writes both; nothing renamed). `achieved_bits` and
  `verifier_target_bits` were added *beside* `achieved_log2` inside `security`. The h100-bestvsbest wrapper
  (`bench_result.py`, the `bench_vu` tool) re-fingerprints as `n_subbatches` / `per_proof_vus` -- pre-existing, untouched.
* **The Python verifier enforced none of it.** `bench-vu` computed `soundness()`'s `union_over_proofs` and *reported*
  it; `serialize verify` checked each proof's transcript (D1: no accounting at all). The Rust `batch` enforced only
  the per-proof gate `per_proof_log2 + log2(n_proofs) <= -128` with the header's `n_proofs`. So everything in task 2/3
  was missing; the only thing "already there" was the arithmetic (`soundness()`), which the rule reuses.
* **Two of the brief's numbers are the non-ZK ones.** "25 x `n_proofs = 1` at 2^-132.9 while the batch is 2^-128.3"
  is the non-ZK interactive decision workload (`t = 196`, union 2^-128.25); the ZK batch re-timed here is `t = 197`,
  per-proof 2^-132.69, batch 2^-128.05. Same gap, same fix; the PROTOCOL.md paragraph quotes the brief's figures.
* **`n_proofs` is not in the statement digest** (only `l, n, D, t, target, zk, k, mode` and the words are), which is
  why the (c) fixtures can be made by relabelling and why rule 3 is a count check, not a binding check: relabelling
  cannot move `b_i` (a function of digest-bound parameters), it can only fail rule 3. Binding `n_proofs` into the
  digest would make a relabelled proof fail rule 1 instead; not done here (a format change), worth weighing.
* **`main` has moved.** The lane is off 5a89d9d as instructed; `main` is now f5fe471 (19 commits, `lane/auth-included`
  merged: statement v3 / proof v2, a D9 of its own). A dry-run merge (`git merge-tree`) conflicts in `run.py`,
  `serialize.py`, `vu.py`, `DISCREPANCIES.md`; on merge this entry becomes **D10**. `fixture.rs`'s `N_PROOFS_OFF`
  (42, the `u32 n_proofs` byte offset of the `ligero-statement/v2` header) still holds for v3 (v3 = the v2 body + a
  trailing authentication block) but the assertion that the fixture was proved at `n_proofs = 1` must be re-run
  against main's fixtures. Not rebased (pod terminated; re-testing the v3 verifier is a merge-time job).
* Precedence choice: a rejected sub-batch's reason wins over the accounting, and the mismatch wins over the union
  bound (a batch that fails rule 3 usually fails rule 2 too; the mismatch names the cause). Both verifiers, both tests.
