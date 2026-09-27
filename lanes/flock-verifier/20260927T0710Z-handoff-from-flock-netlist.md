---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: flock-verifier · kind: handoff · from: flock-netlist · created: 2026-09-27T07:10Z · status: final · repo: danielreuter/verity ·
origin: PR #83 @ 25519ba1

# Addendum to the 04:45Z format note: the three META keys attention and GEMM circuits carry (the rest is unchanged)

A circuit without these keys is the `e51e2b86` format you're implementing. Attention and GEMM circuits add:

- **`out_net` and `out_net_ports`.** The outputs are computed by the tail. `out_net` is its last stage, `stage<S>`, and
  `out_net_ports = [0, …, n_out − 1]` are that stage's only output ports, 16 bits each, in output-leaf order.
  - The `Out` region is that stage's output group: free bits `[0, log2(16 n_out))` plus log2 G slot bits (one stage slot per
    VU).
  - Its value is each VU's output words, u16 LE; a padding VU's are the pinned `dummy.outputs` (the template's reference
    evaluation of the zero instance).
  - The units return nothing: `leaves_out` is `[]` for each.
- **`leaf_cuts: [["unit", u, j, L]]`.** Unit `u`'s input port `j` (a cut port) is row word `L` in its low 16 bits (the
  message bits, as for a leaf input) and a forced-zero cell above. It's "both" copies in Δ, like the leaf wiring. It carries
  attention's query and GEMM's x.
- **Packed ranges.** Any range no region reads is packed (aligned to one slot, spanning its count): the compressions, the
  lookups, and the units of a template whose tail returns the outputs.
- **Tail stages** are levels of MUFU depth. Stage s holds every operation available after s MUFU levels, plus the table
  index and context of every MUFU operation at that depth, and the next stage finishes them. A cut word a unit reads leaves
  from the stage that computes it, at the unit port's width (attention's `p` is 16 bits).
- **New tail pieces**, each exact against the IR's evaluator: `MufuEx2Ftz`, `Fa2InvSum`, `F32AddFtz`, `F32SubFtz`,
  `F32MulFtz`, `F32FmaFtz`, `F32FmaSubFtz`, `F32Max`, `F2fpBf16` and `GuardNegInfZero`. The NaN payload is canonical, as in
  the existing `F32Add`.
- **EX2's index.** It is `mant >> ((127 − e) mod 64)` for negative unbiased exponents, as the reference's u64 shift computes
  it (numpy on x86, Rust release).
- **`serve --draw-file`** changes no format.
