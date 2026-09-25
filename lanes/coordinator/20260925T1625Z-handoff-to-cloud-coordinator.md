---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
lane: coordinator
kind: handoff
from: coordinator bc-4100fff0 (laptop, handing over)
to: cloud research coordinator bc-8ece7cde
created: 2026-09-25T16:25Z
---

# Research coordinator handover: laptop bc-4100fff0 → cloud bc-8ece7cde (9:25 AM PT, Sep 25)

I've stopped merging. You are the only coordinator who merges into `main` from now on. See also my earlier
`20260925T1619Z-handoff-restart.md` (same directory) for the full queue, the scripts and the pod render recipe.

## main's head: **239c0e28**, not 8a3aa083

The root's note said 8a3aa083, but that's two merges old. PRs #23 and #24 and reverify-tile-2 are **already merged**; none of
them is pending.

## What I merged today (all pushed; the CLI worktree and the steward's clone on vy-control-verity are on 239c0e28)

| main | What | Notes |
|---|---|---|
| 3301c435 | lane/ligero-steps-pin c8a16e2b | steps pin H2 + R1/R2/R4 in reverify |
| 5ac28010 | lane/hash-commit 2a92fe61 | Poseidon2 int8 sm_90 row pad |
| 767115db | lane/b-ligero-sha256 98d878ca | sha256/row/v1 scheme + glibc MALLOC defaults |
| bfb0b928 | PR #21 | instance-equiv/v1 stream refs above 4096 |
| c09d74e6 | PR #22 | views "payload not local"; render refreshes payloads |
| 2c92b9e3 | cherry-pick b009fdc8 | bf16-hopper-x4+sha256 PINS row |
| b874764f | lane/flock-live a43f6254 | Flock live coins R1–R8 (re-audit GRANTED WITH CONDITIONS) |
| 33e4d8d1 | lane/vllm-rf-a4 10996616 | merged by the stood-down successor bc-c02f2a05; verified by me |
| 8b3537d5 | lane/vllm-rf-c1 15cf6dcc (--no-ff) | 38 integrations/vllm files + doc-only vllm_v1/PROTOCOL.md |
| 97ca338b | PR #23 | render + parity PYTHONPATH from the workspace (`tree_pythonpath`) |
| 80b19e59 | PR #24 | reaper: RESUMED-POD, custody before FINAL-lane reap, REAP-FAILED retry |
| 117016c1, 8a3aa083 | cherry-picks 977ad27b + 906255b2 | verify-night-3's reverify: manifest at the tree root |
| **239c0e28** | lane/reverify-tile-2 4ee9dd72 | tile re-verification (set.tile), Rust batch refuses stmt w/o proof |

Not merged, and why:
- **vLLM c4ir:** `lane/vllm-rf-c4ir` is force-pushed to 793f14af (phases 1+2 on 33e4d8d1; merges clean), but c4irb's READY is
  DRAFT (gate (a) pending).
- **lane/agkr-bound 89433d06:** untested against current main; drill-down only.

## The 5b28557b (blake3-xob) plan and its dependencies

- 5b28557b alone is **6 PINS rows in `backends/ligero-verify/src/leaf.rs`** (fp8-ada and fp8-ada-x4 under blake3-xob). It
  cherry-picks cleanly onto 239c0e28, but **it's not enough**: the scheme it pins isn't on main either.
- The xob series on `lane/b-ligero-standard-hash` (closed, clean, pushed) to take, oldest first, **skipping merges and the reverify
  commits already on main through ligero-steps-pin / c8a16e2b** (3af90e71, de2fa317, 07e5cf98, 5c7c4488, 806a2f73):
  1. 8dace837: the blake3_xob census prototype.
  2. 53b680e5: the blake3_xob_test census numbers.
  3. e19bc365: the `xadd` witness op (torch, reference, CUDA).
  4. ce86046b: the `leaf blake3-xob` scheme (a new scheme name, per my 0915Z ruling).
  5. fb29b130: blake3_xob_test, xadd in every witness generator.
  6. 672b23ae: conformance, a twin-relabelled statement may be refused by exception. Check whether it's needed.
  7. 5b28557b: the pins.
- Cherry-pick them in a scratch worktree off main, then run `blake3_xob_test`, `reverify_test`, `hashauth_test` and
  `cargo test --release` **on a pod** before pushing. The red team granted fp8-ada+blake3-xob and fp8-ada-x4+blake3-xob at 5b28557b
  (handoff 1226Z), and verify-night-3 accepted the xob cells against a tree that includes it. Once it's on main, those cells render.
  If a pick conflicts, stop and ask for a short cloud lane instead.

## reverify-fp4 (the root is launching it)

`internal/lane-briefs/reverify-fp4.md`, already in `internal/lanes/CLOUD-LANES.txt`:
- register fp4-nvf4 in reverify, then re-verify the 5090 NVFP4 pair (art:70f275ac, art:6740eb22) and blake3-80gb's 4 H100 re-runs;
- register and check, from a fresh pod, the two x4 +sha256 instance-equiv docs. That gives the **first SHA-256 Table 2 cells**
  (art:4aa258ee, art:fcd6a623, already red-team labelled; blocked only by rule I).

Also ready to launch: `internal/lane-briefs/ligero-hygiene.md` (the main live_test bug, the 3 timed-out negatives, the red team's
3 tile follow-ups, and combined-tree tests on 239c0e28). flock-link (bc-4690f05c…) is open, FINAL 18:00Z; its "ready for
re-audit" hands to red-team-flock.

## Laptop timers and processes: state, and how to stop each

| Item | What | State at 16:25Z | How to stop |
|---|---|---|---|
| `proof-opt-sweep-v4` | Cursor timer, every 30 min, sweep | **stopped by me** | `unsubscribe` sub_651374b5-2393-4ec2-b901-6d129399fee2 |
| `proof-opt-6am-render` | Cursor timer, cron `0 13 * * *` | **stopped by me** | `unsubscribe` sub_192955cc-5f5c-49b8-9ff5-bad98a92efbc |
| `proof-opt-daily-digest-6pm` | Cursor timer, cron `0 1 * * *` | **stopped by me** | `unsubscribe` sub_373acba4-02be-484a-bdc9-912c6670b363 |
| `disk-watch-v2` | Cursor timer, every 8 min | **stopped by me** | `unsubscribe` sub_b8d9e307-2fa4-4665-a9aa-7bcc0d6dfd07 |
| spend ledger | `lanes/coordinator/evidence/spend-ledger.py --every 120` | **already dead** (the ~9 AM PT /tmp wipe) | n/a. To re-create: `python spend-ledger.py --every 120`; `--report` prints |
| **cloud-lane mirror loop** | `lanes/coordinator/evidence/cloud-lane-mirror-loop.sh` (runs `cloud-lane-mirror.sh` every 5 min; notes ↔ store `internal/`; then `research notes sync`) | **RUNNING, kept on purpose** until you confirm your replacement on the control pod | `kill $(cat /tmp/cloud-lane-mirror-loop.pid)` on the laptop (it runs in its own session, parent launchd, cwd ~) |

Re-create the three render/sweep timers on your agent. The 6 AM and 6 PM renders **run on the control pod** (the recipe is in the
1619Z handoff). With PR #23 merged, the steward's own render should work: confirm its 01:00Z (6 PM PT) RENDERED line, then delete
`/root/.local/lib/python3.12/site-packages/verity-steward-render.pth.disabled` on vy-control-verity.

**The mirror's replacement** needs both the Project store (visible to agents) and push access to research-notes. Cloud agents'
`cursor[bot]` has no notes access (G1). Either get the Cursor GitHub App access to research-notes, or run the store side on your
VM and publish through the control pod's notes deploy key. Tell the root when yours is running, so the laptop loop can be killed.

## For Daniel

- C8: does A-GKR's 2^-127.7 hash budget count toward the whole-proof 2^-128?
- The published-table switch to the new spec is his call.
- Research spend: $97.75 of the $300 overnight window (ended 9 AM PT).
