---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
lane: coordinator
kind: handoff
from: coordinator (bc-4100fff0, laptop)
created: 2026-09-25T16:19Z
---

# Research coordinator handoff before the laptop Cursor restart (9:19 AM PT, Sep 25)

You succeed the research coordinator bc-4100fff0 on a cloud VM. The state note is `lanes/coordinator/20260923T2120Z-state-coordinator.md`,
the contract is `kb/LANE-CONTRACT.md` and the spec is `kb/TABLES.md`. Times are PT in prose, UTC in ids.

## State at handoff

- **main = 239c0e28** (origin). Merged this morning, in order: flock-live b874764f; vLLM A4 33e4d8d1 (by successor bc-c02f2a05);
  PR #22 c09d74e6; b009fdc8 pin 2c92b9e3; vLLM c1 8b3537d5; **PR #23 97ca338b** (render PYTHONPATH); **PR #24 80b19e59** (reaper:
  RESUMED-POD, custody before FINAL-lane reap); verify-night-3's reverify fix 117016c1/8a3aa083 (cherry-pick of 977ad27b + 906255b2);
  **reverify-tile-2 239c0e28**. The CLI worktree (laptop) and the steward's clone on `vy-control-verity` are on 239c0e28.
- **All research branches and worktrees are pushed and clean** (checked 16:18Z; no WIP needed).
- **Spend:** research $97.75 of $300 since 11:51 PM PT (the $300 window ended 9 AM PT); running about $1.70/h.
- **Laptop disk:** 33 GiB free (the emergency is over; /tmp was wiped around 8–9 AM PT).
- **New-spec Table 2 (B-Ligero), last rendered 16:1xZ on the control pod at 8a3aa083:** RTX 4090 E4M3 keyed-BLAKE3 **1.9e7×**
  (art:ecccca50, x4 32768 plateau); H100 BF16 keyed-BLAKE3 **2.8e8×**; H100 E4M3 keyed-BLAKE3 **2.8e8×**; all verified and red-team
  labelled. SHA-256 rows empty: art:4aa258ee and art:fcd6a623 are red-team labelled but blocked by rule I (no instance-equiv/v1).
  Poseidon2 rows (alg.) provisional. The scoreboard doc is `docs/proof-optimization-tables.md` (my frontmatter).

## Open queue (priority order)

1. **Re-render** on the control pod after any new label or equivalence artifact, and before the 6 PM PT digest (below).
2. **Launch-and-track** (briefs in `internal/lane-briefs/`, not all launched yet; ask the root which are running):
   - `reverify-fp4.md`: register fp4-nvf4 in reverify (5090 NVFP4 pair art:70f275ac/6740eb22); re-verify blake3-80gb's 4 H100
     re-runs; **register + fresh-pod-check the two x4 +sha256 instance-equiv docs → first SHA-256 Table 2 cells**.
   - `ligero-hygiene.md`: combined-tree tests on 239c0e28; the **main `live_test::test_shared_pair_every_coin_from_the_verifier[None]`
     bug** (2^-99.86 vs 2^-100); the 3 timed-out committed-operand negatives; the **red team's 3 tile follow-ups** (float-seed clean
     FAIL, set.sharing vs set.tile, missing .hproof negative).
3. **flock-link** (cloud bc-4690f05c-e4ed-5a3a-b033-0d935c39980e, brief `flock-link.md`, FINAL 18:00Z): L1–L4 + F2. When it hands
   off "ready for re-audit", the root relaunches red-team-flock (bc-fe5a9310). Route (a) cells need that grant + C8 (Daniel) + pins.
4. **vLLM c4ir** (`lane/vllm-rf-c4ir` 793f14af, phases 1+2 on 33e4d8d1): merge once c4irb's READY moves off DRAFT (gate (a)).
5. **xob pins:** 5b28557b (blake3-xob verifier pins, red-team granted) is not on main; verify-night-3's xob acceptances need it to render
   from main. Take the pin commit(s) from `lane/b-ligero-standard-hash` (closed) after checking its dependencies.
6. **Pod .pth:** `/root/.local/lib/python3.12/site-packages/verity-steward-render.pth.disabled` on vy-control-verity: delete after the
   steward's own 6 PM PT (01:00Z) render logs RENDERED (PR #23 makes it unnecessary; a manual #23-path render passed without it).
7. **For Daniel:** C8 (does A-GKR's 2^-127.7 hash budget count toward 2^-128?); agkr-bound's lane/agkr-bound 89433d06 unmerged
   (untested vs current main); the published-table switch to the new spec is his call.

## Cloud lanes (mirror list `internal/lanes/CLOUD-LANES.txt`)

red-team-flock (FINAL), flock-live (FINAL), verify-night-3 (FINAL), red-team-standard-hash-2 (FINAL), reverify-tile-2 (FINAL, merged),
reaper-resume-guard (FINAL, merged #24), flock-link (open), reverify-fp4 and ligero-hygiene (briefs). Agent ids: flock-link
bc-4690f05c…, reaper-resume-guard bc-4027ac8f…, verify-night-3 bc-802ac470…, red-team-standard-hash-2 bc-6e7c09af…, reverify-tile-2
bc-fff2b99f…. No research lanes run on the laptop.

## Timers (Cursor subscriptions on bc-4100fff0; they end with this agent, so re-create them on yours)

- `proof-opt-sweep-v4`, every 30 min: spend, disk, mirror liveness, lane status, inbox, idle pods, checkpoint.
- `proof-opt-6am-render`, cron `0 13 * * *`: 6 AM PT render on the control pod + digest.
- `proof-opt-daily-digest-6pm`, cron `0 1 * * *`: 6 PM PT render on the control pod + digest (only table changes, before/after,
  verified?).
- `disk-watch-v2`, every 8 min: laptop disk rules (1.8 / 1.0 GiB). Likely unneeded once nothing runs on the laptop.

## Detached processes (both already DEAD at 16:19Z: the /tmp wipe; re-create them, ideally on vy-control-verity)

- **Cloud-lane mirror** (notes ↔ store): `lanes/coordinator/evidence/cloud-lane-mirror.sh` (one pass) and
  `cloud-lane-mirror-loop.sh` (every 5 min; start it in its own session). It needs the Project store (laptop or cloud VM: only
  agents see `/cursor/stores/...`) **and** push access to research-notes (the laptop or the control pod's deploy key; cloud
  agents can't push notes yet). So on a cloud VM it can copy store→notes clone but can't publish; either run it on the laptop
  again, or get the Cursor GitHub App access to research-notes. **Without it the steward can't see cloud lanes' checkpoints**
  and could reap their pods (PR #24 now spares pods created after FINAL and checks custody first).
- **Spend ledger:** `lanes/coordinator/evidence/spend-ledger.py --every 120` (writes `spend-ledger.json`; `--report` prints).
  Uses the laptop's RunPod key via research.pods.runpod; on the control pod it would use the pod's account key.

## Scripts (all in `~/.research/notes/lanes/coordinator/evidence/`)

`cloud-lane-mirror.sh`, `cloud-lane-mirror-loop.sh`, `spend-ledger.py`, `render-scoreboard.sh` (laptop render; superseded by
pod renders), `marked-cells.py`, `remove-finished-worktrees.sh`, `archive-dirty-worktrees.py`, `preserve-evict-blobs.sh`,
`evict-run-telemetry.py` (research runs only), `evict-vllm-run-files.py` + `preserve-evict-vllm-run-files.py` (root-approved,
vLLM finished runs). The evict scripts import `/tmp/coord-evict/check.py`, **which the /tmp wipe deleted**: re-create it (direct
R2 HEAD by sha256, size + ETag / multipart ETag) before using them. Logs: `20260924T2120Z-eviction-log.tsv`,
`worktree-removals.log`, `worktree-archives.log`, `cloud-lane-mirror.log`, `balance.log`.

**Pod render recipe (control pod):** `cd /workspace/steward/verity; PY=$(/root/.local/bin/uv python find 3.12); . r2.env;
PP=$(PYTHONPATH=tools/research/src $PY -c "from pathlib import Path; from research.pythonpath import tree_pythonpath;
print(tree_pythonpath(Path('.').resolve()))"); env PYTHONPATH=$PP $PY -s -m research data refresh --store /workspace/steward/store
--payloads instance-equiv/v1 bench-result/v1; then verity_numerical.bench.{tables,drilldown,views} --root /workspace/steward/store
--format md`. Copy outputs back; assemble the scoreboard doc (frontmatter, changed list, new-spec Table 2, frozen tables, drill-downs).
After every merge: move the CLI worktree, `git -C /workspace/steward/verity pull`, restart the steward with
`kill -TERM $(pgrep -f "[p]ython3.12 -s -m research notes watch")`.
