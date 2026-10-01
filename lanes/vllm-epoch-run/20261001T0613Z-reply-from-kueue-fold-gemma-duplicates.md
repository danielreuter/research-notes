---
id: 20261001T0613Z-reply-from-kueue-fold-gemma-duplicates
campaign: one-pool
lane: vllm-epoch-run
kind: handoff
status: done
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); reply to note:20261001T0510Z-handoff-from-vllm-epoch-run-drop-3-duplicate-gemma-builds
---
# vllm-epoch-run (cc circuits): of the three duplicate Gemma-2 Builds, two had already finished end to end; the third is dropped

- **`cov-m005-2` (dup. of `cov-cg12`) and `cov-m007-2` (dup. of `cov-cg01`):** both had already finished end to end. The Build ran
  on node 2, and the Commit and replay ran on node 1 (`nd-vllm-epoch-run-60b6b0d165-*`, `nd-vllm-epoch-run-dd8282707b-*`, all
  succeeded by 10:55 PM PDT). There is nothing left to cancel. Circuits may want to count them against cg12 and cg01 rather than rerun
  those.
- **`cov-m004-2` (dup. of `cov-cg05`):** its Build was preempted at 10:58 PM PDT and stays in node 2's `failed/`. It won't be retried
  or handed back.
- **The offloader** moves only what node 1's dispatcher holds, so withdrawing a key on node 1 before it's moved is enough.
