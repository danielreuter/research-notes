---
id: 20261001T0216Z-handoff-from-proofs-provers-floor-and-slices
campaign: verity
lane: proofs-flock-fp
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs), on @infra's post `1790820414.927189`
---

**STOP if you are bc-15199603** (started at 10:01 PM PDT by mistake, instead of resuming the original worker): submit nothing, change nothing, and end your turn now with the one line "stopped: duplicate". The original worker resumes this lane.

# `provers` is 2 GPUs + 1 borrowed since 6:52 PM PDT, on cores 128-175: drop `CPUSET=96-…`, pass `CPUS=16`, timed points only in the two slots below

to: proofs-flock-fp (bc-6caad52c), proofs-bf16-hill (bc-3d1a7229), proofs-verify-overlap (bc-96b9bb72); the same note is in
each lane.

1. **Quota (infra, 6:52 PM PDT):** Kueue `provers` has a floor of 2 GPUs and can borrow 1. Commits can reclaim the borrowed
   one, so timed points run only on the two floor GPUs. It's revisited at 11:40 PM PDT.
2. **The two timed slots:**
   - **Slot 1, flock-fp:** the dtype × K grid for the plots (NVF4 K=16384, MXF4 K=8192 and 16384), then the re-runs of
     contended points the plots need.
   - **Slot 2, verify-overlap:** the clean locked overlap C and serial D. Then it hands slot 2 to bf16-hill in its checkpoint.
   - **bf16-hill until then:** stage your steps in 0-GPU jobs, so each one proves straight from the cache once you have slot 2.
     Untimed work (gates, selftests) may use the borrowed GPU, but only while both slots are already running. Kueue preempts the
     last borrower, so a third job submitted first would leave a timed point on the borrowed GPU.
3. **CPU (infra):** new `provers` pods start with affinity 128-175, three 16-core slices that `cpu-slices.sh` cuts from the
   job's own affinity.
   - An explicit `CPUSET=96-…` or `128-159` now lies outside that affinity, and `taskset` fails. Pass `CPUS=16` (one slice
     per job, the same budget as your points so far) and let `hold_slices` take a free one.
   - Every other dispatched job runs on 96-127 and 176-191, so a pod started after 6:52 PM PDT whose `slice_cores.tsv`
     shows no other job carries no `cpu-contended` flag. Earlier points keep their flags.
4. **Staging stays in 0-GPU jobs** (`STAGE_ONLY=1`). bf16-hill: the gate's CPU reference prove still holds the GPU. Move it
   into the 0-GPU stage job when you can, since the CPU proof doesn't need the GPU.

Checkpoint one line when your lane complies, or say why it can't.
