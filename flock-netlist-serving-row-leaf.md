---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# flock-netlist: the serving row leaf on frame-v3-sha512 + hm96, status and next steps (2026-09-27 04:10Z)

Lane flock-netlist, PR #83 branch `cursor/flock-netlist-m0-4d6a`. The commits are local until the VM's GitHub token is
refreshed; push fails with "Authentication failed".

## Done (CPU-verified)

- **The statement's rows.** They are `frame-v3-sha512` leaves under `hm96-sha512/row/v1`, and both hashes run in the circuit:
  - **The inner digest.** `x = SHA-512(sha512_row_prefix || row)` runs in `sha512x3` slots: three compressions per 2^18 slot,
    in a packed range, chained by the row's wires from the prefix's midstate.
  - **The commit string.** One `hm96` slot per port computes the padding compression, then `b = x XOR M(key) y` and
    `c = SHA-512(salt_prefix || y)` from the row's private 192-byte salt.
  - **The public data.** `b || c` is the Digest region. The frame leaf is `hm96.SHA512.tree_leaf(key, b || c)`.
  - **The constants.** The midstate and the padding block are Δ constants (the pin, or a forced-zero cell).
  - **What Rust recomputes.** Every row constant and the rows' wires. It refuses a META that differs.
- **The statement's other bindings.**
  - The subcircuit's program digests.
  - A provisional partition digest (`flock-circuit/unit-cover/v0`, this lowering's unit cover), until the partition checker
    defines one.
  - Each block's unit indices, checked against the range at load.
- **Sizes.**
  - One compression is 57,947 ANDs plus the committed schedule words, round state and every fifth carry.
  - `sha512x3` is 256,001 rows and 3.79M nonzeros; `hm96` is 246,785 rows.
  - SiLU (16 KB rows, 258 compressions per VU) should fit a 2^26 block; it has not been staged yet.
- **Staging.**
  - One salt draw writes both the prover's and the verifier's files.
  - The bench's pods share a public staging key over the set's content digest (`stage_salts` in the result).
- **CPU selftests.**
  - rope, 4 instances: 29 of 29 pass.
  - rmsnorm-fused n2048, 2 instances: every case passes except two that build a second statement. Those exceed this VM's
    15 GB and run on the pod.
- **red-team-hm96 C1 and follow-ups.** Done at `e2190ca3`; see
  `lanes/coordinator/20260927T0355Z-handoff-from-flock-netlist.md`.

## Statement-format revision (at `eb90718f`)

- **SHA-512 for every identity and binding digest.** This covers the circuit pin, the public digest, the statement digest,
  Σ, and the record's root_F, root_B, publics, link, round, proof and stream-root digests. The session parameter
  `digests: sha512` is named in `Hello`; other statements are unchanged.
- **The unit draw is live.** `Register` and `Draw` come before `Hello`, with the exact samplers on OS bytes. The drawn
  statement is derived from the registered population file. The record keeps the draw; U1 and U2 are checked in
  `from_record`, U3 in `check_public`.
- **The partition field** has its final shape: a 64-byte SHA-512 digest, plus global unit indices per §2 of
  `lanes/flock-verifier/20260927T0445Z-draft-partition-checks-spec.md`.
- **Published** to the verifier lane: `lanes/flock-verifier/20260927T0445Z-handoff-from-flock-netlist-format.md`.
- **Push.** A bundle of `b32e1a7b..eb90718f` is at `artifacts/pr83-eb90718f.bundle`; the request is in `lanes/coordinator/`.
- **GPU selftests.**
  - rmsnorm-fused at `4b33558e`: 32 of 32 pass. This includes the device witness of the compression slots, C1 on the
    device and `device_salts_match_host`.
  - All four sets at `eb90718f`: `r20260927-044007-4a7b`, running.

## After `eb90718f`

- **The e2e bindings (`e51e2b86`), for the one-stage audit.**
  - A caller's `verity/partition/v1` digest, `program_sha512`, and caller-supplied global unit indices.
  - `units.classes`: SHA-512 of the circuit without META's bindings.
  - Handoff: `lanes/one-stage-e2e/20260927T0545Z-handoff-from-flock-netlist.md`.
- **The serving row-leaf spec and test vector for vLLM** are on the notes remote at
  `lanes/vllm-serving-commit/20260927T0600Z-handoff-from-flock-netlist.md` (vector and check script under
  `campaigns/boolean-escape-hatch/assets/flock-netlist/`), with a copy in the store.
- **GPU selftests at `eb90718f`:** RMSNorm fused 34 of 34, RMSNorm Triton 34 of 34, RoPE 30 of 30, SiLU 31 of 31.
- **Cells at the new format** (L40S prover, verifier in the same datacenter, EU-SE-1).
  - RoPE: `art:62b66c41`, 216 M unit-AND/s. The row leaf costs more than RoPE's units. 1.6 s of the 3.6 s is host witness,
    mostly hm96 slots evaluated on the host, the next device optimization.
  - SiLU, RMSNorm fused and RMSNorm Triton: running in a chain.
- **The first RoPE attempt was discarded.** Its verifier pod was in another datacenter, so each coin round waited 105 ms.
- **The second attempt was refused.** The prover's own thread pool throttled the cgroup, and the guard read contention.
  `61-circuit-cell.sh` now uses one core under the quota's floor.

### Cells registered at the new format (L40S, same-datacenter verifier)

| template | art | unit-AND/s | VUs | end to end |
|---|---|---|---|---|
| RoPE | `art:62b66c41` | 216 M | 4,096 | 3.64 s |
| SiLU | `art:47b1b9b0` | 1.39 G | 64 | 1.02 s |
| RMSNorm fused | `art:e07c9cea` | 1.59 G | 256 | 1.63 s |
| RMSNorm Triton | running | | | |

## Overnight plan (06:00–15:00Z, cap $150)

The coordinator's order:
1. Keep the e2e bindings stable, and tell bc-c520c11b about any change.
2. The serving spec for vllm-serving-commit: done at 06:00Z.
3. Attention with the softmax in the circuit, with L40S cells under IX2 (median of three, per
   `lanes/bench-spine/20260927T0545Z-handoff-from-coordinator.md`).
4. Multi-table, if time allows.
5. A summary for the morning report by 14:30Z.

### Attention in the circuit: the design

- **Tail.** `tail.lower_tail` must output each cut word a unit reads from the stage that computes it, not only from the
  last stage: `p` and the rescaled accumulator feed the PV steps. It must also output `tail_rets`, the head's outputs, from
  the stages.
- **Outputs.** META gains the output source: a stage's output ports instead of the unit's `out_groups[0]`. The Rust `Out`
  region and `leaves_out` must follow it. The padding instance's outputs come from the all-zero instance through the tail.
- **Query.** It becomes a committed row like k and v. Today's frame statement takes it as a public port.
- **Witness.** FA2 interleaves units and tail per key block, so the device's two-pass witness can't follow it. Attention
  starts on the host witness (`converge`), which is correct but slower; device passes per round come later.
- **Scope.** One T class. The pin is per T, or per class through `class_manifest` in `templates/attention_head.py`.

What the captured T = 129 slice (`attention-head-fa2-d64-bn128`) shows:
- **Units.** 1,092 per head: 4 × 129 QK steps and 64 × 9 PV steps. The unit is 9,857 rows (a 2^14 slot).
- **Cut words.** 1,543. Cut words 0–63 are the public query: q's 64 words, which must copy the q row's message bits in the
  low 16 bits and be zero above. That needs a leaf-to-cut wiring (META `leaf_cuts`), with Rust wiring it like the leaf
  inputs.
- **Tail.** 1,046 operations, none of them in `tail.MUFU` or `tail.OPS` yet: `MufuEx2Ftz_v1` × 130 (the ex2 table),
  `F32Max_v1` × 128, `F32FmaSubFtz_v1` × 129, `F32MulFtz_v1` × 131, `F32AddFtz_v1` × 127, `F32FmaFtz_v1` × 4, and
  `F2fpBf16_v1` × 193. Each needs a gf2 piece exact against `verity_vllm.program.registry.prims.<P>.evaluate`.
- **Staging.** With 130 EX2 lookups, one stage per MUFU operation is not viable (130 slot types). Stages must be levels of
  MUFU depth, each holding every lookup at its depth: about three stages, and about 130 ex2 lookup slots per VU, each about
  2^16 bits.
- **Block budget.** About 51M bits per VU, which fits 2^26 with one VU per block: units 17.9M, lookups about 8.6M, 259
  compressions 22.8M, hm96 1M.

### Attention and GEMM in the statement (07:20Z)

- **Attention: the softmax in the circuit** (`9c03bcfb`…`adfae8c0`).
  - **Tail pieces.** Every piece is exact against the IR: EX2 through the ex2 table, `Fa2InvSum` through rcp, the FTZ family,
    `F32Max`, `F2fpBf16` and `GuardNegInfZero`.
  - **Staging.** Stages are levels of MUFU depth: three for attention, plus an output stage whose only ports are the outputs
    (the Out region). Cut words leave at the reading unit's width.
  - **Wiring.** Leaf cuts carry the query words. Ranges no region reads are packed.
  - **Witness.** Convergence is slot by slot. The host builds the witness: the units and the tail interleave round by
    round.
  - **Result.** The T = 129 slice is one VU per 2^26 block, and the GPU selftest passes 33 of 34. The one failure was an
    artifact of a one-instance draw test, since fixed.
- **GEMM: the total unit, as a template** (`15260468`).
  - `gemm-coordinate` Ampere bf16 lowers through `tc_units`: each k-step is a 2^14 unit, x comes in as leaf cuts, and the
    tail is the zero accumulator and the bf16 cast.
  - The step equals core's `AmpereBF16TcDot16_v2` on 3,000 inputs.
  - Selftests: CPU at K = 1024 passes all 32 applicable cases; the GPU selftest passes 31, with only the same draw-test
    artifact failing.
- **`serve --draw-file`** (`3183eaaf`): the verifier's own draw, served at `Register`.
- **The `write()` fix** from vllm-serving-commit: one concatenation instead of one per instance, the same bytes (`25519ba1`).
- **Handoffs to the lanes:**
  - `lanes/one-stage-e2e/20260927T0710Z-handoff-from-flock-netlist.md`;
  - `lanes/flock-verifier/20260927T0710Z-handoff-from-flock-netlist.md`.
- **Cells running (chain, IX2):**
  - RMSNorm Triton at the new tail staging;
  - GEMM on `art:123dc234` (K = 2048), at 256 and 1,024 coordinates;
  - attention at T = 129 on `art:9551ba66`: 16 heads, a subset of #101's c2 set `art:82c591d1`.

## Next

1. **Device witness for the row slots.** Today GPU proofs upload the host witness, which is correct but slow.
   - Evaluate `sha512x3` with a second `fc_unit_witness` pass: its own CSR, level schedule and per-slot inputs from
     `Stmt::row_inputs`, in place of the removed BLAKE3 section of `fc_witness`.
   - Upload the `hm96` slots as host slots on both the cut and non-cut paths.
2. **Pod run** (L40S). A GPU selftest covers C1's device refusal and `device_salts_match_host`. Then re-run and register the 4
   cells (RoPE, SiLU, RMSNorm fused, RMSNorm Triton) at this statement.
3. **Attention in the circuit**, one T class (FlashAttention-2 softmax and rescaling).
4. **Multi-table statement with private glue** (private-recursion's spec; relation counts in
   `note:20260927T0310Z-handoff-from-private-recursion`).

Spend so far is about $15 of the $80 cap. No pod is up.
