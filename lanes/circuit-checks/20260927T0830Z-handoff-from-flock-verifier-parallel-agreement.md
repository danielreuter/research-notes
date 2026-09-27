---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: circuit-checks · kind: handoff · from: flock-verifier · created: 2026-09-27T08:30Z · re: PR #134's lean-agreement step

# The agreement job runs in parallel: PR #118 at `d13f8f71`

**Nothing to change in `check.py`.** `ci.py` without `--session-jobs` now shares one budget of verifier processes among all the
sets it runs. The budget is the cores and the available memory at 8 GB a process, whichever is smaller. Keep passing
`--jobs` (sets at once) as you do.

**How it works.**
- **Chunks.** `agree.py --jobs J` deals each public file's sessions round-robin into chunks of four or more. Each chunk gets
  one Lean and one upstream process, and each drawn session gets its own upstream process, as before.
- **Shared slots.** `ci.py` calls `agree.py` in-process, and every set's processes draw on the same slots. Once the short
  sets finish, the longest set's remaining chunks take their slots.
- **Deterministic output.** The verdicts are reassembled in the sequential run's order. `agreement.tsv`, `result.json` and the
  verdict logs `lean.txt` and `upstream.txt` are byte-identical to `--jobs 1`; I checked this on set 8. Only the `.err`
  timing logs differ.

**Timing,** measured on a 4-core, 15 GB VM:

| what | before | now |
|---|---|---|
| set 8 alone, `agree.py --jobs 4` | 156 s | 62 s |
| sets 8 and 10, `ci.py --jobs 2 --session-jobs 4` | about 290 s | 124 s |

**Estimate for check.** On a machine with C cores and at least 8 GB per core, the 21-minute run should take roughly the total
verifier work divided by C. That work is the sum of every set's sequential time, plus about 20 s of statement setup per
chunk. For a 16-core pod I expect about 5 minutes; please record the real figure with your first run. On this 15 GB VM the
default is one process: the memory cap wins.

**Note.** Set 13 (GEMM, m = 26) needs more than 15 GB for upstream's replay. On a small machine, run it with
`--session-jobs 1`, or leave it to the pod.
