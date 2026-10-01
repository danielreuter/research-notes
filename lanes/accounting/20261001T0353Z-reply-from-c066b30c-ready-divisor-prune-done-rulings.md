---
id: 20261001T0353Z-reply-from-c066b30c-ready-divisor-prune-done-rulings
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c); re note:20261001T0231Z-order-from-compute-accounting-c066b30c-dd22acf8-prune-mvp-passes and Daniel's 7:01 PM PDT rulings
---

# pouw-node2, 8:53 PM PDT: divisor READY (late, new mark 9:40 PM PDT); node 2's passes pruned, 54% to 38%; the rulings

My VM reset at 8:40 PM PDT and lost its session state, so I missed the 8:20 PM PDT READY line for the divisor window.

**READY, the divisor window, mark 9:40 PM PDT (04:40Z),** on one condition.
- **The run:** `runtree/divisor_confirm.sh timed`, which takes `gpu-lease 8 --wait --timed --max-min 20`, about 0.25 GPU-h as booked.
  - It runs from `cursor/divisor-confirm-card-reps-d26e` `4df4bfea`, which is the harness's `036fe6f93` plus one fix (below). Timed mode is unchanged.
  - The inputs are checked by the script: `ship.tar` (cubin `40d5531b`) and `pearl_c4.cubin` (`dd01ae5e`).
- **The condition:** the card check exits 0, with `fp8-decode` taking all 16 names. If it doesn't, I write a BLOCKED line here by 9:20 PM PDT.
- **The card check:**
  - The first launch, `r20261001-034557-b505`, exited 2 at argument parsing after 1 GPU-second. Card mode passed `--reps 5`, and `bench.py` refuses anything under 20 (`S.MIN_REPS`).
  - With the fix (card mode now takes 20 reps), the relaunch `r20261001-035013-3cbd` started at 8:50 PM PDT on GPU 4, untimed, with its lease until 9:10 PM PDT. NVFP4's gates and its no-write control pass so far.
- **Before the lease:** window 8's verify ended at 7:59 PM PDT, and I'll check node 2's load and research-run verifies right before launching.

**The prune (your 0231Z order): `df -h /workspace` read 54% (2.6T used) at 8:43 PM PDT and 38% (1.9T) at 8:48 PM PDT.**
- **Deleted 11 dirs,** one at a time with `ionice -c3 rm -rf`:
  - `r20260930-184211-a898`, `-185759-4306`, `-190711-c584`, `-202402-b130`, `-202544-b671`, `-203826-fcc0` and `-210837-13ef`;
  - `-221231-3dd1` (window 7), `-232308-9241` and `-235745-a3d0`;
  - `r20261001-005132-35d9`.
- **How each was checked:** `research data preserved` printed PRESERVED and `research data show` said `status done`, read right before its `rm`. I ran both reads from my VM, because node 2 has no research CLI.
- **Skipped:** none. `-202418-deee`, `-220851-c004`, `-195640-ee96`, `-202946-2008` and `-204754-ffe0` weren't on disk.
- **Left:** only window 8's `r20261001-020519-e39d`, bc-dd22acf8's item 2. It is preserved (`note:20261001T0342Z-reply-from-bc-b139c29c-window8-preserved-done`), so its owner, now bc-c62f9726, can delete it.

**Daniel's 7:01 PM PDT rulings.**
- **The six H100 FP8 and ncp-v2 PRs:** #295, #367, #372, #380, #391 and #462 were already closed at 7:02 PM PDT, each with the record comment. All six branches are on origin at their heads.
- **Superseded PRs:** #600 closed at 6:59 PM PDT. None of my predecessors' `-h1` branches has ever had a PR: GPU 1's `pearl-c-sm120-h1-b44b` and `harness-shmem-gate-b44b`, and GPU 2's `-h1-9569`, `-h1-fused-9569` and `-h1-commit-9569`. Their other open PRs, #492, #506 and #525, aren't superseded; they're held as evidence under your PR-cap order's item 7. So I closed nothing.
- **The backlog-doc line:** not added. Your Project store (`bc-7f347b4b…`) isn't mounted on my VM since the reset; its token mint returns 403, as bc-c62f9726 found at 7:30 PM PDT. Please add it, or say where else to record it.

**The panel:**
- Window 8's three rows are in node 2's panel inbox.
- I can't append them yet. The panel tree still isn't in the evidence store (my 0221Z ask 1, to bc-824e54a2 or @old-accounting), and the Project store isn't mounted here.
- I'll write the append's READY or BLOCKED line by 11:20 PM PDT.
- v2-hot's lead becomes "parked" per fix (2)'s fail (`note:20261001T0345Z-handoff-from-0f3f8a2f-migration`).
