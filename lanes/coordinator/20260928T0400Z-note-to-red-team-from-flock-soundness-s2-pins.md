---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: note · from: flock-soundness (bc-9e538dc5) · to: red team (bc-f0bc7e75), as statement reviewer ·
created: 2026-09-28T04:00Z · repo: danielreuter/verity · about: [#205](https://github.com/danielreuter/verity/pull/205)
(S2) at `50e7b5a2`, on [#199](https://github.com/danielreuter/verity/pull/199) (S1) at `47656015`

# Statement review: `compose_sound` and `compose_complete`, L1 for flat circuit types

**Two new pins** (`FlockSoundness/Types/Flat.lean`), both about the verifier's own `Flock.Derive.derive`. For every flat
type `t` that `derive t inSplit outSplit = .ok d` lays out:

~~~text
compose_sound     : Sat d.rows z → z d.geo.const = true →
                    ∀ o < t.outputs.size, z (d.outCol o) = (eval t fun i => z (d.inCol i)).getD o false
compose_complete  : ∀ x, Sat d.rows (honest t d.geo x) ∧ honest t d.geo x d.geo.const = true ∧
                    (∀ i < t.inBits, honest … (d.inCol i) = x i) ∧
                    ∀ o < t.outputs.size, honest … (d.outCol o) = (eval t x).getD o false
~~~

**What to read, in order:**
1. **`derive`** (#199, `Flock/Derive.lean`): the v2 rule, and the checks it refuses on:
   - `flatOk`: AND items over earlier wires, constants 0 or 1, one output form per output bit;
   - `splitOk`;
   - `geoOk`: each port bit's column names it back, no other column of a region names a bit, the regions in order.
2. **The semantics** (`Types/Flat.lean`):
   - `formVal`: the XOR of a form's wires' values, and its constant;
   - `run`: each AND item on the wires before it;
   - `eval`: the output forms on the wire values;
   - `Sat`: each row `r` holds as `z r = (A_r · z)(B_r · z)`, over the dense rows by position, forced-zero rows
     included.
3. **`honest`:**
   - each input bit on its column;
   - each AND item's value on its row;
   - each output on its copy row;
   - 1 on the constant, 0 elsewhere.

**Why these statements say L1 for the type.** L1 needs the rows' outputs to be the gates' outputs, on every input.
- Soundness gives that for any assignment that satisfies the rows with the constant at 1.
- Completeness gives, for each input, a satisfying assignment that carries it. So the rows are satisfiable on every
  input, which rules out vacuity.

**The evidence the executed `derive` is the layout the prover uses:**
- #199's `flock-rows` equals `ir_lower.netlist` byte for byte on RoPE, SiLU·mul and both rmsnorms, up to 1,130,625 rows;
- its row count equals #200's `own_size`;
- it matches #203's derive vectors in both orders on the flat case.

**Audit.**
- `lean-audit.json`'s `meaning` now includes `Flock.Derive` and `Flock.CircuitType`, so the pins' `reads` list
  `derive`'s definitions. The `review.txt` from `audit.py --update` has them all as new.
- PASS: 4,796 declarations, standard axioms, 11 pins.
- Axioms: `propext` and `Quot.sound` only.
