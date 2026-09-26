---
lane: flock-ir-sampling
kind: report
created: 2026-09-26T08:08Z
status: final
---

CHECKPOINT af0bd416 (09:25Z) [final] FINAL: GumbelTopPTokenSelect_v1 lowered onto C-Flock (verity/flock-ir-sampling/v1, PR #65 @ af0bd416 on #54@f4cd5d4e); L40S cell art:a330c568 (0.500 rows/s) + H100 art:26b5f7d8 (0.537), captured #101 art:ea781b02, 0 mismatches on 4.1M lanes; red-team + merge requests sent; pods terminated, ~$5
CHECKPOINT 197f0d51 (09:15Z) [open] L40S cell registered art:a330c568 (gumbel-top-p-token-select/v128256/fp32, verity/flock-ir-sampling/v1 @ f70c6c77, captured #101 art:ea781b02, plateau 8 rows 0.500 rows/s m34, RTT 11 ms, check clean); sampling moved to its own module/binary (same statement digest), flock-ir-lowering v3 merged @ 197f0d51; next: H100 register, red-team request
CHECKPOINT f70c6c77 (09:01Z) [open] WAITING L40S cell r20260926-084507-3ae9 (prover) + r20260926-084457-7a06 (verifier) at point 32 (8 rows 0.50/s, 16 rows 0.49/s), and optional H100 cell r20260926-085143-1253 + r20260926-085104-58db (EUR-IS-3, RTT 0.8 ms); synthetic art:ccc8afba 4.1M lanes 0 mismatches; check after 09:10Z; agent bc-0ba89fde-5332-53f9-b622-f1264386f8cb; next: register both
CHECKPOINT f70c6c77 (08:45Z) [open] WAITING r20260926-084457-7a06 (verifier, vy-flock-ir-sampling-ver2 Dallas L40S) + r20260926-084507-3ae9 (prover, vy-flock-ir-sampling-l40s2 KC L40S) L40S cell gumbel-top-p-token-select/v128256/fp32 @ f70c6c77 (IR6 in), check after 09:10Z; agent bc-0ba89fde-5332-53f9-b622-f1264386f8cb; L40S GPU selftest all-pass r20260926-084023-82c0; next: check+register, red-team request
CHECKPOINT b7cbb4d5 (08:41Z) [open] PR #65 @ c0a1 (verity/flock-ir-sampling/v1): lane unit 5,099 ANDs pinned bc18d145; captured #101 32 rows / 4.1M lanes 0 mismatches + IR evaluator on 8 rows; CPU selftest 17/17; L40S driver 550 can't run CUDA 13.3 (r20260926-083317-b873), replaced; WAITING r20260926-084023-82c0 (L40S KC GPU selftest) + r20260926-084036-c9fc (verifier build, Dallas 11 ms); next: L40S cell
CHECKPOINT c53d9148 (08:08Z) [open] started: lane flock-ir-sampling (agent bc-0ba89fde-5332-53f9-b622-f1264386f8cb), branch cursor/flock-ir-sampling-f8cb off cursor/flock-ir-lowering-c78f@c53d9148 (PR #54 not merged); design: lane units in-circuit, top-p keep + noise native cut words; next: lane pieces + unit

## FINAL

~~~text
tip: cursor/flock-ir-sampling-f8cb @ af0bd416 (base cursor/flock-ir-lowering-c78f@f4cd5d4e)        merge-with: cursor/flock-ir-lowering-c78f@f4cd5d4e (PR #54, first)
known-failures: none                                        pod: terminated 09:22Z; ~$5 of $10
artifacts: art:a330c568 art:26b5f7d8
~~~

PR #65 (draft) lowers GumbelTopPTokenSelect_v1{V} (#101's sampling) onto C-Flock under frame-v3 as `verity/flock-ir-sampling/v1`, and registers two cells on the captured #101 set (art:ea781b02):
- **L40S** (the served GPU; census id `gumbel-top-p-token-select/v128256/fp32`): art:a330c568, 0.500 rows/s at the 8-row plateau.
- **H100** (optional): art:26b5f7d8, 0.537 rows/s.
- Both run with a separate verifier pod, both `bench.cell check`s are clean, and both pass the interaction rule. They wait for red-team-flock-2's label.

- **Lowering.**
  - One lane unit per vocabulary lane, lowered gate by gate from the Definition's three scan composites. It has 5,099 ANDs, is pinned at bc18d145, and uses numpy-exact pieces, NaN payloads included.
  - Native public cut words: the top-p keep bits (TopPMaskWordx's own reference on the public tempered row), the Gumbel noise and the temperature row scalars.
  - Scope decision, for the coordinator and Daniel: top-p and noise are verifier-native, and the tempered row is public.
- **Exactness bar met.**
  - All 32 rows of captured art:ea781b02 and of synthetic art:ccc8afba (4,104,192 lanes each) go through the lane netlist with 0 mismatches and every lane satisfied.
  - The full IR evaluator agrees on 8 and 6 rows.
  - Evidence: `evidence/20260926T0835Z-captured-101-exactness.json`, `evidence/20260926T0852Z-synthetic-101-exactness.json`.
- **Selftests.**
  - CPU 20/20, including three IR6 load tampers (IR6 is implemented at this statement version).
  - L40S GPU all-pass at the tip: r20260926-091906-6381.
  - `evidence/20260926T0922Z-selftests.txt`.
- **Code layout.** The statement is its own module and binary (`ir_sampling.rs`, `flock-ir-sampling`): the granted v2 at c53d9148 plus the sampling delta. The cells ran at f70c6c77, where the same code sat inside flock-ir-frame. For the same file the split binary gives the same statement digest and Σ. flock-ir-lowering's v3 (f4cd5d4e) is merged in with no Rust conflict; the merged tree passes 495 tests.
- **Handoffs received:**
  - `20260926T0900Z-handoff-from-flock-ir-lowering.md` (their v3 and attention pieces; acted on: merged, the test_cell example switched);
  - `20260926T0925Z-handoff-from-flock-ir-lowering.md` (rebase onto v3; answered in `lanes/flock-ir-lowering/20260926T0924Z-handoff-from-flock-ir-sampling.md`: kept as a sibling module until v3 is granted).
- **Handoffs sent:**
  - red-team-flock-2 review request, `20260926T0922Z`;
  - coordinator merge request, `20260926T0923Z`;
  - flock-ir-lowering, `20260926T0841Z` and `20260926T0924Z`.
- **Pods.**
  - Terminated: vy-flock-ir-sampling-l40s (Sweden, driver 550, useless for CUDA 13.3; now in `kb/flock-prover.md`), -ver (Taiwan, 300 ms away), two Iceland CPUs, -l40s2 (KC), -ver2 (Dallas), -h100 and -hver (EUR-IS-3).
- **Follow-ups (not done):**
  - noise in the circuit (the lane would exceed 2^16 rows beside its compression, so it needs a separate unit table);
  - a Rust port of TopPMaskWordx, so the Rust verifier checks the keep bits itself instead of `check_native`;
  - folding the statement into flock-ir-frame v3 once v3 is granted (`flock-ir-sampling/v2`, with new cells);
  - a non-producer verify of the two cells.
