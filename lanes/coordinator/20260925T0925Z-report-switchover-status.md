---
lane: coordinator
kind: report
created: 2026-09-25T09:25Z
status: open
---

CHECKPOINT none (09:57Z) [open] 10:04Z (3:04 AM PT) b-ligero-sha256 0955Z allocator finding (per-proof mmap re-faults; MALLOC_MMAP_MAX_=0 + MALLOC_TRIM_THRESHOLD_ fix, prover 7.7-29 s -> 1.4 s at 8192 VUs): asked b-ligero-sha256 for a merge-ready shared-bootstrap default + fingerprint field; told blake3-80gb, b-ligero-standard-hash, poseidon-v1, hash-commit-2, agkr-bound, verify-night-2 to export it now. Earlier numbers unchanged (conservative).
CHECKPOINT none (09:57Z) [open] 10:01Z (3:01 AM PT) flock-bench FINAL 09:58Z (5 pods terminated, $3.48 of $12; 5090 unit+BLAKE3 BF16 0.42-0.58 s, 18-25x under B-Ligero +blake3; link est. ~1.7-2.3x bare on GPU). Freed slot -> launched red-team-link (bc-9d7ffc86): audit docs/flock-link-protocol.md, verdict gates agkr-bound route (a); no laptop worktree, pods only, $15, FINAL 14:00Z; red-team-standard-hash told to drop it from its queue. Disk recovered to 4.6 GiB (above 3; lane hold on laptop fetches stays until >5). Agents 11/11. Spend ~$38 of $300.
CHECKPOINT none (09:49Z) [open] 09:50Z (2:50 AM PT) disk (root-approved): removed main/backends/ligero-verify/target (~36 MB, clean worktree, no merge/build); preserved the two 103 MB orphan blobs as art:646722df + art:5ee81f76 (orphan-blob/v1), R2 direct-hash OK, evicted. Free 2.6 -> 2.8 GiB, still under 3 GiB: laptop freeze and lane hold stay. Logs: worktree-removals.log, eviction-log.tsv.
CHECKPOINT none (09:45Z) [open] 09:48Z (2:48 AM PT) sweep: spend $36.85 of $300 (running $20.53/h). DISK 2.6 GiB, below the 3 GiB stop line: no new laptop-side processes; lanes told no laptop fetches/builds/worktrees (0946Z broadcast). Swap flat (18.2 GB); 420 MB of new store/runs writes incl. two 103 MB blobs not in R2 (kept). Inbox: verify-night-2 0940Z (5 poseidon-v1 alg. results accepted) -> digest list, laptop re-render deferred to the pod steward's 6 AM render; flock-bench 0945Z binary-backend numbers -> digest. Nudged blake3-80gb (A100 idle 12m). All lanes fresh.
CHECKPOINT none (09:34Z) [open] 09:39Z (2:39 AM PT) SP1 committed cell art:49695f7c (not on the scoreboard) labelled UNDER RE-VERIFICATION per red-team SH 0925Z (R3 open on the --instances path); verify-night-2 to re-check with committed-verify --batch. Runbook step 4 D1 confirmed: data label printed 'on s3://verity-dev'.
CHECKPOINT none (09:33Z) [open] 09:37Z (2:37 AM PT) MERGED lane/ligero-steps-pin c8a16e2b into main -> 3301c435 (H2 steps pin, R1 layout, R2 commitment recomputation, R4 stmt/proof coverage; pod tests: py 50, rust 33+7+27, 9/9 existing dumps accepted). 806a2f73 not needed (behaviour included). CLI worktree + pod steward on 3301c435, steward restarted (pass 1, 0 stale). Handoffs: red-team-standard-hash re-run R1/R4/H2 harnesses on main; verify-night-2 CLEARED only at >=3301c435 and after the red-team verdict; b-ligero-standard-hash/b-ligero-sha256/blake3-80gb/poseidon-v1 merge main. Also relaunched hash-commit as hash-commit-2. Spend ~$28 of $300.
CHECKPOINT none (09:30Z) [open] 09:30Z (2:30 AM PT) hash-commit agent bc-cbc8d78b died 09:25Z (activity task timed out; worktree clean+pushed, pod job in flight). Relaunched per contract C as hash-commit-2 (bc-96dbced5): collect the pod job, then GPU committer byte-identity + timing on A100 (sm_80) and H100 (sm_90) for the B-Ligero lanes; FINAL 13:30Z, $40 total (~$3 spent). Agents 11/11. Spend ~$28 of $300.
CHECKPOINT none (09:24Z) [open] 09:26Z (2:26 AM PT) switch-over status, one line per step in lanes/coordinator/20260925T0925Z-report-switchover-status.md: 0 done (lanes open by design) | 1 BLOCKED: 5 vllm-rf-* branches unpushed (vLLM coordinator); flock-bench pushed | 2.1 done (pending=0) | 2.2 PENDING Daniel waiver (324 no-custody, 58 unpreserved) | 3 done | 4 done (store.toml write_through=true 09:20Z) | 5 done | 6 done (A4 552=552) | 7 done | 8.1-8.7a done | 8.8 lease HELD by vy-control-verity pid 71094, renewed 09:16Z; 6 AM render pending | 8.9 reboot test BLOCKED on 9 | 9 NOT DONE: old vyv daemons still run; needs vLLM agreement, then bc-21aca6c8 | 10.1 done | 10.2 G1 PENDING bc-21aca6c8 | 10.3 done | 11 pending (root) | notes sync ON, write-through ON. Spend $27.77+ of $300.
# Cloud switch-over status, 2:25 AM PT (runbook `docs/cloud-switchover-runbook.md`)

Milestone 1 is **in progress, not starting**. Steps 3–7 and 10.1/10.3 are done. The steward is live on the control
pod and holds the lease. Three things block completion: step 9 (the vyv- guard, which needs the vLLM side), the reboot
test that depends on it, and step 11.

| Step | Status | Detail |
|---|---|---|
| 0 Go / no-go | done, with an accepted exception | PRs merged (`main` 94b1c4d2); the cli worktree is at main. The "every lane FINAL" box is not met: 12 research lanes and the vLLM lanes are open. The switch-over is running live around them, as decided. |
| 1 Branches on origin (H1) | **blocked on vLLM coordinator** | Research side done: lane/flock-bench pushed 09:21Z (its only BLOCKING line). Still BLOCKING: lane/vllm-rf-a5, -b4, -b5gm, -c1, -c2 (unpushed, open). |
| 2.1 Pending push | done 09:21Z | `data push --pending`: 12/12 preserved; `data pending` exits 0. |
| 2.2 F2 custody triage | **pending Daniel (morning waiver)** | Triage 09:21Z: 324 `no-custody` and 58 `attempt-unpreserved` runs, 0 waived. Saved at `campaigns/remote-state/assets/parity/triage-20260925T0921Z.json`. The never-fetched list goes to Daniel as one waiver. |
| 3 Parity pass 1 (D4) | done | PARITY OK 04:25Z (9:25 PM PT), after reconciling 9 attempts. |
| 4 Write-through (D1) | done 09:20Z | The wrapper had carried `RESEARCH_WRITE_THROUGH=1` plus r2.env since 06:5xZ; `write_through = true` was added to `~/.research/store.toml` at 09:20Z, so non-wrapper CLI calls write through too. D1 confirmed 09:34Z: a real `data label` printed `on s3://verity-dev`. |
| 5 Parity pass 2 (D7) | done | PARITY OK 05:07Z. |
| 6 Notes remote (A4) | done | origin = danielreuter/research-notes; A4: HEAD 552 = origin 552 (09:18Z); the old `com.research.notes-watch` count is 0. 6.5 A1 clone smoke: checked from the cloud 10:50 PM PT (1 s), and the steward's pod clone has synced since 06:06Z. |
| 7 Contract edits | done | `kb/LANE-CONTRACT.md` v2.0 is on origin. |
| 8.1–8.7a Steward on vy-control-verity | done | Deploy keys, clones, R2 key (7d), state carry-over, `run.sh` + `/post_start.sh`, render repointed (`steward.toml` e68c187, 06:06Z, by `steward`). |
| 8.8 Check | done except the render | **Lease held:** `steward/lease.json` owner vy-control-verity, pid 71094 (the running watcher), acquired 08:48Z, renewed 09:16:39Z, expires 09:31:39Z (TTL 900 s), not released. `watch.log` pass 14 at 09:16Z, ACCOUNT line present. Notes sync commits on origin: 2 by `steward` and 132 by the lanes' synced checkpoints in 8 h. The 6 AM PT render is pending (E4, render half). |
| 8.9 Pod reboot test (E4) | **blocked on step 9** | Needs the guard in `/post_start.sh` first, and a moment with no `vyv-` pod running (7 are up). CLOUD: bc-21aca6c8 or the root. |
| 8.10 R2 key rotation | CLOUD, recurring | The root re-mints daily; the current key is 7d, so there's no urgency. |
| 9 vyv- guard → `research pods guard` | **not done; needs relaying** | The old daemons still run on the pod: `budget_cap.py` (tag 2026-09-23-vyv-rebuild), `deadline.sh vyv- 1790341200` (13:00Z = 6:00 AM PT), `balance_floor.py`. `research pods guard` is not running. Runbook precondition: the vLLM lanes are finished **and** the vLLM coordinator agrees. Then bc-21aca6c8 does 9.1–9.5 (9.2 is CLOUD `pods sync`; 9.1/9.3/9.4 are POD). |
| 10.1 Registry into notes | done | `machines.d` has 28 entries; the wrapper sets `RESEARCH_MACHINES_D`; lanes create pods with `--register`. |
| 10.2 G1 smoke (CLOUD) | **pending, bc-21aca6c8** | No record of it being run. It's a $1 cheapest-pod create → `--on` → terminate from a cloud agent. |
| 10.3 F1 custody | done | PASSED 11:04 PM PT (`internal/f1-custody-test.md`). |
| 11 Coordinators go cloud | pending (CLOUD, root) | After the lanes settle. 11.2: `com.research.podlane-sync` is already gone from launchd; the wrapper stays for laptop use. |
| 12 Done when | not yet | Open: H1 (vLLM branches), F2 waiver, guard status, coordinators in the cloud, and the root's final summary to Daniel. |
