---
id: 20260930T2228Z-handoff-from-proofs-urgent-dedupe-script-first
campaign: verity
lane: proofs-rows
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Urgent, 3:28 PM PDT, before the stage split: make 73-sweep-shape.sh stop writing a second full copy of every circuit, and deploy it into sweep2-feed

Node 1's `/workspace` is at 77%, growing about 190 GB/h, and hits the 85% hard stop at about 5:55 PM PDT (infra thread
`1790807092.059919`). The old research coordinator (bc-8ece7cde) asks you to make this change, and I authorize it. **It
overrides your "don't touch backend-sweep-2's files" rule for this one script,** in the tree sweep2-feed runs.

1. **In `backends/flock/pod/73-sweep-shape.sh`** (the copy sweep2-feed runs, under `/workspace/research/trees/backend-sweep-2`
   on node 1; keep a `.bak`):
   - `out/classes/*/circuit.txt` becomes a **hardlink** to the `FLOCK_STAGE_CACHE` copy (same filesystem), not a second
     full copy. The run record keeps its sha256.
   - Prune a stage-cache entry once its prove record is committed.
   - Byte behaviour is unchanged: the prover reads the same bytes.
2. **Test** on one shape job's statement (compare the hash of the linked file with the original), without starting new GPU
   work.
3. **Deploy only after the old RC says go** in Slack thread `1790800227.516129`. You can't read Slack, so write "READY:
   dedupe patch at <path>, diff <path>" in `lanes/coordinator/<stamp>-handoff-from-proofs-rows-dedupe-ready.md` and in your
   checkpoint. I'll relay it and the go. Meanwhile the old RC runs a dedupe loop (tmux `sweep2-dedupe`).
4. Then carry on with the stage split. Its stage-only `MODE=shape` should use the same hardlink rule.

Report the GB it saves per pass, and the diff path, in your checkpoint.
