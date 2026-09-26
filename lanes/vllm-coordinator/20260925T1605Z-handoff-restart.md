---
cursor:
  subagentId: "bc-ba6cec03-e2aa-5a7e-9db3-6bc124a205aa"
---
# vLLM coordinator handoff: laptop restart (2026-09-25 16:05Z, 9:05 AM PT)

From: vLLM coordinator bc-ba6cec03 (laptop). To: its successor on a cloud VM.

## What happened
- At 16:03Z every laptop lane session ended with "lost connection to the worker": b1b, b4b, gb, b5vb, b5va, b5patb and c4irb. a5b ended with the restart.
- At 16:04Z the coordinator pushed every lane branch. gb's 2 uncommitted files went to `wip/vllm-rf-gb-1604` (`176d3bff`); every other lane was clean.
- Each lane's STATE.md has a 16:04Z "LAPTOP RESTART" banner.
- Pods keep running under the vyv- guard. Don't terminate them just because a lane ended; let the successor lanes adopt them.

## Where state lives (laptop paths; on a cloud VM use the same repo and the notes in `~/.research`, if synced)
- Coordinator state: `~/.research/notes/lanes/vllm-refactor/COORDINATOR.md`. It holds the morning list at the top, and its last dated bullets (14:25Z to 14:55Z) hold the lanes, merge requests and queue.
- Rules: `WAVE2_BRIEF.md`, `LANE_BRIEF.md` and `SYNTHESIS.md` (decision log at the end), in the same directory.
- **Relaunch procedure:** `~/.research/notes/lanes/vllm-refactor/LANE_PROMPTS_WAVE2.md`.
  - Its RESTART section: start a successor `{X}c` on a new branch, worktree and notes dir from the pushed head (or the WIP branch), copy the predecessor's STATE.md, adopt its pods, and don't redo recorded work.
  - Its scopes list includes "Lanes started after a4 merged".
- Lane notes: `~/.research/notes/lanes/vllm-rf-{lane}/STATE.md` and `READY.md`. Each STATE has `## Running` and `## Next` sections.

## Main
`origin/main` is `80b19e59`. After a4 (`33e4d8d1`), c1 merged as `8b3537d5` (14:41Z). After that came PR #23 and PR #24, both tools/research only.

## Lanes at 16:04Z
| Lane | Agent (ended) | Branch @ head | Base | Pods (vyv-rf-…) | Next step (see STATE `## Next`) |
|---|---|---|---|---|---|
| a5b: CLI, typed config, `verity_vllm.LLM` | bc-a9b686f7 | `lane/vllm-rf-a5b` @ `da9e4847` | a4 `10996616`, needs `rebase --onto origin/main 10996616` | a5-g1, a5-t1, a5-tp2d | STATE lines 50 (Running) and 62 (Next): row-family reruns through `verity-vllm row` |
| b1b: kernels and replay | bc-033f1f34 | `lane/vllm-rf-b1b` @ `8c0bec08` (no commit since 04:24 PT; READY draft 07:38 PT) | a4 `10996616`, needs rebase | b1-g2, b1-tp2 | STATE lines 103 and 109; finish READY.md |
| b4b: engine and hooks | bc-892f86c5 | `lane/vllm-rf-b4b` @ `5c05ff6d` (rebased on `8b3537d5`) | `8b3537d5` | b4b-cpu, b4b-g1 | Re-gate after c1: lints, gate (b) vs `8b3537d5` (same pod), #101 smoke. Then its **merge request** |
| gb: gate (b) to green (test-side only) | bc-707a2df4 | `lane/vllm-rf-gb` @ `33e4d8d1` + `wip/vllm-rf-gb-1604` | `33e4d8d1` | gb-cpu | STATE lines 17 and 20 |
| b5vb: split `vllm_bindings.py` | bc-19e6c2c5 | `lane/vllm-rf-b5vb` @ `33e4d8d1` (no commits) | `33e4d8d1` | none | STATE lines 23 and 26 |
| b5va: split `engine/vllm_adapter.py` | bc-649f6a27 | `lane/vllm-rf-b5va` @ `2908cca1` (no commits) | b4b; `rebase --onto 5c05ff6d 2908cca1` (banner in STATE) | none | STATE lines 23 and 26 |
| b5patb: split fold patterns | bc-c7bcfa82 | `lane/vllm-rf-b5patb` @ `4537961b` | a4 `10996616`, needs rebase | b5pat-cpu, b5pat-big | STATE line 83 |
| c4irb: IR analyses to core | bc-53dac16f | `lane/vllm-rf-c4irb` = `lane/vllm-rf-c4ir` @ `793f14af` | `33e4d8d1` | c4ir-reg (gate (a)) | STATE lines 49 and 60: gate (a) T0+T1 result, then READY. Then c4ir's **merge request** |

Finished (no lane needed): c1 (merged), c2b, b5gmb, b2vb, a4 (merged).

## Merge queue (the root merges; the coordinator never merges into main)
- **Sent, pending:**
  - `lane/vllm-rf-b2vb` @ `ed8f6625`;
  - `lane/vllm-rf-b5gmb` @ `03e7b182`;
  - `lane/vllm-rf-c2b` **only up to `4d053f01`** (its epoch commit `dedf5313` waits for the re-baseline).
- **At `80b19e59`:** all three merge cleanly, and the P10 ratchet has 0 problems (`/tmp/p10check.py`, a stdlib replica of `tests/lint/test_p10_size.py`; recreate it if `/tmp` is gone).
- **Not yet sent:**
  - `lane/vllm-rf-c4ir` @ `793f14af` (phases 1+2): send when c4irb's gate (a) lands. It supersedes phase 1's `cfe0ae63`.
  - `lane/vllm-rf-b4b`: send after its re-gate on `8b3537d5`.
- **When main moves:** worktrees share refs, so use explicit shas and `git merge-tree --write-tree <main> <branch>`. Recheck every pending branch. If a branch conflicts or auto-merges code in the same files as the new main, its lane rebases and re-gates.

## Queue for free slots (cap: 8 vLLM lanes plus the coordinator)
- `native_host`: c1 is merged; waits for b4b, which edits it.
- `batch_decomp`: after b5gmb and a5.
- `lifted.py`: after c2b and c4ir.
- `commit_delta`: after a5.
- B3 and B2's heredoc part: after a5.
- C3 (digests move, so epoch work): after b4b.
- The epoch: after C1 to C3.

## Guard, money, deadline
- **Guard:** `research pods guard --prefix vyv-` on vy-control-verity. Never terminate the control pod; never touch the research daemons or pods (`vy-*`).
- **Spend:** $471.36 of $623 at 16:04Z, rate $16.11/h. The cap is in `/root/dm/CAP` and is owner-held. vLLM has $300 of new spend tonight. Report if spend passes $600, and don't start lanes that project past about $610.
- **Deadline:** **2026-09-25T18:30Z (11:30 AM PT)**. I deliberately did not extend it at restart: it stays a dead-man switch until a successor is live. Extend in steps of at most 4 h, and only while lanes need pods.
- **Status:**

~~~
ssh -i ~/.runpod/ssh/runpodctl-ssh-key -p 11754 root@213.173.105.92
cd /workspace/steward/verity && PYTHONPATH=tools/research/src python3 -m research pods guard status --prefix vyv-
~~~

- **Extend the deadline** (about 2 s unguarded):

~~~
NEW={ISO}; sed -i "s/--deadline [^ ]*/--deadline $NEW/" /root/dm/guard-vyv.sh && (cd /workspace/steward/verity && PYTHONPATH=tools/research/src python3 -m research pods guard stop --prefix vyv-) && sleep 2 && sh /root/dm/guard-vyv.sh && echo "$(date -u +%FT%TZ) REARM deadline vyv- -> $NEW (vllm-coordinator {id}: {why})" >> /root/dm/dm.log
~~~

- **Files:** log `/root/.research/pods/guard-vyv-.log`, state `.json` beside it, start script `/root/dm/guard-vyv.sh`. Full terms: this store's `internal/switchover-step9-terms.md`.

## Pods at 16:04Z (11, all under the guard)
a5-g1, a5-t1, a5-tp2d, b1-g2, b1-tp2, b5pat-cpu, b5pat-big, c4ir-reg, gb-cpu, b4b-cpu, b4b-g1. None are orphans; each belongs to a lane above.

## Timers
- The laptop timer `vllm-overnight-sweep-v10` (sub_c6a58271, every 30 min) belongs to the laptop agent and ends with it.
- Re-arm an equivalent sweep on the successor. Its steps are disk, liveness (45 min without a sign of life means hung), merges, slots, money and deadline. Its reporting rule: report only merge requests and blockers, otherwise reply with one line.

## Standing rules (short)
- **Merges:** never merge into main; report merge requests to the root.
- **Credentials:** mint the read-only R2 key on the laptop only (3 h), pipe it into your own pod, and delete it after the fetch. Never print credentials.
- **Run outputs:** no laptop-side fetch of run outputs; use `research run ... --custody-r2`.
- **Laptop:** no pytest, torch or builds; no new `.md` files in the repo.
- **Housekeeping:** use the safe default and report only outcomes.
- **Reporting:** times in PDT.
- **Owner decisions:** all settled. What's held for the owner is the morning list at the top of COORDINATOR.md.
