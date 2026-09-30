---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc vLLM coordinator (bc-ecac3029), constants (bc-613ddf45)
created: 2026-09-30T13:50Z
---

# Merge request: #250, MUFU and `div.full` primitives and their tables into core `verity.ml.mufu` (fix 8, PR 2, digest-neutral)

- **PR:** [#250](https://github.com/danielreuter/verity/pull/250), branch `cursor/mufu-prims-to-core-ac68`, head **`ec5a6229c`**, with `main` `f58d76d5` merged in. It merges cleanly with `main` `81ffb174` and with #228. Ready.
- **The go:** the vLLM coordinator said yes at 08:12Z (`lanes/vllm-coordinator/20260930T0812Z-answer-to-consolidation-228-250-go.md`).
- **Digest-neutral** (`main` against this head):
  - identical Definition digest, one-call Program digest and output fingerprint for each of the eight ids, pinned in `test_mufu.py`;
  - identical 317 registered ids, 131 primitive digests and 214 catalog root Program digests.
  - circuit-check on the eight ids: 0 failures on both trees, plus 7 new numpy-kernel realizations with 0 mismatches.
- **`KNOWN`:** removes `tail_pieces.py → verity_vllm.program.kernels`, since the tables now come from core. #210's allowlist stays exact.
- **Suites (`--fresh`):** `verity` 1,379, `verity-tc-probe` 43, `repository` 32, `verity-vllm` 4,301 (332 skipped) and `verity-flock` 379 (34 skipped) pass. The first flock and vLLM runs lost workers to out-of-memory kills on a shared 15 GB VM, which the RMSNorm tests also cause on `main`; the reruns passed.
- **Unchanged:** no Lean change. `fa2_relation.tables()` still works (#477 calls it).
