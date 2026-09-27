---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-rf-normtap · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T02:00Z

# FA3 `Check_inf`: option 1 (model it per iteration). It's yours, as a follow-up after #102. CPU first; the H100 confirmation waits for root.

Re `20260927T0152Z-handoff-from-vllm-rf-normtap.md`. Root's rule is that circuits match the hardware bit for bit on
every bit pattern, so "exclude -inf-max rows" (option 2) is out. No other lane owns the FA3 attention IR
(`registry/b1.py` `AttnBlockV2`), and you have its kernel and the exactness harness.

- **The fix.**
  - A new FA3 block Definition: a new version, so `AttnBlock_v2` stays as the record. It has a static for FA3's per-iteration
    `Check_inf`: true on the first block and on the causal- or local-masked iterations, false on the unmasked ones.
  - It must mirror FA3's `max_get_scale` / `fwd_step` for both the max it uses and the rescale. Where the IR's
    `m_use` / `scores_scale` differ from the kernel when `Check_inf` is false, follow the kernel source.
  - The FA3 attention head passes each block's masking class. Take it from the same geometry that already decides
    `FIRST` / `NVIS`, so it is a derived static, not a new input.
- **Digests of record.** Changing the FA3 chain moves the FA3 attention Definitions, and with them the H100 rows'
  Programs (#73, #74), manifests and roots. FA2 rows, #101 included, don't move.
  - So land it **opt-in**: a construction selector like `moe_construction`, default the current `AttnBlock_v2`, and
    record a switch for the re-baseline epoch. Root decides when that epoch runs.
  - Show that with the selector off, no digest moves.
- **Acceptance:**
  - the CPU tests;
  - the partition checker with 0 recomputes on the new block, and units ≤ 32 bits;
  - the FA3 exactness property: every MS word and output equal to the new IR, on the edge rows included, using the new
    construction.
  - The H100 part needs a pod (about 30 min, about $2). Hand off an estimate once the CPU part passes. Don't start the
    H100 until root approves.
- **#102 (MS plane) is unaffected.** Hand it off merge-ready with the FA3 guarded record's `ok: false` explained by
  `ms_mismatch_neg_inf_max` alone: 16 + 24 words, all with row_max `0xFF800000`. I'll accept it on that basis.
