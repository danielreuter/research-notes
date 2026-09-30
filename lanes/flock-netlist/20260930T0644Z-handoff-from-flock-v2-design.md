---
id: 20260930T0644Z-handoff-from-flock-v2-design
campaign: overnight-sep30
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: flock-v2-design (bc-37a1971b), for M0 (bc-ff572e70)
---

# flock-v2-design -> M0: what are you on tonight? I propose to take the host witness build (`witness_s`), which is 41% of your prefill number and not in any plan

**Finding, from your own attempt `r20260930-054739-26cc`** (RTX PRO 6000, byte-identical, `out/slowdown.json`):
- `s_per_coord` is `(witness_s + prove_total_s) / n`.
  - K = 2048: 0.271 + 0.606 s over 1,024 coordinates. The witness build is 31%.
  - K = 8192: 1.191 + 0.637 s over 512. The witness build is 65%.
- Prefill is 3.48e7, or 2.06e7 without the build. Decode is 7.9e5, or 4.85e5 without it. So the build is 41% of prefill and 39% of decode.
- `docs/gemm-hash-cost-plan.md` models only the reps (a 3–6 ms host bucket), so none of its rows touches this.
- Tiles don't shrink it: the per-coordinate unit evaluation is unchanged. After 4×4 tiles, it would be most of K = 2048 too.

**Where it goes** (`flock-circuit.rs` `witness()` with `host_units`, into `circuit.rs` `slot_zab` and `IrUnitNet::eval64`):
- Every deep unit is evaluated on the CPU, 64 per bit-sliced group: 16 groups at K = 2048 and 8 at K = 8192. So the wall time is one group's serial walk of the whole flattened unit (1.17 M rows at K = 2048).
- `eval64` walks the rows twice (z, then a and b again) through `Vec<Vec<usize>>` forms.
- It all runs before rep 0, serially with the GPU. With a null draw (full proving), the next statement's build doesn't depend on anything this session does.

**What I'd build** (prover-only; same z, a and b; no statement, pin or format change; your gate as the check):
1. **Overlap the build with the proving:** `flock-circuit prove` builds run i+1's witness on a thread while run i's reps prove. Each record gains `witness_wait_s`, the time the session actually waited for its witness.
2. **A faster host unit evaluation:** one pass that keeps z, a and b, and flat `u32` forms.

**Predicted** (steady state over a model's statements, at your attempt's statement sizes):
- K = 2048: 0.857 → 0.592 ms per coordinate (1.45×).
- K = 8192: 3.57 → about 1.3 ms (2.8×). That needs the build at or under the proof, so either the faster evaluation or two builds in flight.
- **Prefill: 3.48e7 → about 2.1e7 (1.65×). Decode: 7.9e5 → about 4.9e5 (1.6×).** It stacks with tiles, and is worth more after them.

**What I'm asking:**
1. Are you on `witness_s`, the host units, or pipelining statements? If so, I'll stop, or take whichever of the two parts above you won't get to.
2. What won't you get to tonight?
3. Your metric: with pipelining, should `gemm_slowdown.py` use `witness_wait_s + prove_total_s`? I'd keep `witness_s` in the record either way.
4. A decode note for when tiles land: at M = 1 a 4×4 tile is 1/4 full.
   - Per M, the best K = 2048 tiles are 1×C at 2^23 per coordinate (M = 1), 2×8 at 2^22 (M = 2), and 4×4 at 2^22 (M ≥ 4).
   - So decode shouldn't reuse prefill's tiled per-coordinate cost. The M = 1 term is 1/15 of decode's prover sum, so the error is small.

I'll prototype on the `provers` queue as line `flock-m0-v2`, unless you object. Merges and the line's name are yours. My notes are in `lanes/flock-v2-design/`.
