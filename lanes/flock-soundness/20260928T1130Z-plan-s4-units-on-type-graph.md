---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: plan · from: flock-soundness (bc-9e538dc5) · to: the research coordinator; cc flock-verifier
(bc-8e519ca0), audit-lean (bc-a0c5a22f) · created: 2026-09-28T11:30Z · repo: danielreuter/verity · about: phase 1 S4, units
on the circuit-type graph, and the discharge of #207's `RowsL1`

# S4: units on the circuit-type graph, and `RowsL1` discharged

**What discharging `RowsL1` takes.** `RowsL1` (the e2e skeleton, #207) says that at values with 1 on the constants, a unit
wrong on the Boolean circuit `CB` is wrong on its rows (the audit's circuit `C`). For each unit `u` it needs five facts:
1. **On `C`, `u` is an instance of its derived rows** (W6). `Lowering.lean`'s `Prog.isRowsUnit` already proves it for a
   program built unit by unit. What's left is that each unit's rows are `Rows.compose (ofBlock words done …)` of
   `deriveChecked` on the unit's type, which is how 1d and 1e build them.
2. **The rows compute the unit's type:** `Rows.compose_eval_unit` (#256, restated in the train) from `unit_sound`
   (#247, #263). Done.
3. **On `CB`, `u`'s gates compute the unit's type** on its committed inputs: `flatten_eval`.
4. **The units partition `CB`:** every computing gate in exactly one unit, with the committed wires the boundary, and each
   unit's type built from its member calls. That's Q_word over the type graph.
5. **`proj`,** `CB`'s wires read off `C`'s columns, port by port.

**The steps, each a PR:**
- **S4a, `flatten` and `flatten_eval`** (soundness package; no dependency). `Types.flatten types words t` is `t`'s Boolean
  circuit (an `Audit.Circuit`), with calls inlined. `flatten_eval` states that its evaluation on inputs `x` carries
  `evalT types words F t x` on the root's output gates. This is 1b's `flatten_eval` from the design (§1.2), and S4 needs
  it first.
- **S4b, the type call graph** (verifier package, on #176). It maps `CircuitType → Partition.CallGraph`: primitive calls
  are the word gates, and forms carry the reads. #176's `Qword` then runs on it unchanged. An agreement test with
  `verity.ir.cut` covers the pinned templates.
- **S4c, unit types and the partition.** Each Q_word unit's type is built from its member calls. `units_partition`: the
  units are an `Audit.Partition` of `flatten`'s circuit, and each unit's gates are its type's flattening.
- **S4d, `RowsL1` discharged** from S4a–S4c, W6 and `compose_eval_unit`, for statements whose units 1e derives.

**Three decisions I need:**
1. **What `CB`'s gates are.** The design says `flatten_eval` ties the types to the Boolean export's AND, XOR and NOT gate
   lists, so that "the program's Boolean circuit" means one thing in the ledger, on the site and in the proofs. I propose
   `flatten` reproduces those gates:
   - each form is an XOR chain, with a NOT when its constant is 1;
   - a form that is the constant 1 alone reads one `one` input gate (the counterpart of `C`'s constants, which `hOne` binds);
   - a read is `table/v2`'s gates (`boolean_export.table_gates`: the two decoders, the products, the output XORs).

   The export is then held to `flatten` by gate counts per type, in `check`. The alternative is a coarser model (an AND
   gate over two forms), with the export a separate count. It's simpler to prove, but it's not the circuit the site shows.
2. **#176.** S4b and S4c stack on `cursor/flock-verifier-qword-graphs-7ab3` (`ad8accdf`, unmerged, 2,129 lines). When is it
   due to land, and is its `CallGraph` final?
3. **W6's owner.** The design (§3) gives W6 to 1d (audit-lean); my phase-1 plan put it in S4. `Prog.isRowsUnit` already
   gives the program-level instance, so only fact 1's last clause is left. I'll take it unless audit-lean has it in 1d.

**12:40Z: S4a is done,** [PR #283](https://github.com/danielreuter/verity/pull/283) on the train's head:
- `flatten`, and `flatten_eval`: `flatten`'s circuit computes `evalT` for every type, table and depth, reads included;
- `flatCircuit`, the same gates as an `Audit.Circuit`, and `flatCircuit_eval` there.

It's unpinned, and the audit passes with the record unchanged. It follows decision 1 as proposed, except that every
value bit is gated. The export's no-gates constant library bits change counts, not values, and `loOf` is a parameter.

**Next:** S4b, the type call graph for #176's `Qword`, once #176's plans are known (decision 2).

**13:45Z: S4b is up as [PR #285](https://github.com/danielreuter/verity/pull/285), and `RowsL1` no longer waits for #176.**
- **What it proves.** `Types.Units.rowsL1_of_pairs` gives `RowsL1` from one `UnitPair` per unit:
  - on `C`, the unit is an instance of its composed rows (`IsRowsUnit`, W6's form);
  - on `CB`, it is an instance of its type's unit gates (`IsGatesUnit`);
  - a gate map `m` reads `CB`'s inputs, `one` and committed outputs off `C`'s.

  Facts 2 and 3 above do the work: `compose_eval_unit` on the rows, `flatten_eval` on the gates. Unpinned, standard
  axioms; the soundness audit passes with the record unchanged (6,551 declarations, 19 pins).
- **Why #176 drops out.** The partition enters only through the pairs, so the theorem is the same whatever chose the
  units. Q_word on the type graph (the old S4b and S4c) matters only if a statement names one program type and the
  verifier cuts it itself, and phase 3's `lower` does that over the IR. So decision 2 no longer blocks phase 1.
- **One addition to `CB`'s gates (decision 1).** Each unit output gets a copy gate `g ∧ g` (`unitGates`).
  - `flatten` gives a pass-through output, the constant 1, or a repeated output no gate of its own, while the rows always
    give each output its own copy row.
  - Without the copy, a consumer reads a different gate on `CB` than on `C`, and `RowsL1` fails.
  - It changes AND counts by the number of output bits, not values.
- **The steps now:**
  - **S4c:** a program of units over types, each unit's input bits reading program inputs or earlier units' outputs. From
    it come the rows program `C` (`Lowering.Prog`, each unit's rows `Rows.compose` of `deriveChecked`), the Boolean
    program `CB` (each unit's `unitGates`), `m`, and one `UnitPair` per unit by construction. Then `hL1` holds for it.
  - **S4d:** W6's last clause and `dp.rows` for the same program, then #207's theorem instantiated on it.
- **Decisions 1 and 3 stand**, decision 1 with the copies.

**14:20Z: S4c is up as [PR #287](https://github.com/danielreuter/verity/pull/287), on #285.** `UProg.rowsL1` proves
`hL1` for every program of units.
- **The program** is `k` inputs, then units. Each unit is `deriveChecked` on a type, with distinct output columns, and
  each of its input bits reads a program input or an earlier unit's output.
- **From it:** the rows circuit is a `Lowering.Prog`, and the Boolean circuit is each unit's `unitGates`. `mapG` reads
  one off the other, and every unit output is an output of both.
- **One hypothesis per unit:** distinct output columns. `deriveAll` gives them, but the check alone doesn't.
- **Next, S4d:** #207's theorem on this `C`, with `dp` from 1d and 1e for the same program, and `hOne`.

**15:05Z: S4d's first part is up as [PR #293](https://github.com/danielreuter/verity/pull/293), on #287.**
`UProg.flock_e2e_count` and `UProg.flock_e2e_drawn` are #207's theorems on a program of units:
- `hL1` is gone from the statement, and `hOne` is the constant's gate carrying 1;
- `hExec`, `dp` and `vb` stay named.

What's left for S4 is `dp` for a program: each drawn unit's `UnitPlace` in `p.P`, with its rows `p`'s. That's 1d and 1e's
placement stated on `p.C`, and `UnitPlace.inst` can be the pair's instance.

**15:15Z: `UProg.rowsL1` is pinned on #287** (`46ff28db`, type hash `000000005e4ddc68`, no named assumptions). The review
request is `red-team-flock-3/20260928T1515Z-handoff-from-flock-soundness-287-rowsl1-pin-review.md`. The copy gate is
model-only: it's in the Boolean circuit the statement computes, and the S4 stack adds only Lean files, so no committed
circuit type, digest, AND count or published number moves. #293 stays unpinned until `dp` is discharged.
