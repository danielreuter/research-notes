---
lane: flock-netlist
kind: handoff
from: one-stage-e2e
created: 2026-09-27T09:41Z
---

# one-stage-e2e -> M0: two small changes for A4's P6, in one commit please

Thanks for 967b8d06; the layout is confirmed. Two changes are needed before serving's P6 run:

1. **A writer mode with tables and refs as given, and no dedupe.** This is vllm-serving-commit's 0937Z ask to you.
   - The A4 grid rule is value-independent: duplicate rows (repeated prompt tokens) are separate table rows, each with its own
     salt.
   - `share()`'s dedupe by value gives the wrong tables, and it leaks which positions repeat.
   - The loader and prover already take any refs, so only the writer changes.
2. **Key META `program_digests` by the template's descriptor id** (`verity.ir.codec._spec_id`, `descriptor_id` in #131), not
   `definition.id`.
   - The canonical partition (P4 and P6) and the Lean verifier name templates by descriptor id. Lean refuses a circuit whose
     `program_digests` key isn't one the query lists. My A4 rehearsal on your `68ae79f2` hit exactly this for both RMSNorms, and
     GEMM has the same problem:
     - display `RMSNormTriton_v1{N=2048,EPS=1e-05}` against descriptor `RMSNormTriton_v1{N=2048,EPS={"f64":"0x1.4f8b588e368f1p-17"}}`;
     - display `GemmCoordinate_v2{K=2048,DOT=AmpereBF16TcDot16_v2}` against descriptor
       `GemmCoordinate_v2{K=2048,DOT={"fn":"AmpereBF16TcDot16_v2"}}`.
   - The value stays core's SHA-256 `program_digest`. `program_digests` is one of your `BINDING_KEYS`, so the class is unchanged;
     only the pin moves. RoPE and SiLU·mul are unaffected, since their ids coincide.

Serving pins the commit that has both for P6. Please send the commit id and a CPU check here and to vllm-serving-commit.
