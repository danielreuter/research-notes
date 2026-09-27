---
id: coordinator/20260927T1512Z-handoff-from-flock-netlist
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 73a273d4
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Constant-table reads (MUFU ex2, rcp, rsqrt, sqrt) are plain gates in the same zerocheck and lincheck, with no table argument

For Daniel's question: it's **(1)**.

A lookup slot (`backends/flock/live/src/lookup.rs`) is an ordinary expanded gate circuit, built deterministically from the
pinned table. Its rows are:
- the index bits;
- one-hot decoders of the index's low and high halves, each minterm an AND of two half-minterms;
- one AND per (output bit, high minterm), `hi_h · (XOR of the low minterms whose table bit is set)`;
- the output bits as XORs of those products.

**The table's contents are the matrix's constant linear forms.** Nothing about the table is committed or read by a separate
argument; the circuit's pin binds it. Each read is one instance of the slot type, proved in the same zerocheck, lincheck and
opening as every other slot.

| table | entries × bits | ANDs per read | XOR terms per read | slot rows |
|---|---|---|---|---|
| ex2 | 2^23 × 31 | 41,308 | 153.8 M | 41,601 (a 2^16 slot) |
| rcp | 2^23 × 31 | 41,308 | 143.9 M | 41,601 (a 2^16 slot) |
| rsqrt | 2^24 × 31 | 49,576 | 288.9 M | 49,921 (a 2^16 slot) |
| sqrt | 2^24 × 31 | 49,576 | 309.4 M | 49,921 (a 2^16 slot) |

The ANDs are 9.6k–17.8k decoder rows plus 31,744 product rows.

**The XORs are free for the prover.** They cost the verifier one fold of each table type's matrix per rep, about 1.4–3.1 × 10^8
terms. That cost is per type, not per read.

**Gemma's tanh tables aren't in my circuit yet.** They would use the same construction, sized by their index and value bits.
