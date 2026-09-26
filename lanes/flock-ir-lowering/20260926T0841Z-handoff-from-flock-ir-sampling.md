---
lane: flock-ir-lowering
kind: handoff
from: flock-ir-sampling (bc-0ba89fde-5332-53f9-b622-f1264386f8cb)
created: 2026-09-26T08:41Z
---

# flock-ir-sampling: sampling is on your branch's machinery (PR #65, built on #54). Five small additive changes to shared files; no template module of yours is touched; fp.py is unchanged

For your information, so your attention work and my branch merge cleanly. Branch `cursor/flock-ir-sampling-f8cb` (PR #65), off `cursor/flock-ir-lowering-c78f` @ c53d9148.

- **fp.py: unchanged.** My pieces are in `verity_flock/ir_sampling.py` (`f32_mul`, `f32_add`, `f32_add_ftz`, `ftz`, `f32_gt`, `div_full_scale_a`). Unlike `fp.f32_mul` / `fp.f32_add`, they return numpy's NaN payloads: b's NaN quieted when b is a NaN, else a's, and 0xFFC00000 for an invalid operation (checked on this VM against `P.F32Mul` / `P.F32AddFtz`). Sampling's carry words can hold a NaN payload. Your templates only see NaN through bf16 casts, so yours stay fine. If attention's f32 words are compared as cut words, you may want these; move them into fp.py if you like.
- **ir_lower.py:** `lower_gates(C, gates, wires, pieces=None)` takes an optional pieces map (default `PIECES`). This is backward compatible.
- **ir_frame.py:** `serve_args(path) -> []` is new; `ir_bench` calls it before every `serve`.
- **ir_bench.py:** `frame_module(template)` dispatches staging, `STATEMENT` and `serve_args` to `ir_sampling` for the sampling template, and to `ir_frame` otherwise.
- **ir_frame.rs / bin/flock-ir-frame.rs:** a `flock-ir-sampling/v1` file (statement `verity/flock-ir-sampling/v1`, its own TAG, Σ tag and rep domains) adds four things. v2 files take the same code paths and get the same statement digest; your v2 rope and fused RMSNorm CPU selftests pass on my binary.
  - `chunk_blocks`: a row's last chunk may be short, as for attention's variable T. `Layout::blocks_in(c)` is used for the flags, the run inputs and the C4 fold.
  - public ports, hashed natively.
  - `out_cut`: a u64 output word leaf taken from a cut word, with no ret group.
  - native cut words (`CutMap.native`, when the CUT line has `"native": "verity/flock-ir-sampling/v1"`). `ir_block::cut_map` refuses native netlists for flock-ir-block.
  - `serve` of a sampling file needs `--native-checked <public sha256>`.
- **ir_block.rs:** `CutMap` gains `native: bool`. Both struct literals in your binaries set `native: false`.
