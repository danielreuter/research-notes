---
lane: vllm-rf-normtap
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T22:45Z
---
# NEW TASK, once the root approves the estimate: the guarded-max tap in FA2 and FA3 (opt-in). Budget $12

PR #90 is approved (the verdict is with the research coordinator). The next tap is yours, because it's the same pattern.
**Create no pod until a coordinator handoff says the estimate is approved.** Code and CPU tests can start now.

- **What:** `GuardNegInfZero(m)` (f32, `m_use`), one value per (head, KV block after the first, query row), from the FA2 kernel
  (`flash_fwd_kernel`, the softcap instantiation included, which Gemma #57 uses) and the FA3 mainloop (H100). Spec: `docs/fine-query-plan.md`,
  "The tap list", and §3.
- **Where it goes:** the stream's **ROW entry fourth word**, which no build writes today (`commit/hidden_stream.StreamLayout`: 0 row_max, 1
  rescale, 2 step, 3 unused). The layout and buffer don't grow.
- **Opt-in is mandatory.** ROW[3] is part of today's committed FA stream bytes. With the flag off (the default), the stream must stay
  byte-identical, with word 3 as today. Otherwise every recorded run root moves. So use a separate tap version/build (or a template flag),
  selected by one config flag like `NORM_TAP`, and version the stream layout's field 3 meaning under that flag.
- **Exactness property** (extend `properties/fa_tap_exactness.py`):
  - outputs bit-identical to the installed/current tap;
  - ROW[3] equals the IR's `GuardNegInfZero(m)` bit for bit, for every (head, block ≥ 1, row);
  - fields 0–2 unchanged;
  - edge cases: −inf rows, masked blocks, softcap.
  - FA2 on L40S (sm_89), FA3 on an H100 (any H100 is fine for kernel-level exactness).
- **Rows:** #101 on L40S, tap off (= record: Program, manifest, run root) and on (a new run root, and the ROW[3] word count =
  the tap list's 97,280). FA3 kernel-level only (no H100 row).
- **Partition checker:** attention Definitions with ROW[3] acquired: strict partition, committed boundaries, width, **0 recomputed gates**.
  Include the output in the handoff.
- **Estimate for you:** L40S about 3.5 h (build, exactness incl. softcap, #101 off/on), about $4; H100 about 2 h for the FA3 build and
  exactness, about $5–7; gate (b) on a small CPU pod, about $1. **Cap $12.**
