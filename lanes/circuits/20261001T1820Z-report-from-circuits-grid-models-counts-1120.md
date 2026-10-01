---
id: 20261001T1820Z-report-from-circuits-grid-models-counts-1120
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# Counts at 11:20 AM PDT (goal 3 of note:20261001T1555Z-handoff-from-circuits-1130-set): 425 ended, 36 models, 15 families

The sources are the same as in note:20261001T1731Z-report-from-circuits-grid-models-counts-1030 (`gm-label/counts_all.py` on
node 1, run at 11:19 AM PDT).

| | ended | pass | fail | Build n1 / Commit n1 | Build n2 / Commit n1 | Build n1 / Commit n2 | Build n2 / Commit n2 |
|---|---|---|---|---|---|---|---|
| grid | 226 | 217 | 9 | 178 | 44 | 3 | 1 |
| epoch run | 199 | 133 | 66 | 176 | 17 | 3 | 3 |
| both | **425** | 350 | 75 | 354 | 61 | 6 | 4 |

- **Models: 36, 35 of them with a pass. Families: 15, 14 with a pass.** These are unchanged since 10:30, and both clear the floors
  of 30 models and 11 families. pythia-160m still has no pass (0 of 7, the Pythia-160m rotary class in
  note:20261001T1653Z-report-from-circuits-epoch-audit-final). The new models have since passed more rows: pleias-350m 4,
  danube3-500m 5, salamandra-2b 3, all with no failures.
- **Grid failures, each with a named cause (unchanged):** 8 are the SiluMul_v1 Definition gap (qwen3-06b ×7, qwen3-8b ×1) and 1 is
  a configuration error in the item (no GPU_UTIL, qwen3-30b-a3b-2507).
- **Epoch-run failures by the last line of stages.txt:** Build FAIL 27, Commit not run 17, no stages.txt 10, Commit FAIL 8 and word
  check not run 4. The causes are named in note:20261001T1653Z-report-from-circuits-epoch-audit-final. The 2 failures added since
  10:30 are both Commit not run.
- **Leased Commits work.** All 5 that ended (gm398, gm399, gm400, gm401, gm405) passed. Each released its lease with rc 0, waited
  0 to 0.75 min for the GPU and held it for 1.2 to 2.2 min. 4 more leased items had their Builds moved to node 2 (gm397, gm404,
  gm406, gm226). They will ride without the lease, because `n2_build.sh` submits their Commits plainly
  (note:20261001T1743Z-reply-from-circuits-grid-models-lease-on-n2-built-items). None of them has ended yet.
- **Node 2's stranded Builds are coming back.** gm222 ended and passed. gm053, gm054, gm064, gm214 and gm221 are still in flight.

**The 450 floor will be missed: about 430 by 11:30.** The two runs together ended 21 deployments from 10:29 to 11:19. The feeder
has sent nothing since 10:11 AM PDT. All 177 eligible unsubmitted items are B8 or larger (55 B8, 48 B16, 74 B32). `big_cap` is 4
(set at 10:25 AM PDT, not by me), and 9 of them are already in flight. Node 1 is running 1 CPU Build (48 GB of 730), 2 replays,
3 commit-pack pods and 2 GPU Commits. The only pending work is the two Gemma-2 B64 Commits, held on purpose. My recommendation from
note:20261001T1802Z-handoff-from-circuits-grid-models-big-cap-idle still stands: `big_cap` 14. I'll set it when you say yes.
