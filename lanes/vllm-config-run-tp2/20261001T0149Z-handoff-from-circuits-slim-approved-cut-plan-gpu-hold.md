---
id: 20261001T0149Z-handoff-from-circuits-slim-approved-cut-plan-gpu-hold
campaign: verity
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: slim bundles approved; first the #572 merge, then cut the plan's 476 s off the GPU; the cap semantics

Great result: 102.6 GB → 595 MiB at 460/460, fail-closed on any unretained read.
1. **Still first:** merge #572 into #598 (`note:20261001T0144Z-…`). TPH failed on #572's own tests; the re-cut is TPI = main + #572 + #628
   (`r20261001-014441-50a0`). Merge #572 @ `9288c339`, or main once TPI lands, into #598 @ `d2fe2258` (which now has the slim path), resolve
   commit.py / evaluate.py / `p10_size.json`, and post the head.
2. **Then the GPU hold.** GPUs are the scarce resource tonight (Daniel, 6:35 PM PDT), and the plan adds 476 s to each deferred Commit's GPU
   hold. Goal: ≤ 60 s added. Profile it first; if it's Program decode or encoding, cache per Build digest and parallelize. If it can't
   get there, move planning out of the GPU task: the Commit hands the retained store to the CPU replay task, which plans and slims it, so a
   full bundle exists only between the two tasks (the pacer covers that window). Measure GPU hold before and after on Phi-3 B8.
3. **The cap:** keep `--replay-bundle-cap-gb 300` per bundle as the safety. The node-wide total of unreplayed bundles is enforced by the
   steward's pacer on node 1 (`~/commit-release/release.py`: projected total < 300 GB, latch to 150 GB at 78% disk). With slim
   bundles it will rarely bind.
