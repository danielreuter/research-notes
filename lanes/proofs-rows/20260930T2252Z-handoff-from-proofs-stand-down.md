---
id: 20260930T2252Z-handoff-from-proofs-stand-down
campaign: verity
lane: proofs-rows
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Stand down, 3:52 PM PDT: backend-sweep-2 is stopped (Daniel), so don't swap 73-sweep-shape.sh

At 3:49 PM PDT Daniel said "forget about the vLLM deployments", and at 3:51 PM PDT the old research coordinator stopped
backend-sweep-2 (feeder killed, jobs deleted; `sweep2-feed/STOPPED.json`).
- **Deploy nothing** into `/workspace/research/trees/backend-sweep-2`. If you already swapped the script, restore the `.bak`
  and say so in your checkpoint.
- **Delete your own backfill Job** `split-prove-f1e4d147-m1` (`nd-proofs-rows-c38abf8279-prover-b-0`), and stop tmux
  `proofs-rows-split`, killing only pids you started. Remove your node-1 scratch under `/workspace/jobs/proofs-rows/` except
  `measure/` and `tools/`.
- Leave your recipes and diffs in the notes as backlog. The stage/prove split is kept for the new GemmCoordinate hillclimb.
- Write FINAL with what you removed and the GB freed.
