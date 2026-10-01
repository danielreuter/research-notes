---
id: 20261001T0202Z-handoff-from-bc-69c09d42-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-69c09d42, PoUW assumptions table owner
---

_Relayed verbatim from the Cursor store by old-accounting (bc-b729c175): the author's VM gets a 403 pushing to research-notes._

# bc-69c09d42 (PoUW assumptions table owner): migration handoff. Nothing in flight; one document to take over

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`, 7:05 PM PDT.

**What I did:** I owned the PoUW security-assumptions table, at
`/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/assumptions.md` (about 1,630 lines). I folded the
assessor's (bc-d7d4b0d1) ratings and the lanes' results into it, kept its per-line "weakest rating" column current, and kept
it consistent with the panel's `lines.json`. I wrote no code and ran nothing.

**1. Branches and PRs:** none. I own no branch or PR in `verity` or elsewhere.

**2. Runs and jobs in flight:** none. I have no research runs and no fill jobs, so I have nothing to preserve.

**3. Half-done state:**
- **The table** (store, above). It's current through the assessor's 6:36 PM PDT line and Daniel's 5:52 PM PDT rulings. Just now
  (7:02 PM PDT) I fixed the kept item "assumptions-table lead", and v2-hot now leads with "not under 1%":
  - γ ≥ 0.951% packed and ≥ 1.226% as written on the full catalogue, a rising floor (bc-3006c44a, 6:00 PM PDT);
  - the no-charge route, 0.371% packed, is pending fix (2);
  - v1, at 0.519% packed, is the only FP8 line under 1%;
  - the FP4 TT_OUT grant at C (6:36 PM PDT) and v1's full-catalogue B (5:30 PM PDT) are in.
- **My note to the assessor:** `internal/pouw/table-owner-notes-for-assessor.md` (store). Items 1–6 are old, and nothing in it is
  open.
- **The column checker:** `internal/pouw/assumptions-table-column-check.py` (store; copied from my VM just now). It's the one VM-only
  tool worth keeping. The rest of my VM state is throwaway edit scripts under `/tmp`.
- **A relay file**, `internal/pouw/accounting-reply-from-69c09d42-assumptions-table-rulings.md` (store). It's already posted
  (notes `53cd3d18`) and can be deleted.

**4. Next steps for the kept item** (the table):
- **Fold each result as it lands:**
  - **GPU 3's fix (2).** If it fails, v2-hot is parked and its lead says so. If it passes, the assessor rates the no-charge basis,
    and the lead moves to 0.371% packed only then.
  - **The padded clause (b) re-search,** which stops if fix (2) fails.
  - **The W1 off-pipe microbenchmarks** (bc-9221952f, then the assessor's rating of `w1-complete/sm120`). That rating is every FP8
    line's only C, so it moves every FP8 line's weakest.
  - **RowSeed's named Prop.** The row is `rowseed-per-row-draw/pearl-c-sm120`, which waits on M3's re-GO.
  - **B-OVF enforced** in #556 and #580. That lifts Pearl-C4's small-n flag and widens the FP4 grant to 128 ≤ n < 4,096.
  - **The served-path beacon test,** after which served runs can cite `beacon-unpredictability/drand-quicknet` at A.
- **The panel's seven differences** are listed in §5 for bc-2aa33ad8. Recheck them against `lines.json`, since the panel has fixed
  v2-hot's lead since then.
- **What I'd stop:** the long "Also new" history in the summary. It has grown past usefulness. I'd prune it into a dated history
  section, and keep the lead, the per-line table and §5 as the live parts.

**5. Traps:**
- **The file's frontmatter names me** (`subagentId: bc-69c09d42-…`). Under the store's rule, another agent may not edit a document
  whose frontmatter names someone else. Before my successor edits it, @old-accounting or compute-accounting should re-attribute the
  frontmatter to them, or the successor should start a new file and cross-link it.
- **Never rename an id.** A restated statement gets a new id, for example `post-add-bound/sm120-preadd`,
  `no-aligned-exact-region/sm120-unpromoted-hot-t6` and `rowseed-per-row-draw/pearl-c-sm120`. A row at other parameters is a
  different assumption.
- **Table rows break easily.** A `|` inside a cell (an escaped pipe, a magnitude bar) or a bulleted list inside a cell breaks the
  column count. Run the checker before every write, and write back only when it reports `errs 0`.
- **Store writes can fail with EAGAIN.** Retry the copy. Compare the store copy against your base before writing, then `cmp` after
  writing.
- **The assessor's words go in rating cells,** and pending stays pending: mark a rating closed only when the assessor posts it.
  Only the assessor writes in `internal/pouw/red-team/`. The table owner's notes to it go in
  `internal/pouw/table-owner-notes-for-assessor.md`.
- **Times:** write new text in Pacific time with the zone shown. Older entries carry UTC. Two assessor lines stamped
  2:48 PM PDT were written at about 2:28 PM PDT (its 2:42 PM PDT correction).
- **0.371% labels:** every mention must read as v2-hot's no-charge figure, conditional, or as v2's retired D figure. None may read as a
  standing v2 figure.
- **Recompute the weakest column** whenever a cited row moves. Bump the "Consistency" bullet's time on each fold.
- **This VM gets a 403 on research-notes pushes.** Stage replies in `internal/pouw-fp8/accounting-outbox/` under the lane filename.

**After this:** I start no new work, and I'll answer my replacement's questions here.
