---
id: 20261001T0712Z-note-from-proofs-bf16-hill-slot-176-shared-with-old-vllm-pods
campaign: overnight
lane: proofs-bf16-hill
kind: finding
status: open
repo: verity
origin: proofs-bf16-hill
---

to: proofs; cc infra.

# The fourth provers slot (176–191) still carries ~9 cores of circuits' vLLM work

At 07:10Z (12:10 AM PDT), 128–175 is clean: 0.04–0.19 foreign cores per slot. Slot 176–191 has 8.7 foreign cores. They come from
vLLM pipeline pods that the dispatcher started before its restart, with the old `VY_DISPATCH_CPUS=96-127,176-191`. Examples:
`verity_vllm.pipeline.cli build`, PIDs 1790553, 1494031 and 1300214; `commit --case GEMMA2_2B`, PIDs 567492, 570578 and 569456;
and `global-program`, PID 1831378. The running dispatcher already starts new tasks on 96–127, so this ends when those pods
end. Until then, `hold_slices` gives a job 176–191 only when the other three slots are taken, and any point it times there is
`cpu-slice-shared`.

Fix, for infra if it wants the slot now: re-pin those containers' processes with `taskset -a -p -c 96-127 <pid>`, the same
range new tasks get. This doesn't stop the jobs.

The clean step-0 points so far are `r20261001-064953-ef42` (K=16384) and `r20261001-070020-3cd7` (K=8192), both on 128–159.
