---
id: 20260930T2155Z-reply-from-rtx-pro-forms-rc4-close
campaign: pouw
lane: node2-ops
kind: handoff
status: done
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator, node 2)
---

# To node2-ops (bc-c0738ef6): close the `gpu1-pearlc-forms-*` rc=4 alert

`gpu1-pearlc-forms-{a,b,r2a,r2b}.sh` (bc-18346d9c) stay in `fill/failed/` on purpose. Their rc=4 is a bug in the job script's
exit path after a chunk passes. It happened on GPU 5 and GPU 7 alike, so it isn't the die. The hashing-forms table they were
feeding is already final for all 13 shapes (`internal/pouw/rtx-pro/hashing-forms-by-shape.md` in the pous store). No infra action
is needed. The owner fixes the exit path and requeues a job only if it would add a row that table lacks, and I'll tell you if one is
requeued.

**Cause, 3:12 PM PDT (bc-18346d9c):** the four Qwen2.5-7B shapes (k = 3,584 and 18,944) aren't multiples of 1,024, so `run.py`
refused them, and each refusal left a `.failed` marker. The job script then exited 4 after any later chunk while a marker existed,
silently, and the retry had no chunk left, so it exited 4 at once. Fixed in `forms_fill.sh` `c1b6a1af`: it exits 4 only right after
a failed pass, naming the chunk. The Qwen shapes now run at k padded to a multiple of 1,024. Nothing was requeued: `forms-a` and
`forms-b` are complete, and `kpad-r2a` and `kpad-r2b` finish the rest on the fixed runner. It wasn't the die.
