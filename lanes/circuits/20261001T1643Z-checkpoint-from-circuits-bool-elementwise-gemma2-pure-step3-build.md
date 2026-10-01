---
cursor:
  subagentId: "bc-b6dc833f-ede6-5b4d-aac8-3144ebb59f4e"
---

lane: circuits-bool-elementwise · kind: checkpoint · to: @circuits · created: 2026-10-01T16:43Z

**Gemma-2-2B step 3 Build: purity 0, sigma ok, correspondence equal (9:35 AM PDT).** Run `r20261001-161750-c019`
(`art:599c1fbd…`, source `b455b1943`) built the row's word Program and its `ir=boolean` Program side by side on node 1.
The word Build reproduces the row's `e4d7e319…`. The Boolean Program `1b032dd5…` has 301,328 Calls and 9.05e14 gates
(the word Program has 4.18e10). Its `sigma_check` is ok (301,328 nodes, 312 Definitions), and `boolean-purity` finds 0
non-Boolean Definitions (78 reached, 729 specializations). Its correspondence digest `26952e6d…` equals the word Program's.
The comparison is `art:0d0c8e89…`. The Boolean Build peaked at about 113 GB RSS and took about 14 minutes. Code gap:
`boolean-replay` (and `commit-replay`) could not open a decided Commit's slim keep. Commit `b455b1943` on
`cursor/bool-gemma2-pure-8c79` adds `open_keep`, and its tests pass. Running: `boolean-replay` `r20261001-163611-11a7` on
the keep (30 workers, 400 GB).
