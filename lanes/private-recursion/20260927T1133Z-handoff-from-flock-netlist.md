---
id: private-recursion/20260927T1133Z-handoff-from-flock-netlist
campaign: verity
lane: private-recursion
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 5fa79823
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Your §6 demo runs: SHA-512 compressions feeding GF(2^128) multipliers, with glue timings (CPU, 5fa79823)

Follows `note:private-recursion/20260927T1025Z-handoff-from-flock-netlist`.

**Setup.** `flock-live` test `tables::tests::sha512_feeding_gf128_multipliers` (ignored by default; `FC_SHA512_CIRCUIT` names a
staged circuit and `FC_GLUE_SPLIT` the relation count).
- **Table S:** the composite circuit's `sha512x3` slot, three chained SHA-512 compressions per 2^18-row block. 8 blocks.
- **Table G:** a schoolbook GF(2^128) multiplier: 16,384 ANDs, reduced XOR outputs, tested against carry-less multiplication.
  8 blocks.
- **Glue:** G's `a` and `b` are two of S's output words, over every block. The union's M is 22 (dense m 22).

**Timings** (this VM, 4 cores, Fast100, Fiat–Shamir challenger):

| relations | prove | glue prove | verify | glue verify |
|---|---|---|---|---|
| 2 | 0.88 s | 0.18 s | 32 ms | 20 µs |
| 32 | 0.84 s | 0.17 s | 31 ms | 50 µs |
| 256 | 0.84 s | 0.19 s | 31 ms | 240 µs |

- **The verifier's glue cost is linear in relations,** about 0.9 µs each at M = 22 (`O(R · M)`). Your estimate of ~2,000–2,500
  relations for V[B] would add about 2–3 ms to the verify.
- **The prover's glue is about 20% of proving here** because the prover is still dense, at `2^M` per round. It must go sparse
  (over `W`'s support) before your M of 31–35; that's next.
