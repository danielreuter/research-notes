---
id: proofs/20261002T1022Z-finding-pr806-round2-statement-review
campaign: e2e-guarantees
lane: proofs
kind: finding
status: open
repo: verity
origin: proofs bc-8416bc72
---

# #806 round 2 (`cursor/zk-lean-cr-only-95d4` @ `ade0a711c`): statement re-review APPROVE

Reviewer @proofs read round 2's `audit.py --update` output (`internal/proofs/zk-lean-cr-only.md`, "Round 2: `audit.py
--update` output (verbatim)"), at the tree of `ade0a711c`, which contains main `9699b2f28` (merge `19494d6a5`). PASS,
12784 declarations, 252 pins, axioms propext/Classical.choice/Quot.sound. Two records changed, two added, no `reads` group
moved, nothing removed. Round 1's 29 pins (`note:proofs/20261002T0912Z-finding-pr806-cr-only-statement-review`) stand.

- `CROnly.adaptive_prefinal_key` (changed, red-team F3): the only difference is `H : Prod B Cc → D` becoming
  `H : Key → Prod B Cc → D`, read as `H κ` in `hP` and `hI`. Every other token, the conclusion and the bound
  `2·|L|·avg_κ hidingGap (My κ) cs` are identical. The old statement is the special case `H := fun _ => H`, so the new
  one says more: the leaf hash may depend on the uniform key, as hm96-sha512's leaf prefix does.
- `CROnly.adaptive_prefinal_hm96_sha512` (changed): the same single change on the 2047-bit key; bound still
  `2·|L|·2^-257`.
- `CROnly.uprog_e2e_count`, `CROnly.uprog_e2e_drawn` (new, F2): `UProg.flock_e2e_count`/`_drawn` with `0 < t'`, a budget
  `0 < q`, `hCRs : LinkCRStrict … t' q` in place of `hCR`, and `linkBoundE … (strictRunCost t' q)` in the bound: the same
  four-place restatement round 1 approved for the 15 other e2e forms. So every e2e form and the headline now have a
  `cr/sha-512` restatement.
- F1, F4, F5 are documentation; the worker reports F4's docstring changes no record, and the output confirms it.

Grant: `pr:806@ade0a711c29bdbe8cd7e39c9cf4f94d3a44209a8 grant statement-reviewer`. The red-team grant at `0162b6d64` needs
its carry to this head (bc-7b6772b1, after #812). A second main merge follows #792's landing (soundness `ASSUMPTIONS.md`
union); if it moves no record, I re-label there.
