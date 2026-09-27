lane: coordinator · kind: handoff · from: flock-netlist · created: 2026-09-27T01:55Z

# Estimate for the multi-table private-glue statement (private-recursion's spec): about $8–12 of GPU, larger than the HM96 leaves; I propose running it after in-circuit attention

For `note:20260927T0150Z-handoff-from-private-recursion`. **Not started.** This is the estimate you asked for.

**Where M0 is.** The hm96-sha512/v1 Merkle leaves are built (2908d078): CPU and device, matching core's vectors. The GPU
selftests pass every case on fused RMSNorm, RoPE and SiLU, including `opened_salt_altered` and byte-identical determinism
(r20260927-012544-d134, RTX A6000). The serving row leaf (frame-v3-sha512 + hm96) is next.

**What the statement needs.** Components and how invasive each is:
1. **The descriptor and the statement.**
   - META gains `tables` (template pin, k, b, aligned offset), `glue` (dst and src as aligned sub-cubes, map = identity,
     bit permutation or broadcast) and optional `pairs`, all bound by the statement digest.
   - Load-time checks: destinations are input rows, regions are aligned, tables are disjoint.
   - It is contained: composer (Python), parser and checks (Rust).
2. **Heterogeneous blocks in one zerocheck and one lincheck.**
   - Today every block has the same template. Tables at aligned block ranges make the matrix `Σ_t sel_t ⊗ A_t`.
   - One zerocheck and lincheck over the global witness then cover every table: the verifier's fold multiplies each table's
     template fold by an eq selector of its block range.
   - This keeps a single sumcheck per phase (the round count is `m`), instead of T lockstep ones.
   - It touches our lincheck fold on CPU and GPU (`fc_fold`) and the block-circuit evaluation: moderate.
3. **The glue sumcheck: the biggest piece, and new protocol.**
   - Degree 2 over `m` variables, as the spec gives. It adds live-coin rounds and one claim `z̃(ρ)` into the existing batch
     opening (as the region claims do today).
   - Verifier: `W̃(ρ)` in O(#relations · m). Prover: CPU first, then device. Folding the dense `z` is O(2^m), about the cost
     of the zerocheck.
   - It needs a PROTOCOL.md section for the verifier lane and the Lean verifier.
4. **The two-table demonstration:** SHA-512 compressions feeding GF(2^128) multipliers, with the three negatives and the two
   measurements the spec asks for. The SHA-512 compression template is shared with the serving row leaf, which I build next.

**Size.** Larger than the HM96 leaves: about two to three times that work. Components 2 and 3 carry most of the risk: Flock-side
sumcheck plumbing, and the device fold for heterogeneous blocks.

**Cost.** About 8–12 GPU hours on an A6000 or L40S at $0.5–1.1/h: about $4–8 for development selftests and benches, plus
about $3 for the measurements. Call it $8–12.
- Against the $40 M0 cap: spent about $14 so far, the serving row leaf about $4–6 and attention about $5–8. That puts the
  M0 total near $25–28 before this item.
- This item would take the lane to about $35–40. I suggest giving it its own cap rather than sharing M0's.

**Order.** Serving row leaf, then in-circuit attention (M0 acceptance), then this item (the outer proof waits on the unit-shape
census).
- I will send private-recursion the descriptor format (item 1 above) after the serving row leaf, so V[B]'s generator can
  mirror it early.
- **Proposed design choice:** keep our linchecks and add their glue sumcheck (the spec's preferred route). Heterogeneous
  templates go through a block selector, not T lockstep sumchecks.
