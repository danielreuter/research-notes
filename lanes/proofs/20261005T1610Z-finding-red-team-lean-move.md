---
id: proofs/20261005T1610Z-finding-red-team-lean-move
campaign: layout-move
lane: proofs
kind: finding
status: in-progress
repo: danielreuter/verity
origin: red-team-lean-move
---

# Red team pre-review: the Lean layout move (`cursor/lean-layout-move-c3b2`), red-team scope

**Verdict: pending. The branch is not on origin yet (checked 16:09Z).**

- Brief: proofs coordinator (bc-8416bc72), 9:05 AM PDT. Ruling: thread 1791215694.084699. Move thread 1791216100.963309.
- Base: main `378453fb3` (Layout move #1206).
- Scope: `backends/flock/` minus `README.md`, `PROTOCOL.md` and `*/tests/*` (`tools/check/queue.toml`'s red-team grant), plus
  wherever the move puts C-Flock's soundness and level3 Lean, and the gates keyed by their paths.

## Base inventory (main `378453fb3`)

- C-Flock's records: the verifier (`backends/flock/verifier/lean/lean-audit.json`) 25 guarantees and 26 `reads` modules,
  roots `Flock`, `FlockProofs`, `Main`; `level3/` 56 `pins` and 37 `reads` modules; `soundness/` 757 guarantees, 345 `reads`
  modules, 1 assumptions module (`FlockSoundness.Assumptions`), an `upstream` watch list and one `compile_time` module.
- The red-team grant is keyed on `backends/flock/`; lean-agreement's merge trigger and `agreement_closure` too.

## Findings

(in progress)
