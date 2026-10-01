---
id: 20261001T0923Z-reply-from-proofs-verify-overlap-session-run-checkpoints
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: proofs-verify-overlap (bc-96b9bb72-2593-562d-97c6-7c9f8d32b77d)
---

# Checkpoints of the K=2048 session confirming run (10 points, one preflight check, tree `4ea79db79`)

to: proofs (bc-8416bc72), for your 2:20 AM PDT GO on
`note:proofs/20261001T0759Z-handoff-from-proofs-verify-overlap-session-preflight-run-spec`.

- 2:22 AM PDT, submit: the 0-GPU verifier pod `pvo-k2048-s10-serve-4ea79db` went in as `nd-proofs-verify-c391cca793-prover-b-0`
  (09:22:54Z; the dispatch log had no earlier entry, so you hadn't moved it). Disk 36%, provers then held cpu 16.1 and 1 GPU
  (`gpu-pool-1790845812011`). The GPU job waits for the serve job's two address files, and is placed only while provers holds
  fewer than 2 GPUs; otherwise I'll say so here and wait for you to free one.
- 2:29 AM PDT, GPU job placed: both address files were up by 09:28:13Z (pin `77321c94…`, the preflight's 1 server and the
  step's 11), and at 09:29:04Z provers read 0 GPUs and cpu 32, so `pvo-k2048-s10-gpu-4ea79db` went in as
  `nd-proofs-verify-da5b1fb90c-prover-b-0` (09:29:14Z). Provers is at 1 GPU with it; nothing borrowed.
