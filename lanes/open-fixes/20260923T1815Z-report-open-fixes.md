---
lane: open-fixes
kind: report
created: 2026-09-23T18:15Z
status: final
---

# open-fixes — hp2-host CUDA NTT validation · v2 exact-zero-sum gap · v3 pipelined-prover bug

CHECKPOINT ecec3ef (18:15Z) worktree ~/projects/verity-main-wt/open-fixes on lane/open-fixes from lane/leaf-iface 720820d; e689b72 cherry-picked clean (9268cc4 / f66d0bb already on the base); 4090 pod vy-open-fixes (3p9tb8bx2uxjt7, reference 24564 MiB, EUR-IS-1, EPYC 7282) bootstrapping.
CHECKPOINT a0ff818 (18:40Z) task 3 fixed + committed (per-stream hint graphs), fp8-ada-v3 p4 4096 VUs 0.155 s vs v1 0.180 s same pod, Rust 13/13; task 2 = already closed on main by 9a869b3 (probe: 02c3321 rejects 1768, this tree 0), regression test pending pod run; H100 vy-open-fixes-h100 (90rnj2279fblqq, $3.49/h, AP-IN-1) created 18:28Z, bootstrapping; 4090 running v3 gates → task 1 fp8-ada chain.
CHECKPOINT 21a8716 (state at ~19:30Z, line written late at 20:30Z — the 19:25Z checkpoint was missed) task 1 A/B done on H100 (fp8/bf16-hopper) + 4090 (fp8-ada): byte-identical everywhere, gates 0 fail, t.total not consistently faster; H100 terminated after its last run (19:07Z); task 2 regression test committed; v3 gates 0 fail, v3x4 p2/p4 pass + Rust.
CHECKPOINT 5e6b3e3 (20:30Z) NTT reverted; final-tree pod pytest 243 passed / 1 known-fail, cargo 49 passed; 4090 terminated 20:28:41Z; artifacts preserved + labelled. FINAL below.

## Setup

* Base `lane/leaf-iface` @ 720820d. `git merge-base --is-ancestor`: 9268cc4 and f66d0bb ARE ancestors of the base (via post-freeze);
  e689b72 is not → cherry-picked as ecec3ef (3 files: `field.py`, `ntt_cuda.py`, `ntt_cuda_test.py`), no conflicts.
* Pod `vy-open-fixes` = RunPod 3p9tb8bx2uxjt7, RTX 4090 24564 MiB (reference), EUR-IS-1 SECURE, AMD EPYC 7282 host, 9 vCPU, $0.74/h,
  created 18:04:55Z. Bootstrap = `evidence/bootstrap.sh` (blake3-leaf / dev-h100-2 recipe). Env on every run:
  `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1` (`evidence/run.sh`).
* Pod `vy-open-fixes-h100` = RunPod 90rnj2279fblqq, H100 80GB HBM3 81559 MiB (reference), AP-IN-1 SECURE, Xeon 8480+, 28 vCPU,
  $3.49/h, created 18:28:26Z (cap 1 h for the lane's $6).
* A/B trees shipped to both pods as trimmed `git archive`s (9.5 MB: `backends/{direct,shared,numerical/python,ligero-verify
  minus fixtures}`, `packages/verity/src`, `tools/research/src`, `fixtures/bench-instances`): `/workspace/src` = lane HEAD,
  `/workspace/src-base` = git tree bdae32a = HEAD with exactly e689b72's three files reverted (built in a temporary index;
  `git diff --stat HEAD bdae32a` = field.py / ntt_cuda.py / ntt_cuda_test.py only).

## Task 1 — hp2-host's four-step CUDA NTT (e689b72 = ecec3ef here): byte-identical, NOT faster in t.total → REVERTED (5e6b3e3)

Method: two trees per pod differing only in e689b72's three files (Setup). Byte-identity = hostphase's `bitexact.py`
(`evidence/bitexact.py`, adapted: `prove_vus_many` now passes the sub-batch index to the coins factory) — `os.urandom` replaced
by a seeded SHAKE stream so the interactive coins AND the ZK mask keys repeat; `--zk --mode interactive --pipeline 4`, every
sub-batch of the 4096-VU set at l = 16384; `cmpdig.py` compares the sha256 of every written file. Speed = `bench-vu --mode
interactive --batch 16384 --pipeline 4 --total-vus 4096 --reps 3` (local coins), base / lane interleaved, order alternating per
round (`t1_chain.sh`, `t1_more.sh`, `t1_tail.sh`); `ab.py` = paired medians. Dispatch check (`ntt_dispatch.py`, first prove of a
sub-batch): lane = 9 transforms per sub-batch all through `ntt_cuda` — `(36, 65536)` forward ×3 (the ZK mask rows' coset
evaluation) and `(6, 65536)` inverse ×6 (tests) — and 0 through the torch chain; base = 0 / 9. So the identity compares the paths.

| check | H100 fp8-hopper | H100 bf16-hopper | 4090 fp8-ada |
|---|---|---|---|
| seeded transcript identity (int-ZK, p4) | **40/40 files identical** (13 sub-batches × stmt/proof/coins + system) | **76/76** (25 sub-batches) | **40/40** |
| Rust batch verify of the lane files / lane bench dump | ACCEPT / 13/13, pinned | ACCEPT / 25/25, pinned | ACCEPT / 13/13, pinned |
| gate-vu --vus 2048 --batch 16384 (lane), --zk and plain | 7 honest / 92 neg / 0 fail (both) | 13 / 87 / 0 (both) | 7 / 92 / 0 (both) |
| `ntt_cuda_test` | passed | (same run) | passed |
| t.total int-ZK, 6 paired rounds, median base → lane | 0.1283 → 0.1255 s (−2.1 %, lane faster 5/6) | 0.2145 → **0.2207 s (+2.9 %, 3/6)** | 0.2049 → 0.1912 s (−6.7 %, 5/6; −2.8 % on the 3 rounds without a slow base run) |
| t.encoding_commitment int-ZK (t.encode) | 0.0268 → 0.0251 (−6.3 %, 6/6) | 0.0439 → 0.0418 (−4.9 %, 6/6) | 0.0507 → 0.0488 (−3.7 %, 6/6) |
| t.arithmetic int-ZK | 0.0837 → 0.0853 (+1.9 %, 3/6) | 0.1373 → **0.1479 (+7.7 %, lane faster 1/6)** | 0.1227 → 0.1063 (−13 %, base outliers) |
| t.total no-ZK (the brief's literal flags), 3 / 3 / 1 rounds | 0.1232 → 0.1290 (+4.7 %, 1/3) | 0.2019 → 0.2019 (0.0 %, 2/3) | 0.1721 → 0.1627 (−5.4 %, 1 round) |

Why reverted: the rule was "keep only if byte-identical and faster". Byte-identical: yes, everywhere. Faster: the encode phase is
(≈ −2 ms per run, 18/18 paired rounds, as hp2-host's kernel timings predicted), but t.total is not — on the H100 the arithmetic
phase (where the six `(6, 65536)` inverse transforms per sub-batch sit) gets slower and noisier with the kernel on bf16-hopper
(lane 0.136–0.175 vs base 0.135–0.149), cancelling the gain; without ZK there is no encode gain at all (the forward NTT it speeds
up only exists for the ZK mask rows). hp2-host's −7.4 % (bf16-hopper 0.2525 → 0.2337 on their tree) does not reproduce on this
tree, whose base is already 0.2145. The allocation (torch) and stream (`ExternalStream(current_stream)`) handling in
`ntt_cuda.py` are correct; the arithmetic-phase cost is unexplained (hypotheses, untested: per-call cupy launch / `asarray`
host overhead in the eager parts of the tests phase under 4-deep pipelining, or the shared-memory kernel crowding the other
slots). Cheap follow-up if someone wants the encode gain: dispatch only the `(36, n)` forward (encode path) to `ntt_cuda` and keep
the torch chain for the `(6, n)` inverse, then re-run this A/B on an H100. The commit stays in the branch history (ecec3ef) for a
re-pick.

## Task 2 — exact-zero-sum completeness gap: ALREADY CLOSED on main (no relation change; regression coverage added)

* relmin-private's finding ("`fp8-hopper-v2` in main rejects unit 92536 at `g0.norm.clamp`", §4b of their FINAL) was made on
  main **02c3321**. Main has since taken relmin-lookup **9a869b3** (00:31 PDT = 07:31Z, "v2 zero-sum completeness: clamp /
  overflow proofs on the z-masked exponent"): `git merge-base --is-ancestor 9a869b3` → main 22e10e0 yes, base 720820d yes,
  02c3321 no. `pubsel/` and `privsel/` are byte-identical between 720820d and main (`git diff --stat 720820d main` touches only
  the Rust verifier's leaf work).
* Mechanism: relmin-private's v3 fix is `(1 - hid - nsel[t_lo]) (t - tc) = 0`; 9a869b3 instead computes the clamp from the
  z-masked exponent (`e1m = acc_e_min` when `z = 1`), so for a zero sum `tc = width - nb >= t_lo = -nb` is always selectable.
  Two different fixes of the same gap; applying relmin-private's on top would change the four v2 (and four v2x4) digests
  and re-pin Rust for no completeness gain, so it was NOT applied.
* Evidence (4090, 18:15Z, `evidence/zero_sum_probe.py`: unit 92536 + 256 constructed units per relation — two live products
  cancelling exactly at the group maximum, every other product dead, c = ±0 — honest witness in unit and chain mode, plus
  every claim bit-flipped in unit mode):
  * control tree 02c3321: fp8-hopper-v2 rejects unit 92536 (unit and chain) and 256/256 constructed; fp8-ada-v2 256/256;
    bf16-hopper-v2 256/256; bf16-ampere-v2 115/115 → `PROBE_BAD 1768` (reproduces relmin-private's finding);
  * this tree: 0 rejected for all 12 relations (v2 ×4, v2x4 ×4, v3 ×4; unit 92536 on the three k = 32 E4M3 units),
    0 wrong claims accepted → `PROBE_BAD 0`.
* Regression test added: `pubsel/relation_test.py::test_cancelling_sum_at_large_group_maximum_accepted` over the 4 v2 +
  4 v2x4 relations (the existing `test_zero_sums_accepted_in_unit_and_chain_mode` covers only the unfolded four and has no
  "rest dead" shape): unit 92536 (asserted to be the +0 word on fp8-hopper-v2) + 256 constructed units, unit and chain
  mode accepted, bit-flipped claims refused, v1 agrees where registered. No system digest changed → no Rust pin change.

## Task 3 — v3 pipelined-prover bug: ROOT-CAUSED, FIXED (a0ff818)

Root cause (read 18:20Z, confirmed on the pod): `privsel/hints.py` cached ONE CUDA graph with its static input / output
buffers per `(id(sys), l, k, y, device)`; `hints_torch.py` (v1) and `fp8/witness.py` key theirs on
`torch.cuda.current_stream().cuda_stream`. `pipeline.prove_many` runs each job under `stream_context(slot)`, so at depth > 1
two slots copy their inputs into the same static buffers and replay the same graph exec (launches of one exec are ordered, the
input copies are not) → a sub-batch gets another sub-batch's hints → the self-check's "quadratic constraints failed". The same
class as pipe-race's encode_simt scratch-buffer race. `pubsel/hints.py` (v2) had the identical key (latent: v2's graph is short,
so the overlap is rare in the pipeline). Both `_Graph` constructors also swallowed capture failures (`except Exception: g = False`),
so `LIGERO_GRAPH_STRICT=1` could not surface them.

Fix (a0ff818, 2 files + test): key the graph cache on the current stream in both generators; route capture exceptions through
`protocol._capture_failed`. Hint generation only: no system, statement or transcript change → no pin change.

Evidence (4090):
* Repro, unfixed ecec3ef: `fp8-ada-v3 bench-vu --zk --mode interactive --batch 4096 --pipeline 4 --total-vus 340 --reps 1` →
  `AssertionError: sub-batch [0, 85): quadratic constraints failed`. Same command on the fix: `validation: passed`.
* Unit-level: `pipeline_race_test.py::test_hint_graphs_not_shared_across_streams[fp8-ada|fp8-ada-v2|fp8-ada-v3]` — two
  sub-batches' hints at once on two streams (the first held by `torch.cuda._sleep` so the second's inputs land first) vs the
  sequential hints, 5 trials: unfixed base → **fp8-ada-v2 5/10 and fp8-ada-v3 5/10 matrices wrong** (every second-stream one),
  v1 ok; fixed → 3 passed.
* Full point, fixed tree, 4096 VUs, l = 16384, 13 sub-batches, int-ZK, `--pipeline 4`, 3 reps, same pod back to back:

  | relation | t.total | witness | enc+commit | arithmetic | serial | peak mem | validation | Rust (rep 1) |
  |---|---|---|---|---|---|---|---|---|
  | fp8-ada-v3 (run b-ligero-fp8-ada-v3-vu-1790188108) | **0.1547 s** | 0.0547 | 0.0227 | 0.0683 | 0.0075 | 5.19 GiB | passed | 13/13 ACCEPT, batch 2^-128.32, system pinned (fp8-ada-v3), python agreement 13/13 |
  | fp8-ada v1 (run b-ligero-fp8-ada-vu-1790188168) | 0.1795 s | 0.0165 | 0.0486 | 0.1022 | 0.0121 | 6.12 GiB | passed | 13/13 ACCEPT, system pinned (fp8-ada) |

  v3 at depth 4 is **−13.8 % vs v1 at depth 4 on the same pod** (v1 here 0.180 vs Table 2's 0.170: this EPYC 7282 host is
  ≈ 5 % slow). Before the fix v3 could only run pipeline-1: 0.829 s (fold-private). Proof 46.0 MB vs v1's.
* `gate-vu fp8-ada-v3 --vus 2048 --batch 16384` on the fix (the negatives used to crash in `privsel/hints.py` on graph replay):
  `--zk` **7 honest / 92 negatives / 0 failures** (958 s); plain **7 / 92 / 0** (926 s).
* Folded `fp8-ada-v3x4` (failed at depth > 1 per fold-private), fixed tree, 4096 VUs, int-ZK, 1 rep:
  | point | t.total | hints | enc+commit | peak mem | validation | Rust |
  |---|---|---|---|---|---|---|
  | l = 16384, `--pipeline 2`, 4 sub-batches (run b-ligero-fp8-ada-v3x4-vu-1790191123) | 0.2057 s | 0.0899 | 0.0449 | 10.92 GiB | passed | 4/4 ACCEPT, batch 2^-128.67, pinned (fp8-ada-v3x4), python 4/4 |
  | l = 4096, `--pipeline 4`, 13 sub-batches (run b-ligero-fp8-ada-v3x4-vu-1790191308) | 0.2095 s | 0.1353 | 0.0260 | 5.06 GiB | passed | 13/13 ACCEPT, batch 2^-128.33, pinned, python 13/13 |
  The folded v3 is correct at depth > 1 now; it is slower than unfolded v3 at depth 4 (0.155 s) because its hint generation
  dominates (0.09–0.14 s) — a speed question for fold-private, not a correctness one.

## Tests (final tree = 5e6b3e3, shipped to the 4090 as `/workspace/src-base`)

* **Pod pytest** `backends/direct/ligero` (`LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`, 4090, 20:05–20:26Z, log
  `evidence/4090/logs/tests_pytest_final2.log`): **243 passed, 1 failed, 3 skipped, 18 deselected**. The failure is
  `fold_test.py::test_folded_fixture_is_the_compiled_system[bf16-ampere-x4]` (`rows_per_unit` ratio 4.146 against the < 4.1
  bound), which fails the same way on main; blake3-leaf, tier0-bytes and fold-private all report it, and it is unrelated
  to this diff. Deselected: `v2/` (as every lane does), plus the 16 CPU-only `fold_test` cases
  `test_folded_unit_is_exactly_four_chained_base_steps` / `test_folded_chain_is_the_base_claim_cpu` (~1.3 min each on this
  9-vCPU host; they never touch the CUDA hint graphs). The first attempt (`tests_pytest_final.log`) had 16 spurious
  fold-fixture failures because the trimmed archive lacked `backends/ligero-verify/fixtures` and `fixtures/*`; copied, re-run.
  The new tests are in this count: `pipeline_race_test.py::test_hint_graphs_not_shared_across_streams` ×3 and
  `pubsel/relation_test.py::test_cancelling_sum_at_large_group_maximum_accepted` ×8, plus the existing
  `test_differential_v1_v2` ×4 (random units, including 9a869b3's zero-sum families) and `test_differential_v1_v3` ×4.
* **Differential at 1e5** (`RELMIN_DIFF_N=100000`, pubsel): bf16-hopper-v2 passed (≈ 29 min); stopped before the other
  three to save pod time. The zero-sum class is covered deterministically by the new regression test.
* **Cargo** `backends/ligero-verify`, `cargo test --release` on the 4090: **49 passed, 0 failed** (26 + 7 + 16). No Rust changes.
* **Laptop pure-python** (worktree `.venv`, torch-less): `pytest backends/direct/ligero` → **12 passed, 17 skipped, 9
  collection errors** (the 9 modules import torch → their tests are in the pod count above).
* Task 1 extras: `ntt_cuda_test` passed on both the H100 and the 4090 (NTT tree).

## Pod costs

* H100 `vy-open-fixes-h100` (90rnj2279fblqq, $3.49/h): created 18:28:26Z, terminated after the last run (log 19:07:36Z);
  the exact stop time was not recorded, ≈ 0.7 h → **≈ $2.45**. `research pods get` → 404 (gone).
* 4090 `vy-open-fixes` (3p9tb8bx2uxjt7, $0.74/h): 18:04:55Z → terminated 20:28:41Z = 2.40 h → **$1.77**.
* Lane total **≈ $4.2** (cap $6). `research pods list`: no open-fixes pods.

## Artifacts (`research data`, all PRESERVED on the remote, labels by open-fixes, labels synced)

* `bench-result/v1` fp8-ada-v3 p4 `art:9d7d675c…`, fp8-ada v1 p4 control `art:39f1b9eb…`, fp8-ada-v3x4 p2 l = 16384
  `art:31e00d08…`, fp8-ada-v3x4 p4 l = 4096 `art:6e0ca60c…`.
* `run-files/v1` lane evidence tree (scripts, bitexact digests, bench JSON, gate / Rust / pytest / cargo logs, H100 + 4090)
  `art:8d2de58e32f7b5baac84af38c257eb6830a1390ff9ee5605ae39eca813390c50`.

## FINAL

Branch `lane/open-fixes` head **5e6b3e3**, `git status --short` empty. Diff vs 720820d: 4 files, +127 / −6
(`privsel/hints.py`, `pubsel/hints.py`, `pipeline_race_test.py`, `pubsel/relation_test.py`). No system digest changed → **no
Rust pin changes**. No new .md in the repo.

1. **hp2-host CUDA NTT (e689b72): REVERTED.** It's byte-identical (seeded ZK transcripts 40/40, 76/76 and 40/40 files; Rust
   ACCEPT) and gates pass with 0 failures on fp8-hopper, bf16-hopper and fp8-ada. Dispatch counts confirm the A/B exercised the
   kernel (9/9 transforms via `ntt_cuda` vs 0/9). It is not faster in t.total. H100, ZK, median of 6 paired rounds:
   fp8-hopper 0.1283 → 0.1255 s (−2.1 %); bf16-hopper 0.2145 → 0.2207 s (+2.9 %). Without ZK: +4.7 % and 0.0 %.
   t.encode improves 4–6 % in every paired round, but the H100's arithmetic phase gives it back. On the 4090 it is
   faster: fp8-ada 0.2049 → 0.1912 s (−6.7 %, 5/6 rounds; −2.8 % on the rounds without a slow base run). The revert
   rests on the H100, where hp2-host claimed the gain and where this A/B shows a wash or a loss. Follow-up worth trying: route only the
   `(36, n)` forward transform to the kernel.
2. **Exact-zero-sum gap: already closed on main** by relmin-lookup's 9a869b3 (an ancestor of this base and of main 22e10e0);
   relmin-private's finding was made on 02c3321. Probe: 02c3321 rejects 1768 honest units, this tree 0. relmin-private's
   alternative fix was NOT applied (it would change 8 digests for no gain). Added the regression test (unit 92536 + 256
   constructed units × 4 v2 + 4 v2x4, unit and chain mode, flipped claims refused). It fails on 02c3321 and passes here.
3. **v3 pipelined-prover bug: FIXED (a0ff818).** Root cause: `privsel/hints.py` and `pubsel/hints.py` cached one CUDA graph,
   with its static buffers, per shape, so pipeline slots on different streams overwrote each other's inputs. The same class
   as pipe-race's encode_simt scratch race. Graphs are now keyed per stream, and capture failures honour
   `LIGERO_GRAPH_STRICT`. fp8-ada-v3 `--pipeline 4` (4096 VUs, l = 16384, int-ZK): 13/13 sub-batches self-verified and
   Rust-ACCEPT (pinned), **t.total 0.1547 s vs v1 0.1795 s at depth 4 on the same pod (−13.8 %)**. v1 measures 0.170 s in
   Table 2; this host runs about 5 % slow. v3 gates (ZK and plain): 7 honest, 92 negatives, 0 failures, no crash. Folded
   v3x4 passes at depth 2 and 4, with Rust 4/4 and 13/13. The new race test fails on the unfixed tree (v2 5/10, v3 5/10)
   and passes after the fix.

Left for others: the NTT forward-only re-try (above); the bf16-ampere-x4 fold-fixture assertion (pre-existing, owned by
fold-private / tier0-bytes); v3x4 hint-generation speed; a full 1e5 differential across all four v2 relations if wanted
(about 2 h of CPU).
