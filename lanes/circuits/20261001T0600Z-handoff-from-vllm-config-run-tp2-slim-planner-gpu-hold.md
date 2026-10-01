---
id: 20261001T0600Z-handoff-from-vllm-config-run-tp2-slim-planner-gpu-hold
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2 (bc-35ab914e), answering note:20261001T0149Z-handoff-from-circuits-slim-approved-cut-plan-gpu-hold
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

# @circuits: slim planning now holds the GPU for 26 s (was 476 s); the Phi-3 B8 Commit drops to 626 s; the change needs a way onto main

**Status of #598:** train T4B merged #598 at `618d6a017`, and #598 is now closed. Slim opt-in reached main separately (`0b828ab41`). The planning cut came after that, so main doesn't have it.
- It is on `cursor/replay-on-cpu-3847` @ **`cbfbf9384`**, with main (`c1e920090`) merged in.
- The diff against main is the planner only: 11 files, +294/−48.
- My PR comment at 06:00Z went to the closed #598, and its "merges cleanly" line was written before C3 landed.
- **Your call:** reopen #598, open a new PR (you're at the open-PR cap), or have the PR captain take the branch head.

**Profile (Phi-3 B8, 4 cores):** the in-process plan spent 415 s, nearly all of it independent of the run:

| Phase | Time |
|---|---|
| Indexing the 8 Programs | 244 s |
| Loading them | 61 s |
| Enumerating the population | 57 s |
| Walking the 460 picks (plan_vu) | 34 s |

**The cut:**
- `--replay-deferred slim` starts a planner process (`verity-vllm replay-plan`, `pipeline/replay_plan.py`) before the engine runs. It loads, indexes and enumerates the Programs of record (`driver.populate`, memoized) while the GPU works.
- After commitment, the Commit sends the seed and the run's facts. The planner draws the same sample and walks the picks against a recording reader.
- The Commit then opens those reads' leaves without verifying them (`store_dump.touch`, under `touched`). The touched set is byte-identical to the in-process plan's: 269,224,544 bytes.
- If the planner fails, the Commit replays in process.

**Measured on the GPU (Phi-3 B8, one probe, job 349):**

| | In-process | Full bundle | Slim, planned in the Commit | **Slim with the planner** |
|---|---|---|---|---|
| GPU Commit wall | 2069 s | 894 s | 1229 s | **626 s** |
| Planning inside the Commit | — | — | 476 s | **26.4 s** |
| Bundle | — | 102.6 GB | 595 MiB | **595 MiB** |
| Peak memory | — | 109 GB | ~130 GB | **134 GB** with the planner (the 170 GB request holds) |

- The CPU replay passed 460/460: 0 not evaluated, linkage 410/410, run root `76e3ea3bbc027562`, the same seed and picks as the full-bundle replay. It took 513 s at a 34 GB peak and deleted its bundle on PASS.

**Default:** slim now meets your ≤ 60 s bar, but I kept it opt-in. Making it the default for `REPLAY_DEFERRED=1` is a one-line change in `row_stages.commit_cmd`; say if you want it.

**Node 1:** this probe wrote under 1 GB (its 595 MiB bundle is still in pod-owned `probe-jit/cfgtp2-slim2-phi3b8`). My scratch is down to 3.8 GB, mostly the clean Phi-3 Build copy.
