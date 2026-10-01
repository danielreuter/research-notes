---
id: 20261001T0620Z-report-from-vllm-epoch-run-wake-done
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: vllm-epoch-run (bc-21460bd7, continuing bc-75fd4007)
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-10-01T06:20Z (11:20 PM PDT) · on your 10:55 PM PDT wake

Done, 11:20 PM PDT. Your 18 Gemma-2 cg rows are adopted and labelled: 6 pass, cg02–cg04 fail with your word-check cause and won't be rerun, and 9 are still running. The old feeder (still alive on bc-75fd4007's VM, labelling only) had wrongly noted "MAX_GATES raised" on cg08, cg14 and cg18; I corrected it, because all three pass at the default MAX_GATES, so at B>1 the 256k-vocab sampler fits W=32. The six B64 Builds went out at 11:13 PM PDT (`cov-m001-2`, `cov-n048-2`…`cov-n052-2`, i256 first; disk 31%). Their Commits need the steward to lift release.py's B64 hold, which I've asked for. The Gemma-2 TP2 canary p058 already failed at the Build, so the other 10 stay held. g160 and n105 stay labelled fail with the EOS cause. TP2's 13: 6 pass, 6 fail on the staging or MoE gaps, and p085 is held, so there's nothing left to pace. The duplicates m005-2 and m007-2 reproduced cg12's and cg01's run roots byte for byte. Labeller: `lanes/vllm-epoch-run/labeller/` (tmux `epoch-label`, stateless).
