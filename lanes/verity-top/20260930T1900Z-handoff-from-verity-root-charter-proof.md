---
id: 20260930T1900Z-handoff-from-verity-root-charter-proof
campaign: verity
lane: verity-top
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Charter: proof (sampled-proof backend, prover efficiency, proof systems, Lean)

Replies to `note:20260930T1842Z-handoff-from-verity-top-charters`. State as of 19:00Z Sep 30.

- **Owner:** research coordinator `bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628`. **Stays** on as subcoordinator. verity-root hands it any proof state it holds.
- **Remit:** C-Flock (M0 prover, M1 masked prover, the verifier of record), prover overhead, new proof systems, their Lean proofs, red team, and consolidation of core. **It also runs every merge train through `research merge` for now.**

## Workers
| lane | id | owns |
|---|---|---|
| C-Flock M0 | `bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a` | prover overhead: best 7.89×10⁶× native prefill; `flock-m0-v3` draft #554 |
| M1 masked prover | `bc-2a9978cc-cafd-5d88-a4de-888a71d85659` | multi-table ZK sessions |
| Flock verifier | `bc-8e519ca0-db91-5212-bb38-5b9865237ab3` | #434 → #430 → #441 |
| GEMM relation (Lean) | `bc-590cc416-b61a-523d-84f5-280ce207a815` | #538, #550 (PlacedWF) |
| value binding (Lean) | `bc-a84aadb3-b06e-5db9-b0e4-e63614938d81` | #526, #520 |
| table / session ZK (Lean) | `bc-7bf99d94-2cfe-5639-8b30-4de8d243b379` | #519, #560 (on main) |
| verifier refinement | `bc-159ce83b-d3da-5f5d-921a-fae1057fcddd` | #426, #432 |
| Flock soundness / audit-lean | `bc-9e538dc5-64c5-5aad-b845-7ae98c178569` | `setupH_flatPlacement` pin after #434 |
| audit-level integrity | `bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568` | #424, #430, #441 |
| draw law | `bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba` | #427, #429 fallback |
| red team | `bc-f0bc7e75-356e-5c24-a081-9c374b3aac26` | grants (`red-team` role) |
| ZK public / private | `bc-b483c71e-c321-599b-b63b-e4cc0dccb710` / `bc-d7554c77-cc0a-5808-975d-2195e08160aa` | ZK write-ups |
| consolidation | `bc-e373566b-e6f1-5c72-88c3-86eec290ac68` | #228, #250 (MUFU tables to `verity.ml.mufu`) |
| backend-sweep-2 | `bc-62b7c7a1-9d2c-5669-9b01-1d4d148b2ced` | backend sweep as node-1 GPU backfill |
| flock-v4-design | `bc-8a7dff1c…` (full id in `lanes/flock-v4-design/`) | prover v4 design |

## Open items (**D** = needs Daniel)
- Trains: consolidation #228/#250, then the held vLLM PRs, #434 → #430, #441, #329 last.
- GEMM-hash plan levers (target about 6.8×10⁶× native).
- The unmasked protocol's completeness is still a hypothesis.
- **D:** the next circuit-privacy milestone.
- **D:** the four Lean-organization items (including the rename-proof hash).
- **D:** close #367 and POUS's #372/#380/#391 (held).
- **D:** who runs trains after the split: RC, or Job queue stage 1 under infra.

## Hands to infra
- The merge-train machinery (the result cache, pod preflight, the clean-host guard #531), and Job queue stage 1 once it runs a train end to end.
- The `provers` queue and backfill scheduling.

## Where state lives
- Inbox `lanes/coordinator/`; lanes `flock-*`, `red-team-*`, `audit-lean`, `consolidation`, `backend-sweep-2`, `lean-*`.
- The verity-root store's `docs/`: `gemm-hash-cost-plan.md`, `lean-organization.md`, `zk-proof-public.md`, `zk-proof-private.md`, `post-quantum-security.md`, `consolidation-status.md`, `merge-log.md`.
