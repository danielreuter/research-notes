---
lane: coordinator
kind: handoff
from: coordinator
created: 2026-09-24T18:10Z
---

# coordinator (laptop chat) -> the coordinator in the new Cursor Project: everything you need to take over

You replace the laptop coordinator chat. It stops acting once you confirm you have read this (reply with a checkpoint:
`research notes checkpoint coordinator open "project coordinator took over"`). Never have two coordinators merging main.

## Read first, in order
1. `~/.research/notes/kb/LANE-CONTRACT.md`: the rules every lane follows (worktrees, commits, reports/checkpoints, pods via
   `research run --on`, laptop limits, FINAL). You enforce it.
2. `lanes/coordinator/20260923T2120Z-state-coordinator.md`: durable coordinator state (newest block first) and the
   checkpoints at its top.
3. `campaigns/afternoon/BRIEF.md`: today's decisions and the two research lanes to launch (verifier-cost, arith).
4. `campaigns/robustness/BRIEF.md`: why the tooling looks the way it does (steward, pod guard, CLI worktree).
5. Latest tables: `campaigns/afternoon/render/1800Z-tables.md` and `-drilldown.md`.

## State at 18:10Z
- main = 22741456, pushed. Nothing in flight: no lanes running.
- Pods: vy-control (keep), vy-control-verity (the other session's, keep), vy-live2b-verifier-ro pitmqu0zrycw5i ($0.44/h,
  holds the only copy of 5.0 GB of live verifier sessions: the verifier-cost lane preserves it first; do not terminate before).
- Always-on on the laptop (launchd): `com.research.notes-watch` (the steward: status/alerts, reaper, deadlines, budgets,
  daily 13:00Z render from `~/projects/verity-main-wt/cli` per `steward.toml`, guardian-kill routing),
  `com.veritor.memguardian` (kills big laptop processes; disk floor 3.5 GB), `com.veritor.exthost-watch`.
- The CLI every lane uses is `~/.research/bin/research`, running the sparse worktree `~/projects/verity-main-wt/cli`.
  After every merge to main: `git -C ~/projects/verity-main-wt/cli checkout --detach main`, then
  `launchctl kickstart -k gui/$(id -u)/com.research.notes-watch`. Never edit files in `.../main` or `.../cli`.
- Merges: you are the only merger of main. The other session (vllm-coordinator) owns ~/projects/verity and verity-wt/* and
  pushes vllm work to origin/main too: fetch first, merge origin/main in (merge, not rebase), run the affected tests,
  push after every merge. Rust merges: `cargo check` on a pod, not the laptop.

## User decisions you must keep (do not re-litigate)
- Headline tables = `verity_numerical.bench.tables` output from main, nothing hand-made. Contract changes need the user's
  explicit approval first. Table 2 committed column definition: frozen as is.
- Every proof variant at the same security: 2^-128 target and achieved. SP1 stays out of Table 2 until an SP1 run meets it.
- Table 1 A-GKR hash corrected to SHA-512 (done, 04700cb5).
- Re-packed instances count as the frozen set if the decoded values are byte-identical (footnote).
- Standing permission: a more promising GKR variant can get its own hill-climb lane.
- Budget up to $50/h and up to 15 agents; the laptop must not do heavy work (no builds, no big test suites, no big files).
- The user will pilot Cursor SDK / Projects himself; do not ask for a CURSOR_API_KEY or build an SDK launcher unprompted.

## Open items (also in the state note)
- Launch verifier-cost and arith (specs in campaigns/afternoon/BRIEF.md).
- contract.result(...) builder for the ~20 bench-result emitters: spec `lanes/coordinator/20260924T0531Z-handoff-from-coordinator-contract-result.md`; delete that note when merged.
- Post-wave fixes: LIGSTM07 trimmed hashed statement (readers accept legacy); `reverify.py --system-h`; live_test shared-pair fixture 2^-99.86 < 2^-100.
- QoL: dump-completeness check at registration; `research pods stage TARGET ART...`; `research data preserved` hangs on
  network reads with no timeout (seen 17:10Z on art:e7ad0783); `research run --on` puts its own research copy first on
  PYTHONPATH (run pod test suites with `env -u PYTHONPATH`).
- Laptop: Cursor's state.vscdb is 77 GB and grows ~1 GB/h; shrinking it needs Cursor quit (user). Disk 16 GiB free 18:00Z.
- The user wants an SP1 at 2^-128 (apples to apples); not yet specified as a lane.

## If your agents run off the laptop
They need: the verity repo (origin), this notes repo (local git at ~/.research/notes, no remote yet), R2 credentials and the
RunPod key (as secrets, never in the repo), and read/write access to the artifact store index at ~/.research/store
(laptop-only today). Without the store, a lane can run pods and push to R2 but cannot run `research data` checks; say so
in its brief.
