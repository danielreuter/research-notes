---
id: 20261001T0034Z-handoff-from-proofs-cpu-split-approved
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# CPU split approved: you on 96-127, flock-fp on 128-159; re-run your two baselines on the new defaults

- **The split is approved** as you proposed: you pin only inside 96-127, and proofs-flock-fp pins only inside 128-159. I
  told flock-fp to take your `cpu-slice-shared` sampler.
- **Re-runs:** your K=2048 and K=4096 points on the console carry `coins-seed-mode` and `session-not-batched`. Re-run all
  four K with `os-seed-prf` coins, in a batched session (`batched-J1` on the GPU, because the device prover refuses
  `--session-tables` above 1), on the census id `rtx-pro-6000-server/bf16`.
- **Order:** K=8192 and K=16384 first, since they have no point yet, then K=2048 and K=4096 again. That's the 7:40 PM PDT
  mark (BF16 at all four K).
