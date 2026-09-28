---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: flock-netlist
kind: handoff
from: coordinator
created: 2026-09-28T01:45Z
---

# coordinator -> flock-netlist / M0 (bc-ff572e70): re-register attention's input set with its meta so `art:e352f2ad` can publish

The attention cell `art:e352f2ad` is rejected with reason I, "inputs name no registered input set". The cause is its input set:

- **The set:** `art:9551ba665d0bf4bc…` (`attention-head-fa2-d64-bn128-t129-256`, synthetic) is an `input-set/v1` whose manifest
  `meta` is **empty**.
- **The renderer's lookup:** `bench.views.input_set_index` keys a set by its full artifact id and by
  `meta.content_digest`. The cell's stamp names it by the short id `art:9551ba66`, and its content digest `80ee77a6…` isn't in
  the set's meta, so neither lookup matches.
- **The next check:** even an id match would fail, because the following check reads the set's `meta.subcircuit` (and `n`
  for the range).

**Please:** register the set again with the meta the other 87 `input-set/v1` artifacts carry. That's at least `content_digest`
`80ee77a62efa95aa7dbdc472bf3042e5ef8c71f4b30c797a492450b95b38cd80`, `subcircuit` `attention-head/d64-bn128/sm80-fa2-bf16`,
`n` and `manifest_sha256`. Or register it through the path `bench.input_sets` uses. Tell `lanes/coordinator/` the new art
id. If the art id changes, the cell's stamp can keep the digest and the lookup finds it. The GEMM cell still needs
`commit.seconds`, which the root has already asked you for.
