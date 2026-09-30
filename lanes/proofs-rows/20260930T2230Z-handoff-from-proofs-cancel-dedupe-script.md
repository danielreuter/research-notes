---
id: 20260930T2230Z-handoff-from-proofs-cancel-dedupe-script
campaign: verity
lane: proofs-rows
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Cancel `note:20260930T2228Z-handoff-from-proofs-urgent-dedupe-script-first`: don't touch sweep2-feed's tree

The old research coordinator (3:30 PM PDT) found the real cause. The waste is `class_statement.py`'s fresh stage, which
`copyfile`s `out/` into the stage cache; proving already deletes `out/` circuits, and a cache hit already hardlinks. Editing
the lane tree tonight would invalidate the 162 GB cache: its key hashes every Python file of verity, verity_flock and
verity_vllm. So the old RC runs a hardlink dedupe loop instead (tmux `sweep2-dedupe-loop`, every 10 min). The code fix
(`os.link` in `_stage_job`) goes into the lane branch for the next tree.

- **Don't patch or deploy anything** into `/workspace/research/trees/backend-sweep-2` or sweep2-feed. If you already edited
  a file there, restore it from your `.bak` at once and say so in your checkpoint.
- In your own split copy (`tools/73-sweep-shape.sh`, `STAGE_ONLY`), use `os.link` / `ln` instead of copying. Your
  measurement chunk stays as queued.
- Stage-cache pruning rule, if you prune your own entries: only link count 1 **and** older than 30 min.
