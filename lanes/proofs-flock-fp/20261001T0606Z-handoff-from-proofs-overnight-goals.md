---
id: 20261001T0606Z-handoff-from-proofs-overnight-goals
campaign: verity
lane: proofs-flock-fp
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs), on Daniel's overnight goals (10:58 PM PDT) relayed by the top-level
---

# Overnight goal (due 7:50 AM PDT): every format at all four K, hill-climbed as far as it goes, flags cleared

to: proofs-flock-fp (bc-15199603) and proofs-bf16-hill (bc-89f3138c); the same note is in both lanes.

**The goal (Daniel):** overhead against K for BF16, E4M3, NVF4 and MXF4 at K = 2048, 4096, 8192 and 16384, *hill-climbed as
far as it will go*, not just shown. A cell counts when its newest point carries neither `cpu-slice-shared` nor
`draft-554-unreviewed`. Checks at 2:05, 4:50 and 7:50 AM PDT count the cells and each cell's best overhead.

1. **Still first: leave two `provers` slices free until verify-overlap's pair has submitted** (`…T0559Z`; the check is in
   that note). flock-fp: your e4m3 K=8192 clean2 and nvf4 K=8192 points went in at 06:01–06:03Z beside the K=16384 stage
   job and proofs-arch's CPU job, so four pods share three slices; expect `cpu-slice-shared` on both and re-run them after
   the pair.
2. **Then borrow every idle GPU (Daniel).** Infra is raising `provers`' GPU borrowing limit and widening its CPU range to
   match; Commits still take GPUs back. Run one point per free 16-core slice (count the slices in your pod's affinity, or
   `kubectl get clusterqueue provers -o jsonpath='{.spec.resourceGroups}'`), staging jobs included, and never two jobs on
   one slice. A preempted point is re-run, never reported.
3. **Climb every cell, not only BF16.** The format-independent levers so far: the column-major verifier fold
   (`d1775df80`), the verifier overlap (`FC_VERIFY_AHEAD=10`), the verifier in its own 0-GPU pod (verify-overlap's how-to,
   `…T0539Z`), slot circuits only on a stage-cache miss (`bd9852624`) and the gate's self-tests at once (`4110f98dd`, branch
   `cursor/proofs-verify-overlap-95d4`). flock-fp: bring them to the FP trees and climb E4M3, NVF4 and MXF4 at all four K.
   bf16-hill: the ladder at every K (step 1 and the overlap are measured only at some K so far). Each step names its
   question; Daniel's word covers climbing these cells, so nothing more is needed to start.
4. **`draft-554-unreviewed`:** `gemm_hill.py` adds it to every point unconditionally. I've asked red-team-flock-3 to review
   #554 (`8a0b17250`): whether non-tile statements are byte-identical to main's, and the 4x4 tile statement and pins. When it
   grants, bf16-hill changes the flag to fire only for statements the grant doesn't cover, and flock-fp mirrors the change.
   I'll say when.
5. Unchanged: staging and CPU-only steps in `gpus: 0` jobs, `CPUS=16`, one point per job, each with its question.
