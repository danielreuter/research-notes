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

On 2026-09-29 every file under `renders/`, `campaigns/*/assets/` and `lanes/*/evidence/` left the tree: 5,033 files, 281 MB,
each in the evidence store first and checked there by its sha256, size and MD5.  A `notes-asset:<path>` citation, or a path
in an older note, still resolves two ways:

- the store: the index `art:92e189514c344a4e6abce0c22bd53b3ba55de1cbf9763d57be531698fb8f58ae` has one line per file,
  `{path, sha256, bytes, art, member}`; `research data fetch <art> --path <member>` restores it;
- history (never rewritten): `git show "$(git log -1 --format=%H --diff-filter=D -- <path>)^:<path>"`.

`research notes sync` keeps new ones out: evidence goes to the store (`research data put --kind evidence/v1 ... --preserve`).
