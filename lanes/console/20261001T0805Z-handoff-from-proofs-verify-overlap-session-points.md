---
id: 20261001T0805Z-handoff-from-proofs-verify-overlap-session-points
campaign: overnight
lane: console
kind: handoff
status: open
repo: verity
origin: proofs-verify-overlap (bc-96b9bb72-2593-562d-97c6-7c9f8d32b77d), for proofs (bc-8416bc72)
---

# Hillclimb roll-ups will hold several points per run and step: key rows by run and point index

Daniel said yes (12:05 AM PDT) to one preflight check per GPU session, which amortizes the check over several points. A session
is one job: one tree, one binary, one `FC_*` set and one K. It runs the preflight check once, then N points of the same
statement. The first such run (K=2048, 10 points, step 8) waits on the research owner's yes. Its spec is
`note:20261001T0759Z-handoff-from-proofs-verify-overlap-session-preflight-run-spec`. I haven't edited the console's code;
this is the change its hillclimb reader needs.

## What changes in the data

- **N points per run:** a session's Attempt declares N `hillclimb-point/v0` outputs (`hillclimb-0` … `hillclimb-<N-1>`).
  `gemm_hill.py rollup` appends each one to `/workspace/usage/hillclimb/<subcircuit>.json`.
  - All N share `run_id`, `step`, `label` and `commit`; `point.index` tells them apart.
  - `rollup` used to skip a point whose `run_id` was already in the file. It now skips only a repeated (`run_id`,
    `point.index`) pair.
- **New fields in every point.** These are additive; the schema stays `verity/hillclimb-point/v0`:
  - `point: {index, of}`. A one-point run has `{0, 1}`. Older points lack the field: read them as `{0, 1}`.
  - `preflight: {output, record_sha256, status, key, key_matches}`: the session's one preflight check, which the point
    cites, and whether the point's key equals the check's. A point whose key differs has `byte_identical: false` and a
    `why`.
  - `gpu_held_s_point`: the point's own sweep.
  - `gpu_held_s_session`: the whole session's GPU-held seconds, the same on each of its points.
  - `gpu_held_s_amortized`: the point's sweep plus an equal share of the seconds outside every point (pod start, the preflight
    check, the gaps). The N values sum to the session's.
- **Unchanged:** `gpu_held_s_per_vu`, `overhead`, `throughput_vu_per_s` and `gpu_util` still describe the point's own timed
  sessions.

## What the reader needs

1. **Key rows by (`run_id`, `point.index`), not by `run_id` or by `step`.** Otherwise a session shows as one row, and nine
   of its ten points are lost.
2. **Two columns:**
   - Point, shown as "i of N" (blank or "1 of 1" for older points);
   - GPU-held s per point (amortized), from `gpu_held_s_amortized` (blank for older points).
3. **The page note:** "One row per step" becomes "One row per point; a GPU session's points share one step and one run".
4. **The plots:** a session puts N points at one step. Drawing each is fine, and so is a median with its range. The
   best-so-far line already takes the lowest byte-identical point.

If the reader already keys by something else, a one-line reply here saying what it keys by is enough; I'll match the records
to it.
