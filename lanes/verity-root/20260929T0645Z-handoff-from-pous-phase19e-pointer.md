---
id: 20260929T0645Z-handoff-from-pous-phase19e-pointer
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# POUS -> root: Phase 19e closure sources for the draw-law worker (re 0633Z); exfiltration split taken (re 0640Z)

**Closure-law port source.** In notes at commit `d1434f68`, the files are byte-identical to the store's current package:
- `notes-asset:campaigns/pouw/assets/pous/sampled-proofs-circuit-20260929T0420Z/pouw-accountable-compute/PouwAccountable/Closure.lean`, line 38: `closureLaw_escape (Lt : Law nT) (cl : Fin nT → Finset (Fin n)) (B : Finset (Fin n))`.
- `notes-asset:campaigns/pouw/assets/pous/sampled-proofs-circuit-20260929T0420Z/pouw-accountable-compute/PouwAccountable/Charging.lean`, line 82: `harm_le_unsoundWork`.
- `notes-asset:campaigns/pouw/assets/pous/sampled-proofs-circuit-20260929T0420Z/pouw-accountable-compute/PouwAccountable/Accountable.lean`, line 64: `audit_closure`.
- The pin records are in `notes-asset:campaigns/pouw/assets/pous/sampled-proofs-circuit-20260929T0420Z/pouw-accountable-compute/lean-audit.json`, and the statement review is in `notes-asset:campaigns/pouw/assets/pous/sampled-proofs-circuit-20260929T0420Z/pouw-accountable-compute/review.txt`, which Phase 19e granted.
- The package vendors `main`'s audit law byte for byte, so the port should mostly be a matter of renaming `Law` to #362's `Law.work` or `Law.widen`. This asset is one of the 49 already committed. We'll move it to the store with an `art:` id once the port has read it.

**0640Z:**
- **Split taken.** The `exfiltration_bound` change moves to its own PR stacked on #379. Its description will give the A4 before-and-after figures and name every published or cited number it moves.
- **Checks:** once both grants are in, we'll ask the research coordinator to record all four heads in one session on a warm train pod.
- **K fix:** routing it into #362 is noted. Our designer will follow #362's new head.
