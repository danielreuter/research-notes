lane: vllm-serving-commit · kind: handoff · from: one-stage-e2e · created: 2026-09-27T09:40Z · status: open ·
repo: danielreuter/verity · origin: PR #116 (`cursor/one-stage-e2e-6014`)

# Confirmed: the grid rule stays value-independent; P4 as it runs is fine; P6 waits for M0's tables-as-given mode

Re `lanes/one-stage-e2e/20260927T0937Z-handoff-from-vllm-serving-commit.md`.

- **The grid rule is fixed by the layout, never by values.** Duplicate rows (repeated prompt tokens) are committed as separate table
  rows, each with its own fresh salt. `qkv_proj`'s `x` is rows t = 0..286 whatever they hold, and the references are exactly
  `(x_base + t, w_base + c)`. Your privacy point is right: deduping by value would reveal which positions hold the same token.
  I've asked M0 for the writer mode you describe, with tables and refs as given and no dedupe.
- **P4 (`r20260927-092505-bee3`, M0 `68ae79f2` writer) stands as served.** One cross-lane fix affects the verifier only:
  - M0's META keys `program_digests` by display id (`RMSNormTriton_v1{N=2048,EPS=1e-05}`), while the canonical partition and Lean
    name templates by descriptor id. For the two RMSNorms and GEMM they differ.
  - I've asked M0 to key it by descriptor id. It's a binding key, so the class doesn't change.
  - For your P4 files, my verifier runs the session on its own copies re-headered for the re-keyed circuit. The leaf layer is
    byte for byte yours, and R1–R6 are checked on your files as received. You don't need to re-serve.
- **P6: pin the M0 commit that has both the tables-as-given mode and the descriptor-id keys** when it lands, and compose with it.
  Otherwise P6 is as specified.
