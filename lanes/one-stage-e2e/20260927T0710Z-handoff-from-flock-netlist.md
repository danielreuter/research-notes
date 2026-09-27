---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: one-stage-e2e · kind: handoff · from: flock-netlist · created: 2026-09-27T07:10Z · status: final · repo: danielreuter/verity ·
origin: PR #83 @ 25519ba1

# GEMM (the total unit) and attention are templates of M0's statement; `serve --draw-file`; the e51e2b86 bindings are unchanged

**Bindings.** `--partition`, `--program`, `--unit-indices` and `units.classes` are byte for byte as at `e51e2b86`. A
circuit's class changes only when its circuit does. RMSNorm's does: its tail stages were rebuilt, so read the class with
`--class-only` again.

## GEMM: `gemm-coordinate`, Ampere bf16 (`sm80.mma.m16n8k16.bf16`)

- **How it lowers.** Each tensor-core k-step is one unit, the 2^14 slot the Flock backend family proves. Unit inputs:
  - W's words are its leaves;
  - x's words are leaf cuts, row words read as cut inputs;
  - the accumulator chains through cut words.
- **The tail** is the zero accumulator and the bf16 cast, and it returns `y`.
- **Exactness.** The step equals core's `AmpereBF16TcDot16_v2` on 3,000 inputs, including NaN, infinity and saturation
  cases.
- **Staging.** `python -m verity_flock.circuit --input-set <a gemm-coordinate set> ...` lowers it automatically
  (`templates/gemm_coordinate.circuit_lowering`).
- **Checks.** CPU selftest at K = 1024, 4 instances: every applicable case passes. The tail-swap negatives are skipped:
  GEMM's tail has no constant to forge.
- **Next.** A GPU selftest and an L40S cell on `art:123dc234` (K = 2048), at 256 and 1,024 coordinates. Hopper and FP8
  steps aren't lowered.

## Attention

- **Shape.** One T per statement: the circuit depends on T. The softmax runs in the circuit, in three depth stages plus an
  output stage, with 130 EX2 lookups and one RCP.
- **GPU selftest** on the captured T = 129 head: running, and passing so far.
- **Cell.** Measured per T; a class is its Ts' statements.

## `flock-circuit serve --draw-file PATH`

- **What it does.** The server serves the verifier's own draw, the §7.3 object `{"law", "population", "k" | "p", "units"}`,
  at `Register` instead of sampling.
- **Checks.** U2 at load; the draw's population must be the staged population's N; U1–U3 hold as for a live draw.
- **Test.** Case `unit_draw_from_file` passes.

The wire, the record and the drawn statement are the same as for `--draw`.

## META keys only these templates carry

`out_net` and `out_net_ports` (the tail's output stage and its 16-bit output ports), and `leaf_cuts` (`[["unit", u, input
port, leaf]]`). A circuit without them is exactly the `e51e2b86` format.
