---
lane: coordinator
kind: handoff
from: notes-data-layer
to: research coordinator (bc-8ece7cde)
created: 2026-09-29T07:12Z
status: open
---

# Merge request: #365 #369 #377 #384 #386 (the notes and data-layer fixes Daniel approved); patch the mirror before #386 first runs, or the next pass re-adds 107 handoffs

Daniel approved five small fixes from the knowledge-storage BOTEC, and all five are up as draft PRs. Please run `check` on them,
merge them, and decide the #386 cutover below. No pod was used, and only `check` needs one.

## The PRs

| PR | Branch at | What changes | Stacked on |
|---|---|---|---|
| [#365](https://github.com/danielreuter/verity/pull/365) | `cursor/store-abandoned-label-1cae` at `0905b75c` | an `abandoned` label word | |
| [#369](https://github.com/danielreuter/verity/pull/369) | `cursor/notes-sync-header-check-1cae` at `59836839` | sync checks front matter | |
| [#377](https://github.com/danielreuter/verity/pull/377) | `cursor/notes-sync-citation-check-1cae` at `13c10014` | sync checks citations after a push | #369 |
| [#384](https://github.com/danielreuter/verity/pull/384) | `cursor/notes-mcp-catalog-1cae` at `ef77007d` | notes search and evidence joins over MCP, and a compact catalog | |
| [#386](https://github.com/danielreuter/verity/pull/386) | `cursor/notes-archive-month-folders-1cae` at `5bb85870` | `research notes archive` | |

What each one does:

- **#365:** `research data label` writes `abandoned` only with `--ref` naming the note that says why, as
  `note:<lane>/<name>` or `note:<campaign>/<lane>/<name>`.
- **#369:** `research notes sync` refuses broken front matter: an unclosed block, a line that isn't `key: value`, or a
  `created:` that isn't UTC. It warns on a `lane:` or `created:` mismatch. Only new content is judged.
- **#377:** after a push, sync warns (`SYNC-WARN`, never a refusal) for each pushed note that cites a run or an `art:` id the
  store's remote lacks. It checks at most 64 ids and spends at most 20 s per sync; `RESEARCH_NOTES_CITE_CHECK=0` turns it off.
- **#384:** `research notes index` and `research notes mcp` give full-text search over the notes, joined to the catalog, over
  MCP on stdio. `research data catalog --compact OUT` writes a copy of the catalog for readers that only query it.
- **#386:** `research notes archive LANE` moves a lane's older notes into month or day folders. It does nothing until someone
  runs it with `--apply`.

#365 has merged main `bb64e78d`. Its one conflict was in `test_store_vocab.py`, where main added a `grant` key on the
neighbouring line; the merge keeps both keys. The five then merge cleanly onto `bb64e78d`. On the merged tree, run on this VM,
`tools/research` passes 577 tests and skips 1, and `tests/test_repository.py` passes 11. Nothing touches circuits, Lean or
`backends/flock/`, so `lean-agreement` doesn't apply.

## #386's cutover needs your OK, and Daniel's

It departs from the BOTEC. The BOTEC said new files would go into month folders and existing files would stay; #386 instead
moves older notes and leaves writers alone. There are three reasons:

- **Writers.** Dozens of lanes, the mirror and the steward write into `lanes/coordinator/` using the contract's path.
  Redirecting new files means changing every one of them, and a lane that missed the change would write to the old place.
- **Size.** A month of your folder is 4,500 to 8,400 files, past GitHub's 3,000 per directory, so you need day folders either way.
- **Readers.** `inbox`, `status` and `mail` list only the top level, so they don't change.

The cost is paths. A note's id is its file name, and that doesn't change, but a path in an older note goes stale.

I measured it on a copy of today's notes (`74aaff3a`), with nothing pushed.
`archive coordinator --by day --older-days 3` moves 263 notes stamped before 09-26T06:58Z, in 0.35 s. Every move is a pure
rename. That leaves 641 entries at the top level, 632 of them recent, and the day folders hold 10, 44, 151 and 58. No file name
appears twice. Of the 271 distinct `lanes/coordinator/<stamp>-…` paths the notes cite, 99 would no longer exist at that path.
#384's `read_note` resolves the same 267 of them before the move and after it.

If you'd rather have the BOTEC's version (new files go to month folders), say so and I'll build it instead.

### Procedure

1. **Patch the mirror first.** `cloud-mirror-control-pod.sh` sends a store handoff with `--ignore-existing`. Once a handoff has
   moved into a month folder, its top-level path is empty, so the next pass would send it again. After the `ex=` line, add:

   ~~~bash
   # names `research notes archive` moved into a month folder: never forward them to the top level again
   arch=/tmp/cloud-mirror-archived.rules
   names=$(timeout 120 $sshcmd "$host" "cd $N && git ls-files -- 'lanes/*/20[0-9][0-9]-[0-9][0-9]/*'") \
     || { echo "$(stamp) FAIL archived names: ${names: -300}"; exit 1; }
   awk -F/ 'NF {print "- /lanes/" $2 "/" $NF}' <<<"$names" > "$arch"
   ~~~

   Then add `--filter="merge $arch"` right after `--filter="merge $ex"` in both forward rsyncs (`fwd` and `fwdh`), so it comes
   before their include rules. I tested it with rsync 3.2.7 on a copy of the store's `internal/lanes/coordinator/` names
   against the archived copy. Without the rules the handoff pass would create 108 files at the top level: the 107 archived
   handoffs from cloud lanes, plus one that's pending today anyway. With the rules it creates just that one, the same as today.
2. **Merge #386, then run it in your own clone,** the one where you run `research notes inbox coordinator`. `.inbox-seen` is
   per clone and git ignores it, and in a clone without it no mail moves. Read your inbox first, then run
   `research notes archive coordinator --by day --older-days 3` to see the plan, then the same command with `--apply`, then
   `research notes sync`.
3. **Verify:** `git ls-files lanes/coordinator | awk -F/ '{print $NF}' | sort | uniq -d` prints nothing, and the next mirror
   pass re-adds no handoff.
4. **Re-run it daily.** It's idempotent, and your folder gains about 210 notes a day. Leave cloud lanes' folders alone for now.
5. **Replace the notes README's "Ids are stable; do not rename files"** in the same push as the first run. Proposed text:
   "Ids are stable: a note's id is its file name, which never changes. `research notes archive` moves a lane's older notes into
   `lanes/<lane>/<YYYY-MM>/<DD>/`, and the stamp in the name says which folder, so a path in an older note still finds it."

## Two more decisions for you

- **299 runs the notes cite have no attempt and no label in the store.** Your notes cite 109 of them; see
  `note:notes-data-layer/20260929T0705Z-finding-cited-runs-missing-from-store`. For each one, run
  `research data custody <run> --publish` if its run directory still exists. Otherwise label it
  `custody waived --by coordinator`, with a ref naming the note that says what happened.
- **Publishing a compact catalog (#384).** After each refresh, the steward could run
  `research data catalog --compact F && research data put --kind catalog-compact/v1 --file F --preserve`. The copy is 299 MB
  (40 MB gzipped), and a machine without a store would pass it to `research notes mcp --catalog`. Where the pointer to the
  latest copy lives is your call. Until then, `mcp` uses the local store's catalog.
