---
id: 20261001T0200Z-handoff-from-bc-26712550-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-26712550 (pous live-console publisher)
---

# Migration handoff from bc-26712550: POUS's live-console panels (`pous/*` on /admin/live)

Per `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. One kept item, the backlog's "console panels" row
(`20261001T0205Z-reply-from-old-accounting-full-backlog.md`, line 111).

## 1. Branches and PRs

None. My only commits are research-notes notes.

## 2. Runs and jobs in flight

- No research runs, no fill jobs, nothing on node 2.
- On my VM, tmux `live-console-publish` runs `run.sh`. Every 5 minutes it sends each of the 11 `pous/*` panels whose source
  changed. The loop only runs while my VM is awake, and the VM sleeps between my turns; the last pass was at 01:20Z. Nothing
  needs preserving: the panels are rebuilt from their sources on every pass.

## 3. Half-done state, and what's only on my VM

- **Code and list (old pous store):** `code/live-console/export.py`, `run.sh` and `request-key.sh`, plus the panel list
  `internal/live-console/pous-panels.md` (ids, sources, format, publishing state).
  - `export.py` reads its sources relative to its own place in the store: `internal/pouw/panel/{attempts.jsonl,lines.json,panel.py}`,
    `internal/pouw/infra/utilization-report.json`, `docs/pouw/{assumptions,security-proofs,hashing-accounting,mvp-e2e}.md`,
    `docs/pous-throughput.md` and `docs/band-decode-benchmark.md`.
  - So copy `code/live-console/` into whichever store holds the live copies of those files, at the same relative paths.
- **Only on my VM:**
  - The key `~/.config/verity/panels.key` (`pous-panels`, `panels:write`, expires 2026-12-29T18:29:40Z). It's a secret, so it
    is not copied anywhere; the successor asks for its own (see 4).
  - `~/.local/state/pous-live-console/` (the publish log and the digests of the last PUTs). Not needed: a new host
    republishes everything once.
  - `/tmp/research-auth`, PR #457's `research auth` source, which `request-key.sh` fetches again by itself.

## 4. The next step

**Keep:** the 11 panels refreshed. The successor, on a VM that mounts the store holding the sources:

1. Copy `code/live-console/` there, then run `python3 export.py check` (the dry run: 11 of 11 should pass).
2. Ask for a key under the same name:
   `research auth request --name pous-panels --scopes panels:write --days 90 --file ~/.config/verity/panels.key`
   (or `bash request-key.sh`, which uses PR #457's client). Hand Daniel the printed sign-in link and code at once; he signs in
   there and approves at /approvals.
3. Start `bash run.sh` in tmux, and keep the VM awake: a wake timer, or a host that doesn't sleep.

When the successor confirms takeover here, I stop `live-console-publish`.

**Would stop:** nothing. The two PoUS tables are static and cost nothing.

**Still Daniel's:** confirming the panels render at /admin/live (backlog line 168).

## 5. Traps

- **Panel ownership.** The key that first published a panel owns it. The site records `published_by: "pous-panels"`, the
  token's name, so a new token named `pous-panels` should keep the panels; it replaces my token at its first use, and my PUTs
  then fail harmlessly. That's inferred from the site's response, not tested. A token under another name would likely be
  refused on all 11 ids, and someone would have to DELETE them with my key first.
- **The sign-in window.** A key request that nobody signs in to expires after 15 minutes (18:11Z expired that way). Daniel
  must open the request's own sign-in link before Approve is enabled.
- **Site limits the posted format doesn't state:** a text cell is at most 200 characters, a column name at most 60, there
  are 1 to 20 distinct columns, and a body is at most 64 KiB. `export.py` enforces all of these.
- **The VM sleeps between turns,** so the tmux loop stalls (18:52–23:43Z and 23:53–01:00Z). Every panel's `updated_at` is
  its source file's mtime, so a stall doesn't show on the panel itself.
- **The store mount** sometimes answers EAGAIN. `export.py` retries, but bash can fail to read `run.sh` from the store at
  start; just start it again.
- **`export.py` imports the store's `panel.py`** (`load_attempts`, `counted`, `basis`, `best`, `pct`). If those change shape,
  the two plots and the lines table go out as `rows: []` with a "No data" note, and stderr says why.
- **`pous/pouw-mvp-e2e` labels decode rows by their twin.** A decode row whose shape has a `-eager` twin in the same run and
  attempt reads "decode over stock FP8 with CUDA graphs (like-for-like)"; otherwise it reads "decode over eager stock FP8".
- **/admin/live can't be checked from an agent VM.** It's behind Vercel's protection and then the admin sign-in, and
  `/api/panels/*` takes only PUT and DELETE. The PUT's answer (`published_by`, `rows`) is the check.
