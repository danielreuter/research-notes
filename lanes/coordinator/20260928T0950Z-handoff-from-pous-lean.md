---
lane: coordinator
kind: handoff
from: pous-lean
created: 2026-09-28T09:50Z
---

# pous-lean → coordinator: the four POUS PRs have passing checks at their new tips, but main moved to 3ba4d8b3 meanwhile (#149, an AGENTS.md conflict). How do you want to take them?

This supersedes `20260928T0446Z-handoff-from-pous-lean.md` (the tips, and the train question) and `20260928T0427Z` (the
old SHAs). I own landing all four, including the reference worker's two branches, which I have taken over; every change
is a merge commit.

- **Chain:** `main@6746f408` ← #162 ← #183 ← #166 ← #196. Each branch contains the one before.
- **Recorded `check`, passed at each tip, clean tree, PRESERVED on R2.** Each covers pytest, `circuit-check`,
  `lean-build`, `lean-unit-cut`, and `lean-audit` over every Lake package: Flock's three packages (`soundness` 4,638
  declarations) and POUS.
  - [#162](https://github.com/danielreuter/verity/pull/162) `4ef7bbc8`: `r20260928-043314-e1ee`.
  - [#183](https://github.com/danielreuter/verity/pull/183) `26f0f92d`: `r20260928-061856-643d`. Its `PROTOCOL.md` now
    makes the band graph with `d = 12` the secure-first scheme (Daniel, 01:10Z), with dense selectable.
  - [#166](https://github.com/danielreuter/verity/pull/166) `be77ec58`: `r20260928-080435-909e`. `PROTOCOL.md` is resolved
    into one band-default document. The GitHub base is retargeted to #183's branch.
  - [#196](https://github.com/danielreuter/verity/pull/196) `ca17ec0f`: `r20260928-085551-84e9`.
  - An earlier #166 tip, `d7e2c36f`, failed (`r20260928-073654-b3f8`). `protocols/tests/test_protocol_boundaries.py`
    scanned `protocols/pous/lean/.lake`, where Mathlib's Python scripts live once the Lean package is built. The fix, in
    `be77ec58`, makes the scan skip dot-directories. It touches a shared test outside `protocols/pous`, so please look.
- **`main` moved past all four during the checks,** to `3ba4d8b3` (`train-docs-merge`), so the gate refuses these tips.
  The next round needs two things:
  - **`AGENTS.md` conflicts** between #162's one-line `protocols/pous` entry and the train's changes.
  - **#149 is in**, so POUS's `lean-audit.json` must be re-recorded. The records' signatures now print without notation.
    I'll confirm every `type_hash` is unchanged, which makes it text-only.
- **The question:** how do you want to take them?
  1. **One merge of the chain.** I merge `3ba4d8b3` into all four (`AGENTS.md` resolved, records re-recorded) and record
     one check at #196's tip. Then `research merge cursor/pous-public-encoder-9796` lands all four. This is the fastest
     against a moving `main`, and my default.
  2. **The same, with separate merges.** I record a check at each of the four new tips, about 4 h on my VM.
  3. **Your own train** from these tips. Then I won't push to these branches until you say.

  Please answer in `lanes/pous-lean/`. Until then I'm not pushing to the four branches, so a train can take them as they
  are.
- **Also:** #166 changes `tools/research/tests/test_pythonpath.py` (`protocols/pous` joins the uv workspace). bc-13eada34,
  stacked on #166/#196, needs to merge the new tips.
