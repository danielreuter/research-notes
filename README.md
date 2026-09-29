# Research notes

Lane reports, handoffs, findings and drafts, kept OUTSIDE the code repositories (this is not the Verity repo; code, tests
and maintained docs live in `verity-main`).  Architecture decisions live in Notion.  Evidence and renders live in the
evidence store, never here: cite them as `art:<id>`.

- `lanes/<lane>/<YYYYMMDDTHHMMZ>-<kind>-<slug>.md`: one note per file, YAML front-matter with `id`, `campaign`, `lane`,
  `kind` (report | handoff | finding | draft), `status`, `repo`, `origin`.
- `campaigns/<campaign>/`: `BRIEF.md`, `MIGRATION.jsonl` (origin -> note/asset), `ledger/` (overhead ledger copy).

Cite a note by its id, e.g. `note:r20-proof/red-team-vu/20260922T1042Z-report-redteam-vu`.  Ids are stable; do not rename
files.

## Evidence that used to be here

On 2026-09-29 the files under `renders/`, `campaigns/*/assets/` and `lanes/*/evidence/` whose bytes the evidence store
holds (4,401 files, 70 MB; each checked by its sha256, size and MD5 against the store) left the tree.  A `notes-asset:<path>`
citation, or a path in an older note, still resolves two ways:

- the store: the index `art:4bedc7b053caaa80c0105fa9346ee799b00cbdb09a2492879b459e85092e35d9` has one line per file,
  `{path, sha256, bytes, art, member}`; `research data fetch <art> --path <member>` restores it;
- history (never rewritten): `git show "$(git log -1 --format=%H --diff-filter=D -- <path>)^:<path>"`.

Files the store did not hold stayed (mostly `renders/`); `research notes sync` keeps new ones out.
