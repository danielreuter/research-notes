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

**Verdict: pending; no generated move commit yet.** At 16:29Z the branch is `19a960c8b`: the srcDir fix (`12a031dd8`, #1217)
and the codemod (`tools/move/lean.py`, `lean_map.toml`). Pre-review of the codemod below; one blocking item so far.

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

### Blocking (codemod at `19a960c8b`)

1. **The upstream watch on ArkLib goes vacuous.** `lean.py`'s `merge_locks` starts the proofs lock's `upstream` as
   `{"imports": [], "watch": {}}` and copies each old lock's `imports` and `watch`, but never its `scan`. Soundness's base lock
   has `"scan": {"Arklib": {"baseline": "scripts/axiom_baseline.json", "sources": ["ArkLib"]}}`, and `upstream.pinned()`
   (the audit's no-build pass) iterates `cfg.get("scan", {})` only. Without it the pass scans nothing and reports no failure,
   so the 15 C-Flock watch entries (`A1-johnson-mca`, `udr-mca`, `list-size`, … `live-verifier-custody-tables`) stop
   failing the audit when a pinned ArkLib proves one of them.
   - Fix: in `merge_locks`, `prf["upstream"].setdefault("scan", {}).update(up.get("scan", {}))` (and raise on a name in two
     locks, as for `watch`). Sturdier: `upstream.pinned()` (or the audit) fails a policy whose `watch` is non-empty while
     `scan` names no package, so a lost `scan` can't pass. NCI's base lock already has a `watch` with no `scan` (Mathlib
     only, `loomis-whitney`), so that check would flag it too: pre-existing, and its owner's call.

### Codemod observations (not blocking)

- Every old lock merges into `verity/Security/lean-audit.json` (`proved_in: ["Proofs"]`); `security_proofs` at
  `verity/Security/Proofs` (`srcDir = ".."`) holds C-Flock's proofs as `Proofs.Flock.{Verifier, Level3, Soundness}`. The
  verifier stays a code package (`Flock`, `FlockVerify`, `FlockRows`), and its lock keeps only roots, `meaning`, `escapes`,
  `exempt` and the toolchain.
- C-Flock's assumptions module goes to `Proofs.Flock.Soundness.Assumptions`, inside the proofs package, not to `Specs/`
  as the ruling's layout has it. The audit matches a hypothesis by its constant's module (`audit.py:607`), and the lock's
  list is renamed the same way, so this keeps the check, but the assumptions stay in untrusted, ArkLib-reaching text. Say so
  in the PR, or move them.
- The merged lock's `assumptions` lists every area's modules, so a C-Flock guarantee could now take another area's named
  assumption and pass the hypothesis check. Each record lists its named assumptions, so an existing record can't change
  silently; it widens only what a new guarantee may assume.
- `compile_time`'s `FlockSoundness.Refine.Walk` digest is of the file as reviewed. The import rewrite changes the file, and
  `--update` re-records the digest without a review, so I check that only its import lines change.
- The Mathlib (`5ed29652…`) and ArkLib (`b2e456fc…`) revisions in the generated lakefiles are the base manifests'. The
  `leanOptions` only tighten (`relaxedAutoImplicit = false` added to level3's modules).
