---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: draft · status: scoped, building · repo: danielreuter/verity · re: removing L1 for RoPE
(the goal of Sep 27, 17:08Z)

# RoPE's verified lowering: scope

**The goal.** Remove L1, that each template's rows compute its gates, for `rope-head/neox-bf16/pair`. Lean re-derives the
unit's rows from its gate circuit, the IR's Boolean export, and proves that the derived rows compute the circuit's
function. A checked equality, not `native_decide`, then shows that the pinned rows equal the derived rows.

## The deciding measurement: the export reproduces the pinned rows exactly

- **The pinned rows** come from `ir_lower.layout` applied to `U.circuit()`, the unit's `gf2` circuit. That circuit
  commits only ANDs of linear forms. The layout is `flock-ir-unit/v2`:
  - the input port groups, as self rows, aligned to a power of two of 128-bit words and padded with forced-zero rows;
  - the live ANDs, in creation order, as `(form a)·(form b)`;
  - one row per assertion;
  - the output groups, as copy rows `form·1`, aligned the same way;
  - the constant last.
  Each row's columns are reduced by parity, then sorted.
- **The Boolean export** (`boolean_export.gate_list`, traced from the same `U.circuit()`) lists the unit's AND, XOR and NOT
  gates in creation order. The XOR and NOT gates are the traced linear operations.
- **Re-linearizing it reproduces the pinned rows** (`/tmp/rope-exp/relin.py`). The re-linearization takes XOR as the
  symmetric difference and NOT as a flip of the constant; each AND gets a new column. Laid out by v2, the result equals the
  pinned layout row for row.
  - The export has 17,503 gates (5,996 AND, 9,774 XOR, 1,733 NOT), 64 inputs and 32 outputs.
  - The layout has 6,273 rows, with the constant at column 6272, and 58,826 and 99,145 nonzeros in A and B.
  - The netlist's SHA-256 is the pin, `933c4ef8…`.
  - There are no assertions and no hints. The circuit's 38 dead ANDs are the ones both sides drop.
- **Getting the whole unit's list.** The export's CLI writes only the unit's pieces for units larger than `GATE_LIMIT`.
  `Registry.analyse(…, list_root=True)`, which the tensor-core units already use, writes the whole unit's list.

## Gadgets, per gate kind

| Gate | Rows | Linear form |
|---|---|---|
| input bit `k` | a self row (v2); an input column (the audit's `Rows`) | `{k}` |
| `AND x y` | one computed row, `A = form x`, `B = form y` | `{its column}` |
| `XOR x y` | none | `form x ⊕ form y` (symmetric difference) |
| `NOT x` | none | `form x` with the constant flipped |
| constants 0, 1 | none | `∅` and `{one}` |
| output bit | a copy row `A = form`, `B = {one}` | |
| padding, alignment | a forced-zero row, `A = B = ∅` | |

So the lowering has one gadget with a row (AND) and three linear ones. The whole correctness proof is one invariant: after
each gate, `xorSum (form w) z` is the gate's value `w`.

## Proof strategy

1. **Generic** (`FlockSoundness/GateRows.lean`). A gate circuit (inputs; AND, XOR and NOT of earlier wires or
   constants; outputs), its evaluation, and `ofGates`: the v2 rows, then the audit's `Rows` (the input padding columns
   dropped, as the pinned file is read today).
   - **The theorem:** for every well-formed circuit and every `z` that satisfies the rows with the constant 1, the output
     columns are the circuit's outputs on the input columns. Its proof is the invariant above, by induction on the gates.
   - **Uniqueness:** the rows are topologically ordered, so the satisfying `z` is the gate values.
2. **The check** (`FlockSoundness/Rope/*`). A kernel equality `pinned = derived`, by `decide +kernel`, computed on
   bitmask `Nat`s.
   - XOR of forms is then `Nat.xor`, and a row comparison is `Nat.beq`, both native in the kernel. 20,000 xors of
     6,209-bit masks check in about 4 s.
   - The pinned rows' sparse lists become masks by `2^c` sums.
   - A lemma relates the mask computation to the list one: `Nat.testBit` of an xor.
3. **The data** is generated Lean, with a byte-for-byte test:
   - `Rope/Gates.lean`: the export's 17,503 gates, one packed `Nat` per gate;
   - `Rope/Pinned.lean`: the pinned 6,273 rows, one packed `Nat` per row;
   - a pytest that regenerates both, from `boolean_export` and from the pinned lowering, compares them with the Lean
     files, and checks the netlist's SHA-256 against `rope_head.PINS`.
   The test is the one link from Lean to the pinned file, since a file's bytes cannot enter the kernel otherwise. The
   first cut, 1.15 MB of nested lists, elaborates in about 55 s. Packing each row into one `Nat` should cut that.
4. **The audit's L1 for RoPE.** The pinned unit's `Rows` compute the export's function, so `Partition.Correct` against
   `Prog.circuit` (the rows) is correctness against the Boolean circuit's gates, for RoPE units.

## What stays named for RoPE

**That the Boolean export computes the IR's bf16 RoPE pair.** Both the export and the rows come from the same traced `fp`
and `gf2` functions. Their agreement with the IR's primitives is tested today, not proved:
- `test_rope_unit_matches_its_primitives`, on 8,000 inputs;
- the piece tests.

That is the IR-to-Boolean compilation. The plan of record puts it with V[B], which Lean generates with an equivalence
proof. It is a separate item from L1, and `assumptions/l1-template-rows.md` will say so.

## W6, beside it

W6 connects #171's `_placed` forms to the executable. It builds `Prog` by `snoc`ing `Rows.stack (Rows.ofNet h) upv` per
instance (audit-lean, 11:55Z), so `Prog.isRowsUnit` gives `UnitPlace`'s `inst`. It needs #154 (`ExecRows.lean`) and #147
(`parse_rowOrder`), neither on `main` yet. Once they land, a lemma `Rows.ofNet (parse pinned) = ropeRows` joins the two.

## Sizes and risks

- **Sizes:**
  - the audit's `Rows`: `nIn = 64`, `nComp = 6,144` (5,996 ANDs, 20 alignment zeros, 32 copies and 96 zeros), `w = 6,209`;
  - kernel work: about 17.5k xors, 158k `2^c`, 12.5k comparisons.
- **Risks:**
  - the data's elaboration time;
  - kernel memory for the whole check, which is small in the benchmark.
  - If the export changes, the test fails and the data is regenerated. If the pinned rows change, the pin changes too.
- **Base.** It sits on #180 (docs split), after train J.
