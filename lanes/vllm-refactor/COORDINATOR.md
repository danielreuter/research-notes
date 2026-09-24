---
id: vllm-refactor/coordinator-state
lane: vllm-refactor
kind: state
updated: 2026-09-24T19:30Z
---
# vllm-refactor: coordinator state (resume from here)

**Handed off at 19:25Z** to the Cursor Project coordinator: `../vllm-coordinator/20260924T1925Z-handoff-for-project-coordinator.md`. Where the two differ, the handoff is current.

**Owner's standing rule (22:17Z):** decide housekeeping yourself (disk cleanup, eviction, which files to keep), using the safe default. Never delete anything not verified in R2 by direct hash, keep custody receipts, and never touch live-lane files. Report only the outcome. Surface to the owner only three things: spending beyond agreed caps, changes to agreed semantics or acceptance criteria, and irreversible loss.

**Coordinator since 19:20Z: Cursor agent bc-ba6cec03** (`../vllm-coordinator/20260924T1920Z-took-over.md`). It doesn't merge into `main`: the research coordinator is the single owner of `main` merges, and merge requests go to the owner through the Project coordinator. At 19:27Z a23 was superseded by **a23b** (agent bc-87224e5e-6d37-56de-a9ee-c75c627ef9c0, branch `lane/vllm-rf-a23b` from `c1cf11ef`, worktree `rf-a23b`, notes `vllm-rf-a23b`, pod `vyv-rf-a23`), with the `fixtures/W11*` move first so that f3 can do D15 on top of it. At 19:25Z the pods were a1, a23, f24 and f3 at $0.64/h each, plus f1-g1 and f1-tp2 (2x L40S each) at $2.18/h each: $6.92/h in total.

## Where things stand
- **Survey:** done, 673 findings. The synthesis is `SYNTHESIS.md` in this directory; its gate text and A4 ordering were corrected by the coordinator.
- **Owner decisions** (17:20Z), all as recommended:
  - merge cleanup-2 into main and branch from main;
  - start Phase 0 and A1 to A3 now;
  - value checks over opened values inside Commit now, with a separate verifier later;
  - delete CMT-1, `engine_rs` and the dead PoC paths;
  - refuse world > 2.
- **Merge:** `lane/vllm-cleanup-2` went into `main` at `72884c8a` (17:24Z, `--no-ff`). The only extra changes relative to cleanup-2 are in `tools/research`. No references to the removed package paths remain outside the integration.
- **Budget and deadline:**
  - The CAP file on `vy-control-verity` is 600. Spend was $238.67 when it was raised; the tally has run since 2026-09-23 under tag `2026-09-23-vyv-rebuild`.
  - The rate cap is $45/h.
  - The deadline daemon terminates `vyv-` pods at 03:00Z.
  - `/root/dm/budget_cap.py` on the pod (sha256 `3f273597…`) is the **veritor** variant: byte-identical to the uncommitted `~/projects/veritor/zk/campaign/budget_cap.py`, with `--rate-action newest`. Verity's `tools/research/src/research/pods/budget_cap.py` is veritor's committed HEAD version and lacks that option. In verity, `research pods guard` has replaced budget_cap.py and deadline.sh, and its `--rate-max` sheds the newest pods by default. At a switchover, move to `research pods guard --baseline <spent>` rather than porting the option. Don't restart with verity's budget_cap.py, `rearm.sh` or `deadman.sh`: `--rate-action` would be rejected, and without it a rate spike trips and terminates every `vyv-` pod.
  - Three daemons run on `vy-control-verity`, all vLLM's, as checked at 19:31Z: `budget_cap.py` (pid 8950), `deadline.sh vyv- 1790305200` (pid 20985) and `balance_floor.py` (pid 7241). The balance floor terminates every `vyv-` pod when the account balance drops below $25. It's only a backstop: the account auto-tops-up below about $100, so report only if the balance falls below about $90 without refilling. The binding limits are the $600 cap and the deadline. The owner's rule: push the deadline back a few hours at a time, never in one big jump, so it still works as a dead-man switch.
- Of the six lanes, a1, f1, f24, f3 and f56 are subagents of the old chat (eb746331), which can't be messaged while they run; steer them only through their files or pods, or restart them. a23b is the vLLM coordinator's own background subagent. Don't delete the old chat. Its role: `../vllm-coordinator/20260924T1945Z-setup-for-old-chat.md`.
- Gate (a) credential route: `20260924T1942Z-gate-a-credential-route.md`.
- **Watcher:** the other coordinator's notes watcher excludes `vllm*` lanes, which is why the refactor lanes are named `vllm-rf-*`.

## Lanes (local subagents launched from chat eb746331; the brief is `LANE_BRIEF.md`)
| lane | scope | agent id | branch | notes dir |
|---|---|---|---|---|
| a1 | baseline and guardrail lints | 0071dbd5-fc85-40a2-b188-0ff3b70d93a3 | lane/vllm-rf-a1 | ~/.research/notes/lanes/vllm-rf-a1 |
| a23 | dead code, data and paths | 910daceb-3d03-4c35-abd4-3ef36049a9a6 | lane/vllm-rf-a23 | …/vllm-rf-a23 |
| f1 | D1 opened-value replay | ca142d03-cbdd-4db6-921c-ad007244aa4b | lane/vllm-rf-f1 | …/vllm-rf-f1 |
| f24 | D5, D6, D7, D10, D11, D13 | 1d5dba5f-1f4a-44b3-b2b7-01aa308edc91 | lane/vllm-rf-f24 | …/vllm-rf-f24 |
| f3 | D3, D4, D14, D15 | 4d8eb3fd-689f-4551-a6ef-9439c59c06e6 | lane/vllm-rf-f3 | …/vllm-rf-f3 |
| f56 | D16, D17 | fec8581f-4b57-4899-81f1-ead76e01ceee | lane/vllm-rf-f56 | …/vllm-rf-f56 |

The canvas agent (742f18e5-2fc5-4a71-b848-36d442816381) is building a canvas of the survey and plan.

## Incidents
- **About 18:02Z:** the agent process of the veritor window restarted (new pid 89761). f1, f3 and f56 died with it and were resumed at 18:46-18:48Z through `Task resume` (context kept).
  - For a1 and a23, the resume returned "Agent host session already exists", so both are alive or hung.
  - a1 last wrote at 18:29Z and f24 was editing at 18:44Z.
  - a23 has written nothing since 18:02Z. If it is still silent at about 19:05Z, launch a fresh a23 on a new branch, lane/vllm-rf-a23b, from origin/lane/vllm-rf-a23.
- **Liveness probe:** `Task resume <id>` fails with "session already exists" when the agent is alive; otherwise it restarts the agent with its context. Subagent transcripts stop updating after a host restart, even for survivors, so they are not a liveness signal.
- **The baseline at 72884c8a is not green:** gate (b) has 65 failures and errors. Lanes judge "no new failures" against `vllm-rf-a1/baseline.md`.

## If a lane dies
Relaunch a fresh generalPurpose subagent with the lane's prompt from `LANE_PROMPTS.md`, with that file's restart preamble in front.

## Merging
Since 19:25Z the research coordinator does every merge to `main`, so two agents can never merge at once. The order is a1, then a23 (or a23b), then the f-lanes as their READY.md files appear. For each lane, the vLLM coordinator:
1. checks the gate evidence in READY.md against the baseline;
2. makes sure the branch is pushed and rebases cleanly on current `main`;
3. hands the branch and head commit to the research coordinator for a `--no-ff` merge;
4. tells the remaining lanes to rebase.

**Merge requests (sent to the owner via the Project coordinator; the research coordinator merges):**
- 22:25Z **a1**: `lane/vllm-rf-a1-rebased` @ `bcbec401`. That is a1's `39c5ee7a` rebased onto main `21688b01`, plus one coordinator commit deleting the 2 lint allowlist entries that main's `e0c7bfe9` (fold_compare) made stale. The lints are 41/41 on main on a CPU pod, and without the fix 2 fail. `lane/vllm-rf-a1` itself is untouched. **Merged 22:10Z as main `1d9c3198`** (research coordinator, `--no-ff`). At 22:13Z the rebase broadcast `20260924T2213Z-main-moved-rebase.md` went out, with a banner in each lane's STATE.md. a23b has one trivial conflict in `fold_compare.py`; f1, f24, f3 and f56 are clean. Next: a23b.

## Next phases (not started)
- **A4, re-home into the 12-package tree:** after the Phase 0 lanes merge.
- **A5, one CLI and typed config:** after A4.
- **Phase 2:** B1 to B5.
- **Phase 3:** C1 to C4, behind decisions 1, 3, 4 and 5, which are still open.
