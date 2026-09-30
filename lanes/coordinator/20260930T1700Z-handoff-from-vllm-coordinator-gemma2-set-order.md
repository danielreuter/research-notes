---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde; cc consolidation bc-e373566b) · kind: handoff (merge order) · from: vllm-coordinator · created: 2026-09-30T17:00Z

# Gemma-2 set: land #250 first, then #568, #581, and #569 last (after I update it)

1. **#250** @ `da4261e5`, or its next rebase (granted). It moves the MUFU tables to `verity.ml.mufu`.
2. **[#568](https://github.com/danielreuter/verity/pull/568)** @ `0ba8865b` (granted): call boundaries.
3. **[#581](https://github.com/danielreuter/verity/pull/581)** @ `3d18086eaba267b73edf0319bc768bc788f53995` (**granted now**): replay rows for the 15 dense Definitions, exact on the PRO 6000 (job 268, 450/450). It's clean on main `b1134766`, with #250 and with #568.
4. **[#569](https://github.com/danielreuter/verity/pull/569):** hold it. Its softcap row reads `prims._tanh_shards`, which #250 removes. That's what failed #250.
   - Once #250 is on main, I'll push the two-line switch to `verity.ml.mufu` on #569's branch myself (its lane lost GitHub auth) and re-grant.
   - It also conflicts with #581 at the end of `rows.py`, where both append a registration block. Keep both; I'll resolve that in the same update.

**Don't train #569 at `91947326`.**
