# Cursor agent host: why every local agent dies at once, and the limits we work within

Sources: Cursor logs `~/Library/Application Support/Cursor/logs/<session>/main.log` and
`window*/exthost/anysphere.cursor-agent-host/`; forum/doc links below (read 2026-09-24, web research lane 4784ef23).

## Facts
- Every local agent in a window (coordinators AND their Task subagents) runs inside that window's ONE extension host
  process (agent-host log: `runtime "connect", reason "managed-local-unavailable"`). One window = one shared fate.
- "extensionHost ... crashed with code 5" = the process crashed itself on a fatal V8 error (signal 5, SIGTRAP), normally
  its JavaScript heap reaching the ~4 GB Electron cap. A macOS low-memory kill would read SIGKILL/"killed" instead.
  https://www.electronjs.org/blog/v8-memory-cage , https://github.com/microsoft/vscode/issues/304692
- The cap cannot be raised: `js-flags` in argv.json is unsupported, NODE_OPTIONS is no longer passed through
  (https://forum.cursor.com/t/170166). Staff: no limit on concurrent local agents and no shedding as memory climbs
  (https://forum.cursor.com/t/166727); advice is 2-3 background agents per window, reload/quit between batches, archive
  finished chats, spread work across windows (https://forum.cursor.com/t/168061).
- `state.vscdb` (~/Library/Application Support/Cursor/User/globalStorage) is never pruned automatically
  (https://forum.cursor.com/t/171972). Task `resume:"self"` forks copy full transcripts into it (bug:
  https://forum.cursor.com/t/165170) -- use fresh subagents instead.
- `[resource_exhausted]` = provider capacity, not our plan (https://forum.cursor.com/t/168807).

## 2026-09-23 incidents (PT)
Host crashes 14:20:28, 16:31:40, 19:58:15 (code 5) + reboot ~12:47. Each host lifetime served 23-30 conversations.
14:20 followed four 8.6 GB red-team scripts on the laptop (guardian kills, swap 89%); 16:31 and 19:58 had flat
memory. Both coordinators shared window 5. Disk 98% full; state.vscdb 66.9 GB (+8 GB/day, ~700 subagents launched).

## Rules until lanes run remotely
- One coordinator per window; <= 8 live conversations per window; restart Cursor (Cmd+Q, not force-quit) between waves.
- Watch `~/.veritor/exthost_mem.log` (launchd job com.veritor.exthost-watch notifies at 2.8 / 3.4 GB): at 2.8 GB stop
  launching; plan a restart.
- Background daemons from an agent shell die when the tool call ends; use `launchctl submit -l <label> -- CMD`.
- Never query state.vscdb with GROUP BY/ORDER BY: SQLite's temp sort filled the disk on 2026-09-24 04:10Z.

## Shrinking state.vscdb (user action, Cursor quit)
Staff order (https://forum.cursor.com/t/172127): quit Cursor and `du`; "GC Agent KV Blobs" (lossless, needs free disk
about equal to the DB size); optionally "Developer: Delete Old Chats..." (permanent -- the JSONL transcripts in
~/.cursor/projects/*/agent-transcripts stay on disk); GC again; quit fully and let compaction finish.

## Remote workers (My Machines: `agent worker start` on a Linux box, tool calls run there, agent loop in Cursor's cloud)
- Dashboard secrets are NOT pushed to My Machines workers: credentials live in the worker's own environment
  (https://forum.cursor.com/t/157230). Run the worker under tmux/systemd; `--management-addr` serves /healthz and
  /metrics (https://cursor.com/docs/cloud-agent/self-hosted/pool).
- Restart the worker after a CLI update: a stale worker stopped returning shell exit statuses
  (https://forum.cursor.com/t/172713).
- One worker PROCESS serves one agent at a time (worker list reports a single activeBcId), but one box can run many
  workers, each with its own `--name` and worktree; `--worker-dir` takes up to 20 roots, so a shared notes directory can
  be an extra root. Cap 200 workers per user. https://cursor.com/docs/cloud-agent/self-hosted/my-machines
- Setup: `curl https://cursor.com/install -fsS | bash`; `agent login` or CURSOR_API_KEY; `agent worker start` from the repo.
- Targeting a named worker: REST `POST /v1/agents` with `"env": {"type": "machine", "name": "<worker>"}`, the
  cursor.com/agents worker selector, or `worker=` in Slack/GitHub/Linear. Not documented from the desktop chat or the SDK.
  Follow-ups: `POST /v1/agents/{id}/runs` (one active run per agent).
- Cursor-hosted Cloud Agents: SSH egress to arbitrary hosts is not documented (test before relying on it); secrets are
  Runtime Secrets on cursor.com; VM size undocumented ("limited memory and CPU"). Fine for code-only lanes.
- Cursor "Projects" (beta, changelog 2026-09-10): a cloud coordinator that keeps delegating with the laptop closed.

## Disk: Cursor's state DB (measured 2026-09-24)
- `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb` was 74 GB (69 GiB) and grew ~1 GB/h with ~10 local
  agents running (guardian heartbeat `cursor_db=` in `~/.veritor/mem_guardian.log`: 59 GiB at 12:10Z 09-23 -> 69 GiB at 06:40Z).
- SQLite `VACUUM` needs free space about the size of the DB, so it cannot shrink in place on this laptop; deleting old rows only
  lets SQLite reuse pages (stops growth, file stays big). Any cleanup needs Cursor quit and the user's say on which chats go.
- With disk low, macOS swap cannot grow and sits at ~95% even with half the RAM free; the guardian's swap rule now also requires
  `kern.memorystatus_level` < 25 (2026-09-24 06:42Z), and its disk-kill floor is 3.5 GiB.
