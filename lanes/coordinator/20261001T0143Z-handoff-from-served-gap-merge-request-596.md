---
id: 20261001T0143Z-handoff-from-served-gap-merge-request-596
campaign: pouw
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: served-gap profile (bc-ccd30e80); coordinator compute-accounting (bc-e90634dd)
---

# served-gap -> research coordinator: merge request for #596 (Pearl-C `-h2` on the served path, and the stack under it), head `10b5526b`

[#596](https://github.com/danielreuter/verity/pull/596), branch `cursor/served-gap-h2-spread-76ee`, head `10b5526b66298e011e7127fca4fae23960240cc9`.

- **Why now:** Daniel approved `-h2` on the served path at 1:36 PM PDT. Window 7 timed #596's `05ce9ce4` (`r20260930-221231-3dd1`) and its verify passed at 6:37 PM PDT: accept, accept, reject, reject. Its panel rows are with bc-2aa33ad8: decode **3.402× over graphed stock FP8**, 1.263× over eager.
- **The check:** `r20261001-004441-884b` (`check.py --record --on vy-nebius-2` at `10b5526b`) **passed**. `lean-agreement` is skipped, since nothing under `backends/flock/` changes.
- **`main` has moved:** it is at `4860d817` (train TCX), 126 commits past #596's last merge of `main` (`e15dc1ef`).
  - `git merge-tree` of `10b5526b` with `origin/main` merges cleanly.
  - So it needs `research merge --train cursor/served-gap-h2-spread-76ee --on vy-nebius-2 --project verity`, or a fresh merge of `main` and a check from me. Say which.
- **What it lands:** #596 carries the whole unmerged served-path stack, so merging it into `main` lands all of these. Their PRs then close as merged:
  - #435, #540, #564, #573, #576, #578, #585 and #593;
  - #591 at `8b060461`;
  - #572 at `d20e4d16` (its head when merged here; #572 has since moved to `9288c339`, with #449's `1b1895bc`).
- **Since window 7's tree:**
  - the fork-pool fix (#572 `d20e4d16`);
  - `panel_rows.py`'s headline over graphed FP8, with the eager row beside it;
  - the `verity-vllm` lint fixes, including the split of `pouw_pearl_c_device.py`;
  - the TP2 MoE re-pin (#572's `fe92c61a`, bc-f9184c6e's call);
  - #593's per-call trims (`10b5526b`, compute-accounting's YES at 5:42 PM PDT).
  - None of these touch `run.py` or the cubin.
- **Timing:** window 8 runs #610 (`e442d494`, on `10b5526b`) tonight. Merging #596 doesn't change #610's tree, but if you'd rather land it after window 8, that's fine.
