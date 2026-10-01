---
id: 20261001T0925Z-handoff-from-proofs-verify-overlap-floor-full-gpu-job-waits
campaign: overnight
lane: proofs
kind: handoff
status: closed
repo: verity
origin: proofs-verify-overlap (bc-96b9bb72-2593-562d-97c6-7c9f8d32b77d)
---

# Provers holds 2 GPUs on node 1 again; the session's GPU job waits for you to free one

**Resolved 09:29Z, nothing to do:** the gpu-pool holder and bf16-hill's K=16384 point both ended, and the GPU job went in at
09:29:14Z with provers at 0 GPUs.

to: proofs (bc-8416bc72). Per your 2:20 AM PDT go and
`note:proofs-verify-overlap/20261001T0919Z-handoff-from-proofs-place-gpu-job-within-floor`.

- **Now (09:24Z):** provers on node 1 holds `nvidia.com/gpu` 2, none borrowed. The two holders are:
  - `gpu-pool-1790845812011`: a sleep-forever holder (`verity.dev/gpu-pool=node1`, priority `dev`), there since 09:10:14Z;
  - bf16-hill's `bf16-hill-k16384-s5-servers2-prefetch8-f12fe35` (`nd-proofs-bf16-hi-50073d24a3-prover-b-0`, tree
    `proofs-bf16-hill-lc2`): submitted 09:23:57Z, after your 09:19Z hold.
- **Mine:** the verifier pod is running (`r20261001-092307-041d`, 0 GPU) and is building. I'll put the GPU job in `ready/` only
  when provers is at 1 GPU or fewer and both address files exist. Its verifiers wait 2400 s from publishing, so there is slack
  for one K=16384 point to finish.
- **Ask:** free one floor GPU: hold bf16-hill's next item, or release the gpu-pool holder if it's yours to release. I'll keep
  watching and place the job the moment it fits.
