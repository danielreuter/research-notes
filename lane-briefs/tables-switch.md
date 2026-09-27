---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Lane tables-switch: publish the new-spec tables at the 6 PM PT render (the labelled switch), and add a Flock column

Budget $10 (CPU only; the renders run on vy-control-verity through the coordinator) · **merge-ready by 5:30 PM PT (00:30Z)** ·
base `origin/main` (`270b0de2` or later) · branch `lane/tables-switch`.
Read first: `internal/lane-briefs/cloud-lane-setup.md` (sections 1, 5, 6), `$RESEARCH_NOTES/kb/TABLES.md` (the spec,
especially "Render" and "The switch"), `docs/proof-optimization-tables.md` (today's preview and each cell's history).

## Decisions (Daniel, 11:17 AM PT)

1. **Publish the new-spec tables as the default at the 6 PM PT render.** The frozen tables stay available as a drill-down.
2. **Flock is its own backend family:** Table 2 (and Tables 1 and 3) gets a **Flock** column. Lane `flock-backend`
   (bc-d3ca695f) is building `backends/flock` and the first pure-Flock cell.

## Deliverables (one merge-ready handoff to `lanes/coordinator/`)

1. **Parity (TABLES.md "The switch", condition 2).** The new views, rendered with today's parameters, must select exactly
   the cells of a `tables --snapshot` taken for the purpose, with the same artifacts and ratios. Today's parameters are:
   a 2^-128 filter, batch 4,096, K = 1536, the bare and "+ in-proof hash" columns with Poseidon2 per row and no sharing,
   and proving time only. Check `backends/numerical/tests/bench/test_views.py` for what already exists; PR #27's author
   said "parity passes". Make it one command whose output is recorded as an artifact, and give the coordinator the
   exact command to run on the control pod store.
2. **The published default.** Today the steward's `[[render]]` entries (`research.notes.render_lines`, `steward.toml` in
   the notes root) render `tables` and `drilldown`, plus `views` as a preview when `preview = true`. After the switch the
   views are published as `<stamp>-tables.md`, and the frozen tables become a drill-down (e.g. `<stamp>-tables-frozen.md`).
   Choose the smallest change: an entry option such as `published = "views"`, with a test in `tools/research/tests/test_notes.py`.
   Give the coordinator the exact `steward.toml` edit.
3. **The switch digest:** a generator, or at least a documented recipe, for the 6 PM PT digest labelled as a change of
   method. It shows each old published number beside its replacement, or beside the reason it left Table 2. The
   coordinator runs it and posts it.
4. **Changelog:** a `CHANGELOG.md` entry, in `backends/numerical/` unless one already exists elsewhere (it's on the
   maintained-docs list in AGENTS.md). Cover the switch, the method change and the new Flock column.
5. **Flock column:**
   - Add the family to the views (Tables 1–3) and to `kb/TABLES.md` (edit the kb doc in place and bump its version line).
   - A pure-Flock configuration (relation plus hashes in one binary-field circuit) goes in the Flock column.
   - Route (a) (A-GKR prime side + Flock hashes + the link) stays in the A-GKR column with a note. If you think it
     belongs elsewhere, say so in the handoff; don't decide it yourself.
   - Agree the result-record fields (family/backend key, profile, security bound) with flock-backend: a handoff to
     `lanes/flock-backend/`. Its first cell should render without renderer changes.
   - Until a Flock result exists, the column renders `—` with its reason.

## Rules

- No pods needed. Tests: `backends/numerical/tests/bench` (265 pass today) and `tools/research/tests/test_notes.py` on the merged tree.
- Frozen tables must render byte-identical, apart from the file they land in.
- One merge-ready handoff (tip, tests, the parity command, the steward.toml edit, the digest recipe). Keep checkpoints short.
