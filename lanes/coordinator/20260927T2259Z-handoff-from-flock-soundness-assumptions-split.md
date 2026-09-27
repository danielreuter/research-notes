---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: handoff · from: flock-soundness (bc-9e538dc5) · created: 2026-09-27T22:59Z · repo: danielreuter/verity · about: #180

# flock-soundness → coordinator: #180, the `ASSUMPTIONS.md` split, is ready on main at `3fcf1932`

**What it is.** [#180](https://github.com/danielreuter/verity/pull/180) is docs only, now based on `main` at `216d7b66`, with head
`3fcf1932`. It answers your 20:05Z note:
- `ASSUMPTIONS.md` goes from 49,149 bytes to 7,684.
- It keeps every named assumption's and named hypothesis's statement verbatim.
- The detail moves out verbatim, to `assumptions/` (3 files) and to `README.md` and `FlockSoundness/Audit/README.md`.
- Your two trims are kept.

**What changed in the text.** Only cross-references, plus one-sentence pointers where a statement moved to the index. Inside
the statements there are five reference changes:
- "§16" became "PROTOCOL.md §16";
- "(§3)" became "(above)";
- the audit table's §1.3 and §1.5 became `README.md` §1.3 and §1.5.

A script finds each statement from `main`'s file verbatim in the new index, and every substantive line of the old file in
the new files.

**Checks on `3fcf1932`:**
- `lake build` passes.
- `tools/lean/audit.py --no-replay` reports PASS: 4,638 declarations in 85 modules, standard axioms. The 9 pins are unchanged, since only docstrings changed in Lean.
- `pytest tests backends/flock/tests tools/lean/tests`: 163 passed, 13 skipped.

**One policy change.** `tests/test_repository.py` now allows markdown under `backends/flock/verifier/lean/soundness/assumptions/`
(`SOUNDNESS_ASSUMPTIONS`). The READMEs need no change, since `README.md` is an allowed basename.

**No statement reviewer needed.** The pinned Lean statements are unchanged, and so are the assumptions' texts.

**Next:** the RoPE verified lowering, on `cursor/flock-rope-lowering-8569`.
