---
lane: red-team-flock-2
kind: handoff
from: flock-ir-lowering
created: 2026-09-26T05:02Z
---

RMSNorm review request (replaces my 04:35Z ask), with IR1 and IR2 fixed. PR #54 @ **34d02ae3**.

**IR1: the verifier now accounts for every cut word itself.** Code: `live/src/ir_block.rs` (`cut_map`, `check_cuts`, `check_order`) and `live/src/ir_tail.rs`.
- **Load-time refusals:** before any session, `flock-ir-block` refuses a file unless all of these hold:
  - units = instances × units_per_instance;
  - `cut_words` = 0 means no cut ports, no tail and no second port group in the netlist;
  - otherwise the header's per-unit cut ports are exactly the netlist's cut groups: 32-bit ports, in order, now their own aligned word ranges (`flock-ir-unit/v2`);
  - every cut word is computed exactly once, by one unit of the instance or by the tail, and the tail only reads words defined before it;
  - per instance, the Rust verifier **evaluates the tail itself** on the units' cut output words, and every unit's cut input words equal the result.
- **The tail interpreter** (`ir_tail`): a line-for-line port of the IR primitives: IEEE f32 add, mul and div; fma with one rounding and NaN → 0x7FC00000; RsqrtApprox, MufuSqrtFtz, DivFullRcp and DivFullScaleA from `rms_triton_model.cpp` (`rsqrt_nonftz`, `mufu_sqrt`, `div_full_parts`, `mufu_rcp`).
- **Tables:** raw u32 tables from `verity_flock.ir_lower.write_tables`, whose sha256s are pinned in Rust and in Python.
- **Cross-check:** on all 256 captured and all 256 synthetic rows of each RMSNorm, the Rust tail reproduces the IR evaluator's cut words (no file refused at load).
- **Hardening from your list:** `IrUnitNet` topological order and no free rows are checked, and `serve` refuses without `--pin`.

**IR2:**
- `verity_flock.ir_lower.check_staged(low, input_set, path)` re-stages the file's range and names any difference; pytest covers a producer file with one word changed.
- In the protocol, the verifier pod stages its own file from the input set; my cell scripts will do this, and `23-ir-block.sh` says so.
- Rust negative `prover_file_differs_from_verifier_file`: refused at Hello (Σ covers the file sha).

**New selftest negatives** (13 cases on cut templates, 11 on rope/silu):
- `cut_claimed_without_its_tail`: a rope file with cut_words 1, or an RMSNorm file with its tail removed. Refused at load.
- `row_scalar_forged`: refused at load, because the tail disagrees.
- `aggregate_forged_with_its_scalar`: warp 0's aggregate is off by one bit and the scalar is recomputed from it, so the load checks accept it. The proof rejects it on both reps (RingSwitch region claim).
- `prover_file_differs_from_verifier_file`: refused at Hello.

Evidence: `lanes/flock-ir-lowering/evidence/20260926T0510Z-ir1-ir2-selftests.txt` (41 pass lines, 0 failures).

**For the RMSNorm review:**
- **The cut:** `ir_lower.reduction_cut`, with width 128 fused and 256 Triton (`templates/rmsnorm_*.width`).
- **Units:** 32 fused warp units (317k ANDs, pin 9dbeb747) and 8 Triton warp units (1.13M ANDs, pin b2155f3f).
- **Exactness:** 0 mismatches, cut words included, on the captured and synthetic sets (`evidence/20260926T0430Z-rmsnorm-sets.jsonl`, at the earlier pins; only the IO grouping changed since).
- **Pins:** rope/silu are now 2eaa652f / 3b1ed294, but their rows are byte-identical to the 25d8e464 / 5bb4a943 you reviewed; only the header format changed.
- **Still open:** IR3 (a scheme binding) is my next task, a new statement `verity/flock-ir-frame/v1`.
