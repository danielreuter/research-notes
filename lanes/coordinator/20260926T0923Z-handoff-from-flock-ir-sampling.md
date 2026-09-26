---
lane: coordinator
kind: handoff
from: flock-ir-sampling (bc-0ba89fde-5332-53f9-b622-f1264386f8cb)
created: 2026-09-26T09:23Z
---

# flock-ir-sampling: merge-ready: PR #65 @ af0bd416, which contains PR #54 @ f4cd5d4e, so merge #54 first. Sampling's L40S cell is art:a330c568, with an optional H100 cell art:26b5f7d8. Red-team review requested; all pods terminated; about $5 of $10 spent

**Merge.** PR #65, branch `cursor/flock-ir-sampling-f8cb` @ af0bd416. It merges flock-ir-lowering's f4cd5d4e (their v3) with no Rust conflict. On top of it:
- the sampling statement `verity/flock-ir-sampling/v1`, in its own module and binary (`live/src/ir_sampling.rs`, `bin/flock-ir-sampling.rs`);
- `verity_flock/ir_sampling.py`;
- the template module `templates/gumbel_top_p_token_select.py`;
- `pod/34-ir-sampling.sh`;
- small hooks in the shared files: `ir_lower.lower_gates` takes a pieces map; `ir_frame.serve_args`; `ir_bench` dispatches staging per template; `33-ir-cell.sh` builds `flock-ir-sampling` for sampling; C-interactive registers an IR cell's verifier binary from its result;
- tests: `test_lowerings` and `test_cell` updated, since sampling is now lowered.

The merged tree passes 495 tests (`backends/flock/tests` + `backends/numerical/tests/bench`). Known failures: none in those suites.

**Cells** (`bench.cell`; both checks are clean and pass the interaction rule; NON_ZK_PROOF, 2^-195.4):

| cell | plateau | e2e | rows/s | RTT | art |
| --- | --- | --- | --- | --- | --- |
| **L40S**, `gumbel-top-p-token-select/v128256/fp32` + frame-v3/blake3-keyed, captured #101 art:ea781b02 (prover r20260926-084507-3ae9, separate verifier r20260926-084457-7a06) | 8 rows, 1 proof | 16.0 s | 0.500 | 11.2 ms | art:a330c568 |
| H100, same set (r20260926-085143-1253 / r20260926-085104-58db) | 8 rows, 1 proof | 14.9 s | 0.537 | 0.18 ms | art:26b5f7d8 |

- The L40S verifier is in Dallas and the prover in Kansas City: no pod of any kind was free in the prover's datacenter. The interaction rule holds at the run's own RTT.
- The first L40S, a community host with driver 550, can't run CUDA 13.3 (r20260926-083317-b873). The fact is in `kb/flock-prover.md`.
- The cells ran at f70c6c77, where the statement sat inside `flock-ir-frame`. For the same file, the split binary gives the same statement digest and Σ. They wait for red-team-flock-2's `proof_class` label.

**Decision for you / Daniel (scope of "proven").** The top-p mask is native: `TopPMaskWordx{V}`'s split pipeline runs the measured MUFU EX2/RCP tables over whole-row reductions, and nothing here lowers it. The verifier evaluates it on the public tempered row, and the Gumbel noise likewise.
- So the proof binds the committed logits row to the sampled token, and proves the lane work in the circuit: temperature, mask select, noisy add, first-max chain.
- The tempered row is public (NON_ZK). The census may want to count sampling as partially covered. The review request asks red-team-flock-2 whether the native tail is acceptable.

**Exactness** (the flock-ir-lowering bar):
- 0 mismatches over all 32 rows of captured #101 and of synthetic art:ccc8afba: 4,104,192 lanes each through the lane netlist;
- the full IR evaluator on 8 and 6 rows (`lanes/flock-ir-sampling/evidence/`).

**Other lanes:** the review request is `lanes/red-team-flock-2/20260926T0922Z-handoff-from-flock-ir-sampling.md`. flock-ir-lowering has a note on the shared-file hooks (`lanes/flock-ir-lowering/20260926T0841Z-handoff-from-flock-ir-sampling.md`).
