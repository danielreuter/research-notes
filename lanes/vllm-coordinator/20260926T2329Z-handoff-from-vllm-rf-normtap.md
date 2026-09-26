---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-normtap (agent bc-12c2f2d9)
created: 2026-09-26T23:29Z
---
# Finding that changes the tap list: the FA stream does not carry `max * scale`, which the no-recompute cut commits

The guarded-max tap (PR #95, draft) is on track; its merge-ready handoff follows.  While building it I found a second attention value that
serving does not commit.

- **The cut commits it.** In every attention block, `max_scaled = F32MulFtz(m_use, scale_log2)` is read by each of the block's exp2
  units: `p[c] = MufuEx2Ftz(F32FmaSubFtz(s[c], scale_log2, max_scaled))`, in the bodies of `AttnBlock_v3` (FA2), `AttnBlock_v2` (FA3)
  and `AttnBlockSoftcap_v1`.  So the no-recompute cut commits one `max_scaled` per (head, key block, query row), whenever the block has
  more than one visible key.  Unlike the guarded max, this includes the first block.
- **The stream does not carry it.** `docs/fine-query-plan.md` §3 and `committed_today` on `cursor/no-recompute-partition-289b`
  (`_STREAM["F32MulFtz_v1"] = "ROW step (max * scale)"`) map it to ROW word 2.  Both taps write the kernel's visit index there instead:
  `rowstat` in `verity_tap.h` / `verity_tap_fa3.h` does `dst[2] = __int_as_float(step)`, where `step` is the loop counter `vt_step`, and
  `hidden_stream.thread_message` reads it back as the block's step.
- **Size for #101.** It is about 243 k words: 32 heads × 16 layers × (384 prefill + 93 decode blocks), less the blocks with one visible
  key.  The partition-checker run `r20260926-232341-8c37` will give the exact count; I'll put it in the merge-ready handoff.
- **Where it could go.** The ROW entry has no free word once the guarded max takes word 3 (0 row_max, 1 rescale, 2 step, 3 guard, 4-7 lane
  sums).  Options:
  - (a) a ninth ROW word or a new plane, which changes the layout and the buffer size;
  - (b) under a flag, ROW word 2 carries `max_scaled` instead of the visit index, which the block index and `n_block_max` already
    determine.  This breaks "fields 0–2 unchanged" and the thread-leaf mode's use of word 2.

  This is your decision; PR #95 does not depend on it.
