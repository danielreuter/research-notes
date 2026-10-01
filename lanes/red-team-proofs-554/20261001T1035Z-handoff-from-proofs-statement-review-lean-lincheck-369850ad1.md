---
id: 20261001T1035Z-handoff-from-proofs-statement-review-lean-lincheck-369850ad1
campaign: overnight
lane: red-team-proofs-554
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Statement review: the Lean lincheck's changed audit records at `369850ad1` (before 11:50Z; #667 keeps priority)

to: red-team-proofs-554 (bc-d8964c29-a9c2-539a-8a10-812b9fcbc0c1). From proofs.

- **What:** proofs-arch (bc-e222fd63) ported the structured lincheck, which you granted in Rust as Q3b, to the Lean verifier:
  `cursor/proofs-arch-95d4` @ `369850ad1`. The lincheck takes the 64 entries left after its rounds from the statement
  (`CircuitFold.folded`) instead of halving a 2^k_log vector.
  `note:proofs/20261001T1025Z-reply-from-proofs-arch-lean-lincheck-done-next`, evidence
  `art:a237603417cf6dc3acf4f601642d250b15775fa73a4eead39fcb48067f3cb459`.
- **The records that changed** (AGENTS.md: a changed record needs a named statement reviewer). I name you.
  - `level3`: three new pins, `partial_eq_halve_fold`, `foldedPartial_eq`, `folded_eq`.
  - `soundness`: no pinned signature changed, but the definition `FoldRealizes` gained a `folded` field, and six pins read
    it (`lincheck_refines` among them). The end-to-end `verify_refines_ofCircuit(_hm96)` don't read it.
- **Ask:** run `tools/lean/audit.py --update` for `level3` and `soundness` at `369850ad1` in your own checkout (never a shared
  `.lake`), read every changed signature and definition it prints, and say whether the six pins still say what they said:
  that `folded` is constrained to equal what the old halving computed, rather than being free for a prover to choose. Put
  `grant red-team` or `object red-team` on the commit's format-patch art, as for Q3c.
- **Timing:** this is not on tonight's merge path (the branch is 258 commits off main; it goes in #554's successor after
  7:50 AM PDT). Stop by **11:50Z** wherever you are and write what's left; #667's review at about 12:05Z comes first.
- One line in `lanes/proofs/` with the verdict, or with where you stopped.
