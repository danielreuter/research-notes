---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75) · to: verity-root / the research coordinator
(bc-8ece7cde); cc POUS (Lean lane bc-e7e2bf3a) · created: 2026-09-29T19:50Z

# #425 restacked on #427, at `c4499c8c`: CONFIRMED

The delta keeps my `7fd7e0b9` grant, and #425 can go to train TX.

Re: `internal/lanes/verity-root/20260929T1912Z-handoff-from-pous-425-restacked-on-427.md`, on my grant
`internal/lanes/pous/20260929T1900Z-redteam-425-keyed-draw.md`. I fetched the branch head `c4499c8c` directly; #427's
granted `5550fd7c` is an ancestor. Evidence is in the store's `private/red-team-reviews/pr425-restack-evidence.log`.
CPU only, $0.

## Checks

- **Build:** both packages build.
- **Axioms:** `#print axioms` over all 128 pins gives only the standard three.
- **Audit:** `audit.py` passes with kernel replay: 10,541 declarations in 154 modules, 128 pins. That is one module
  fewer than `7fd7e0b9`'s 155, the deleted `WindowCompiled`.
- **Tests:** 48 passed across `test_repository.py`, `test_lean_packages.py`, `test_lean_verifier.py`,
  `test_randomness_spec.py` and the claims tests.

## The delta is what the handoff says

It is three commits above `7fd7e0b9`: #427 merged at `dff428ad` and then at `5550fd7c`, and A5's wording.
- **The duplicate is gone.** `Audit/WindowCompiled.lean` is deleted, and its import leaves the root. `KeyedDraw.lean`'s
  only change is the import from `Audit.WindowCompiled` to `Audit.Window`. So step 4 now cites #427's
  `extraction_audit_window_of_le_slack` and `extraction_audit_window_split_of_record_of_le_slack`.
- **#427's copy is untouched.** `Audit/Window.lean` is byte-identical to `5550fd7c`'s.
- **A5's text.** `Assumptions.lean`'s change is A5's docstring alone. `UniformSecret`'s `Prop` is unchanged. The
  docstring and `ASSUMPTIONS.md` now carry the platform wording I suggested on #423:
  - Linux, with CPython 3.12 or later;
  - `secrets` reads `getrandom(2)` and blocks until the kernel CSPRNG is initialized;
  - there is no user-space state, so forks don't repeat;
  - a restored snapshot is safe only with vmgenid reseeding or a hardware RNG;
  - the CSPRNG is idealized as uniform, with a negligible distinguishing advantage;
  - re-read all this on any other platform.
- **`Audit/README.md`** changes only its text.

## The audit record is `7fd7e0b9`'s, in content

- It has the same 128 pins, and every pin record is semantically identical.
- In `reads`, every module digest, all 1,158 definition hashes and every module's pin set match. The other sections
  are equal too.
- The 565-line file diff is serialization only. For example, three records (`countRule_eq_draw`, `workRule_eq_draw` and
  `execArith_correct`) now wrap a one-element `signature` list. So the record is not byte-identical, but no record's
  content moves.
