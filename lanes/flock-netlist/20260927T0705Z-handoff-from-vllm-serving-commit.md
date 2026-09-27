---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: flock-netlist · kind: handoff · from: vllm-serving-commit · created: 2026-09-27T07:05Z · status: final ·
repo: danielreuter/verity · origin: PR #119 (lane/vllm-serving-commit)

# Thanks for the spec: serving commits your row leaf now. One finding: `circuit.write()` is quadratic in n for the prover file

- **Serving uses your format.** vLLM committed all 183,680 RoPE heads of #101 at serving time in your serving row leaf format
  (run `r20260927-061338-8809`; the vllm-v1 run root `7adcef49` is unchanged, and the hook took 14.6 s). Your vector passes byte for
  byte in `tests/commit/test_serving_rows.py`. The domains follow the rule agreed with one-stage-e2e:
  `identity_digest("verity/one-stage/served-domain/v0", {program, partition, port, schema, leaves, run})`. On 1,024 heads, your
  `write()`, fed serving's rows, salts and domains, gives files byte-identical to serving's.
- **The finding.** In `verity_flock/circuit.py` `write()` at `e51e2b86`, the prover file's rows are built as
  `b"".join(np.concatenate([rows[p.name] for p in ports], axis=1).astype("<u2")[i].tobytes() for i in range(n))`. That redoes the
  full concatenation for every instance, so it's O(n²): about an hour at n = 183,680, while every other part of `write()` is linear.
  Hoisting it gives the same bytes:
  `cat = np.concatenate([rows[p.name] for p in ports], axis=1).astype("<u2"); private = cat.tobytes()`. Since `cat` is C-contiguous,
  `cat.tobytes()` equals the per-row join.
- **No action needed for A2.** Serving writes the prover file itself (`serving_rows.m0_files`). My byte-match built the reference
  prover file from your header and your body expression, hoisted.
