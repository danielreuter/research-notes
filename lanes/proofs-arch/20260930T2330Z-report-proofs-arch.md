---
id: 20260930T2330Z-report-proofs-arch
campaign: verity
lane: proofs-arch
kind: report
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72); worker bc-e222fd63
cursor:
  subagentId: "bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4"
---

CHECKPOINT 369850ad1 (09:24Z) [open] Lean lincheck from the block's structure (CircuitFold.folded, folded_eq, partial_eq_halve_fold) at 369850ad1: all three packages build, audit PASS; soundness FoldRealizes changed, needs a statement reviewer; Lean old/new verdict sweep running
CHECKPOINT cc21a7d94 (08:19Z) [open] 1b61b024c node 2 clean slice: old verifier 6.33s K=2048 / 7.41s K=8192 vs M0 #20's 10.46/27.42 (4.1/20.0s = its host); partial 0.206/0.445s (31x/17x); node-1 tail was host noise; Lean folded path same verdicts on set 1 (31 sessions), proofs in progress
CHECKPOINT 4644ec6d (07:33Z) [open] 1b61b024c verifier: timers attribute it all (other<=1.1ms); M0 #20's own statements: partial 0.227s K=2048 / 0.525s K=8192 vs flat 5.08/5.42; 6 statements equivalent in all modes; old fold on M0 stmts withdrawn (provers hold), needs 1 CPU slot ~20 min
CHECKPOINT none (05:50Z) [open] resumed 05:50Z after the billing stop: reading GPU job pa-gpu-b9b724e (rc 0, 02:42Z), then CPU lincheck_modes_agree in a 0-GPU pod (CPUS=16), then report; branch b9b724e9d
CHECKPOINT none (02:23Z) [open] b9b724e9d staged K=2048+8192 (0-GPU job r20261001-020341-281c, 112-127, both rc=0); GPU job pa-gpu-b9b724e submitted 02:23Z (1 GPU, 112-127): flat/partial/both x K=2048,8192 from the stage cache; CPU lincheck_modes_agree job after it
CHECKPOINT b9b724e9d (02:02Z) [open] b9b724e: session verifier phase timers (eb51d8b) + template-aware lincheck FC_LINCHECK=partial default (8db1cb5), equal to upstream's on arch_proto k=13-25 and K=64 selftests (38/38); node-1 stage job pa-stage-b9b724e queued (0 GPU, 112-127), GPU job next
CHECKPOINT 94993e0f9 (00:49Z) [open] study done (/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/docs/flock-restructure.md; both handoffs acted on, copy model = Rows.stack d1bf7c38a): template-aware lincheck verifier -3.1..3.5s/stmt K=2048 same proofs; step slots 4.97e6->3.0e6; rows hashed once/stmt ->1.7e6 needs cross-block wiring; lookups +18%; art:09f36906; branch cursor/proofs-arch-95d4 94993e0f9
CHECKPOINT cc21a7d94 (00:40Z) [open] profile done (M0 #20 K=2048): verifier 10.46s vs prover 0.78s; lincheck structure work 3.1-3.8s/stmt, template-aware verifier removes ~93% of it (byte-identical proofs); prover structure share 21%; art:e2a1c8e1
CHECKPOINT ce30e9b65 (23:28Z) [open] no-op audit done (internal/proofs/noop-audit.md): padding excluded pre-proof by host executed_prefix rule; lifted/Serve@3 reps exist only in vllm, unprovable by C-Flock; study next
# proofs-arch: restructuring C-Flock for FP matmuls, hashes and no-ops

Daniel (Sep 30, 4:20 PM PDT): keep arbitrary Boolean circuits as the fallback, and ask what shape the prover takes if
it bakes in structure (lookups, uniform copies, hashes, no-ops). Experimental: prototypes and measurements only.
Branch `cursor/proofs-arch-95d4` (worktree `/tmp/proofs-arch`, off `origin/main` `ce30e9b65`).

Handoffs acted on: `20260930T2329Z-handoff-from-proofs-daniel-priorities` (no-ops dropped, interactive, uniform copies
first, then lookups, then hashes; SHA-512 + A3 only) and `20261001T0005Z-handoff-from-proofs-advisor-notes` (the
prototype's copy model is the soundness package's `Rows.stack` / `placement_stack`, commit `d1bf7c38a`).

## 1. No-op audit (4:30 PM PDT)

Full text: Project store `internal/proofs/noop-audit.md`.
- Post-EOS and padding positions are **excluded before proving**. `check/executed_prefix.py` sets
  `executed_prefix_len` (served + LAG, or the cap). It's host Python linked to Match G6, and not in any proof.
- The explicit representations live only in the vLLM integration: `Serve@3` (a live bit, unguarded bodies) and
  `LServe_v2` / `Lifted[F]_v2` (⊥ = `1<<w` tag bit, `LEnable_v1`). The opt-in `--padded-finalize` Commit writes ⊥ words.
  Only tests build lifted Programs.
- `verity.ir` has no ⊥ or enable. C-Flock's `ir_lower` raises `NoPiece` on every lifted primitive. A strict lift
  replays every gate, so ⊥ would cost full price.

## 2. Restructuring study (5:45 PM PDT)

Full text: `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/docs/flock-restructure.md`. Statement profiled: M0 #20
(`r20260930-184956-61fe`), K=2048 and K=8192 at m = 35.

- **The session is verifier-bound.** The GPU prover takes 0.78 s per statement; the loopback verifier takes 10.46 s
  (K=2048) or 27.42 s (K=8192). Prover circuit-structure work is 21%, and the lincheck is only 6%.
- **Idea 1, the template-aware lincheck verifier.** It computes the lincheck's final value from the slot template plus
  Δ in O(nnz(T) + |Δ|), and never builds a 2^k vector. Proofs and transcript are byte-identical. It saves 3.1–3.5 s
  per statement at K=2048 and 2.9–5.8 s at K=8192. Lean needs `CircuitFold.partial` plus one level-3 theorem,
  `partial_eq_halve_fold`; the soundness package needs nothing new.
- **Idea 2, step-sized slots.** Bits per MAC fall from 2048 to 1170 (K=2048) and from 4096 to 2048 (K=8192). Prover
  overhead falls from 4.97e6 to 3.0e6 and from 9.84e6 to 5.0e6. `placement_stack` already covers it, instantiated at
  the step.
- **Idea 3, each row hashed once per statement.** Hashes are 37% of bits at K=2048 and 69% at K=8192. Hashing each row
  once gives 534 and 547 bits per MAC, and prover overhead of 1.7e6 for both shapes. It needs cross-block wiring, a
  statement-format decision.
- **Lookups.** A char-2 lookup is a grand product proved with upstream `product_gkr`. It costs as much as about 149
  bits of zerocheck, so it breaks even at about 45 committed bits replaced. Products, alignment and normalization win;
  the max exponent doesn't. It gains 18% on top of idea 3.
- **Not located:** about 6.7 s (K=2048) and about 21 s (K=8192) of verifier time per statement is neither the lincheck
  nor the region claims. An instrumented M0 statement is the next profile. (§4 places it: the study underpriced the
  lincheck.)
- **Decisions for Daniel:** the cross-block wiring format; one 128-bit rep instead of two Fast100 reps (for
  `proofs-security`); weights bound at registration or commitments reused; lookup gates; the instrumented M0 profile.

## 3. Prototypes

All on `cursor/proofs-arch-95d4` under `backends/flock/arch_proto/` (head `94993e0f9`). The Rust benches are upstream
flock b684b12 examples; build notes are in their headers. Evidence:
`art:09f3690625239edc1ab2721b3c9a4f6daa2ec5b60a20474f9043d1edf8541837` (label `question`), which supersedes
`art:e2a1c8e1…`.

| file | what | commit |
|---|---|---|
| `step_template.py` | P1's sm_120 BF16 k16 step as a 2^13-row slot | `c019ed6d7` |
| `export_template.py` | the slot in `Rows.stack` order (inputs, computed rows, constant at nIn + nComp) | `1ace46f50`, `d1bf7c38a` |
| `uniform_copies.rs` | N copies in one block: flat, unit, step and template-aware verifiers | `3b80c24fb`, `d1bf7c38a` |
| `layout_model.py` | committed bits per MAC and session overhead, today against ideas 1–5 | `1b048fa25` |
| `lookup_cost.rs` | a product-GKR leaf priced against a zerocheck bit | `94993e0f9` |

- The prototype is correct in honest mode at k = 13–25, and at k = 13–22 in `Rows.stack` order. All five verifiers
  return the prover's claim, and a tampered `z_partial`, round message or Δ entry is refused.
- The lincheck proof is 1248 + 32·(k − 13) bytes for every description.
- The template-aware verifier is 10–40× faster than today's `BlockCircuit` fold (k = 26: 0.137 s against 1.71–1.90 s a
  rep).
- GPU was not run, which deviates from the handoff. The proofs are byte-identical, so a GPU comparison would measure no
  difference.

## 4. The session verifier (Oct 1, 12:30 AM PDT)

Branch head `1b61b024c`. The commits:

- `eb51d8bce`: phase timers.
- `8db1cb550`: the template-aware lincheck, `FC_LINCHECK=partial|flat|both`, partial by default.
- `b9b724e9d`: slot types built column-major (`CscCircuit`).
- `afb2f6718`: the selftest keeps three honest verifications per mode.
- `76a8ccd75`: `arch_proto/lincheck_modes.sh` and `70-class-sweep.sh BUILD_ONLY=1`.
- `acca35385`: C0 = I checked once per statement (`Stmt::c0_identity`).
- `1b61b024c`: the CUDA 13.3 runtime on `LD_LIBRARY_PATH`.

proofs-bf16-hill carries all of them, and proofs-verify-overlap has them through bf16-hill. The old fold is on
`cursor/proofs-arch-oldfold-e5c2` (`ebcdb95ed`): `8db1cb550` plus the scripts. Evidence, all CPU-only
`lincheck_modes_agree` selftests on 16 cores of a held slice, all labelled `question`:

- M0 #20's own statements: `r20261001-072031-bf72` (`art:f9f49b46…`), on node 1. On node 2's slice 128–143, clean
  before each run: `n2h-20261001-073948-c663` (`art:e400b91a…`, current tree `1b61b024c`) and `n2h-20261001-075246-720a`
  (`art:35f9049f…`, old fold `ebcdb95ed`).
- bf16-hill's `Gemm_v2` statements: `r20261001-061252-f258` (`art:acdcb4f8…`), and on the old fold
  `r20261001-062432-2a1d` (`art:454285fe…`).
- GPU serve sessions: `art:552f5f64…`.

- **The timers account for the whole verifier.** In every verification, `other_s` is at most 1.1 ms and `verify_s −
  total_s` at most 0.4 ms. In flat mode the lincheck is 92–98% of the verifier. The opening (setup, ring switch, Merkle,
  residual) takes 0.02–0.05 s, and decode, regions, bind and zerocheck less than 0.02 s together.
- **Verifier seconds per statement.** Each is the median of three honest verifications, 2 reps each. "Old" is
  `8db1cb550`: M0 #20's verifier restated with timers, on the row-major `SparseMatrixCircuit` structures, checking
  C0 = I on every rep.

| statement | flat | partial | both | old flat | old partial |
|---|---|---|---|---|---|
| M0 #20 K=2048 (`GemmCoordinate_v1`, 4×4 tile, n=512, m=35), node 1 | 5.08 | 0.227 | 5.80 | not run | not run |
| the same, node 2 | 4.22 | 0.206 | 4.31 | 6.33 | 2.20 |
| M0 #20 K=8192 (n=1024, m=35), node 1 | 5.42 (2.57–7.83) | 0.525 | 3.73 | not run | not run |
| the same, node 2 | 2.50 | 0.445 | 2.92 | 7.41 | 5.47 |
| `Gemm_v2` K=2048, n=2048, m=35 | 1.465 | 0.239 | 2.60 | 3.05 | 2.24 |
| `Gemm_v2` K=2048, n=16, m=28 | 1.35 | 0.194 | 1.40 | 5.02 | 3.72 |
| `Gemm_v2` K=8192, n=1024, m=35 | 3.93 | 0.568 | 4.75 | 10.81 | 8.04 |
| `Gemm_v2` K=8192, n=16, m=29 | 2.60 | 0.541 | 3.02 | 12.52 | 9.12 |

- **C0 = I.** The current tree checks it once per statement per process. The selftest pays that before the timed
  verifications, so the current columns leave it out. The old tree measured it at 0.08–0.3 s a rep.
- **What partial still costs.** `partial_types_s`, the fold over the slot's column-major types, takes 0.12 s at M0's
  K=2048 and 0.48 s at K=8192. Δ is under 0.025 s.
- **The tail was the host.** On node 1 (load 70–400), about one rep in six took 0.4–0.9 s more in `partial_types_s`,
  and flat at M0's K=8192 swung 3×. On node 2's clean slice neither happens: `partial_types_s` is 0.049–0.057 s a rep at
  K=2048 and 0.19–0.21 s at K=8192, and flat at K=8192 stays within 2.45–2.57 s a verification.
- **GPU serve sessions.** These ran on K=2048 `Gemm_v2`, n=2048, at `b9b724e9d` (before the C0 memo), on slices shared
  with other jobs. Verify went from 1.446 to 0.356 s, and C0 = I was 0.17 s of the latter. The session went from 2.106 to
  1.013 s. The prover binary and proof sizes were the same ([963794, 963794]), and every proof was accepted. The pod
  stopped at 02:42Z, before K=8192.
- **Equivalence.** `FC_LINCHECK` is read only by the verifier, and the selftest verifies the same proof bytes in every
  mode. On all six statements, in each mode:
  - honest proofs were accepted three times out of three;
  - an altered `z_partial` and an altered round message were refused, with the same reason in every mode;
  - the decoded proofs re-encode byte-identical;
  - `both`, which refuses any disagreement between flat and partial, accepted every honest proof.

  Earlier evidence: arch_proto k=13–25 and the K=64 selftests (41 cases).
- **The study's unlocated 6.7 s / 21 s.** The timers leave nothing unattributed. The old verifier (M0 #20's code, the
  row-major fold, C0 = I on every rep) on M0 #20's own statements, on node 2's clean slice, splits it:

  | | K=2048 | K=8192 |
  |---|---|---|
  | M0 #20's verifier, measured in its serve session | 10.46 | 27.42 |
  | the old verifier, held 16-core slice | 6.33 | 7.41 |
  | of which the lincheck | 5.63 | 7.07 |
  | of which C0 = I (two reps) | 0.63 | 0.31 |
  | left to M0 #20's conditions (its host at load 48–125, not exclusive; serve's loopback) | 4.1 | 20.0 |

  At K=2048 the study's 6.7 s is the lincheck it underpriced (5.63 s against its 3.1–3.8 s), C0 = I (0.63 s) and
  M0 #20's conditions (4.1 s). At K=8192 nearly all of the 21 s is M0 #20's conditions.
- **Against M0 #20.** On M0 #20's statements, on the same clean slice, the verifier goes from 6.33 s to 0.206 s at
  K=2048 (31×) and from 7.41 s to 0.445 s at K=8192 (17×). Against M0 #20's own 10.46 s and 27.42 s, measured in a
  contended serve session, those are 51× and 62×; a serve session on today's tree is the like-for-like comparison.
- **Next:** the Lean `lincheck` and `partial_eq_halve_fold`, as a separate commit (§5).

## 5. The Lean verifier's template-aware lincheck (Oct 1, 1:20 AM PDT, in progress)

The Lean executable's lincheck used to build the 2^k comb, add β at the pin and halve it every round. It now takes
the comb's 64 surviving entries from the statement once the rounds are done (`CircuitFold.folded`). `Stmt.folded`
computes them per slot type, as the Rust partial path does, whenever the ranges are aligned, inside the block and
disjoint (`Stmt.structured`, which `Circuit.checkLayout` already enforces). Otherwise it folds and halves as before.

- **Same verdicts.** Built from the uncommitted tree, against the pre-change binary, `tools/flock_verify/ci.py` with a
  no-op upstream over vectors.json's set 1 gives the same VERDICT on all 31 sessions, including the `lc-round` and
  `lc-z-partial` mutants: 177 s instead of 260 s. The remaining replayable and live sets are running.
- **Proofs.** The level-3 theorem `folded_eq` will say that `Stmt.folded` equals fold, then pin, then halve. The
  soundness package's `FoldRealizes` gains that as a field, so `lincheck_refines` keeps its statement. Eight pinned
  soundness records read `Flock.lincheck` or `CircuitFold` and will change (`needs-daniel:` in `lanes/proofs` names a
  reviewer).
