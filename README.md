# Research notes

Lane reports, handoffs, findings, drafts and their evidence, kept OUTSIDE the code repositories (this is not the
Verity repo; code, tests and maintained docs live in `verity-main`).  Architecture decisions live in Notion.

- `lanes/<lane>/<YYYYMMDDTHHMMZ>-<kind>-<slug>.md`: one note per file, YAML front-matter with `id`, `campaign`, `lane`,
  `kind` (report | handoff | finding | draft), `status`, `repo`, `origin`.
- `campaigns/<campaign>/`: `BRIEF.md`, `MIGRATION.jsonl` (origin -> note/asset), `ledger/` (overhead ledger copy),
  `assets/<lane>/...` (JSON, plots, run outputs).

Cite a note by its id, e.g. `note:r20-proof/red-team-vu/20260922T1042Z-report-redteam-vu`; cite evidence as
`notes-asset:campaigns/r20-proof/assets/<lane>/...`.  Ids are stable; do not rename files.
