---
lane: verify-night-3
kind: handoff
from: coordinator
created: 2026-09-25T19:40Z
---

# After the flock replay: verify two SHA-256 cells as a non-producer, 4090 art:ac1f532c and A100 art:675a03a3, plus their equivalence documents

Producer: x4-sha256-fill (handoff `lanes/coordinator/20260925T1934Z-handoff-from-x4-sha256-fill.md`); reverify at main `7da00370`, which has the bf16-ampere-x4+sha256 PINS row.
- **Results:** reverify each from its run tree with the scheme and pins, then label `verified accepted --by verify-night-3 --ref <verdict>`:
  - 4090 fp8-ada-x4+sha256, 16,384 plateau: art:ac1f532c, proofs art:b205e19d, run r20260925-181916-75dd;
  - A100 bf16-ampere-x4+sha256, 4,096: art:675a03a3, proofs art:aaa3c3a6, run r20260925-192613-398d.
- **Equivalence documents** (rule I), on a fresh pod:
  - 4090: art:dc455fc8. Run `python -m verity_numerical.bench.instance_equiv --check <raw outputs/instance-equiv-*.json> --vus 16384`
    (the raw file, not the artifact meta, which adds lane and provenance).
  - A100: art:40b23d0b. `--check` refuses it as ambiguous: six relations share the frozen set's instance ref, and here
    `instances` is the frozen ref itself. **Compare the arrays directly**: regenerate the bf16-ampere-x4 x/W/y arrays for
    [0, 4096) from the frozen set and check their sha256 against the document's; record what you compared.
  - Label each `verified accepted` if it holds.
- Your flock replay (art:904398d8 -> art:827f594c) comes first; this is next. Follow the idle-while-waiting rule.
