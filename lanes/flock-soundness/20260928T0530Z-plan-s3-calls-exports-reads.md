---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: plan · from: flock-soundness (bc-9e538dc5) · created: 2026-09-28T05:30Z ·
repo: danielreuter/verity · about: S3 of phase 1, cut into three PRs, against #203's vectors

# S3: `derive` for calls, exports and reads, in three PRs

**The reference is #203's mirror (`verity_flock.derive`) and its 21 vectors (`backends/flock/tests/derive_vectors.json`).**
`flock-rows --archive FILE` will print the same three texts the vectors hash: each layout's physical rows, the unit's Δ,
and the logical list. So each case is compared by SHA-512.

| PR | Branch | What | Vectors it must match |
|---|---|---|---|
| S3a | `cursor/flock-compose-dag-8569`, on #205 | Wires map to forms (sorted column sets, XOR as symmetric difference); see below | "4-bit adder, calls in block slots", "4-bit adder, calls inlined", "wrapper …, nested placement", "wrapper …, both levels inlined", and the random cases without reads |
| S3b | on S3a | Reads, inline and placed, by `table/v2` (the table words from the archive) | "a read inline", "a read placed in a block slot", "a read placed inside a placed callee", "fan-out 20 calls, 20 reads", and the remaining random cases |
| S3c | on S3b | The proofs over the type DAG, restating S2's two pins; see below | none (the pins go to the red team) |

**S3a in detail:**
- **Placed calls:** a callee's layout at `q · 2^s` inside an inner layout. Its non-exported inputs get binding copies
  `form · [callee constant]`, and its constant row is `[c] · [c]` of the caller's.
- **Exports**, by the exclusive-use rule, with the caller's input groups compacted.
- **Inline calls:** expanded by the callee's layout, which places nothing.
- **The unit level:** placed entries in block ranges after the own region, aligned, in item order. The unit's parts and
  Δ come out as `PART` and `DELTA` lines, with the constant bound to `one`.

**S3c in detail:**
- The rule lemmas: own rows (S2), a placed call (binding copies and the callee's rows), an inline call (expansion), an
  exported input, a read (the truth-table lemma, via `build_computes` for v2).
- `compose_sound` and `compose_complete` by induction over the layouts, callees first.
- S2's two pins, restated for the type DAG; the flat case becomes the corollary.

**Order and discharge.** S3a, S3b and S3c go in that order; S4 (Q_word units on the type graph, W6, `flatten_eval`)
follows S3c. Together S3 and S4 discharge the end-to-end skeleton's `RowsL1`.
