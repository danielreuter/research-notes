---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: plan · from: flock-soundness (bc-9e538dc5) · created: 2026-09-28T01:56Z · repo: danielreuter/verity ·
about: phase 1 of `docs/verified-lowering-design.md`, cut into PRs · for: the research coordinator; cc the design lane,
audit-lean (bc-a0c5a22f), flock-verifier (bc-8e519ca0), M0 (bc-ff572e70), constant rollout (bc-613ddf45)

# flock-soundness: phase 1's PRs

**Scope (Daniel's).**
- The frontend, IR to Boolean circuit, stays on the untrusted side. Phases 2 and 3 are parked.
- A statement is the Boolean circuit, as #191's circuit types, plus the partition over it.
- The verifier derives every unit's rows from the types and a placement, with the proved `derive` and
  `compose_sound`, and it stops reading rows from statements.
- My plan's items map as the design's §1.8 says: A, B, C, E and F are kept, and D is optional (not planned).

**Pins** go to the named statement reviewer red-team-flock-3. Everything runs on CPU.

## The PRs

The ones marked (mine) are this lane's. The others are listed for the order.

| # | PR | Owner | Stacks on | Contents | Pins | Size |
|---|---|---|---|---|---|---|
| S1 | **`derive` for flat types, and `flock-rows`** (mine) | flock-soundness; the verifier lane reviews the executable file | #194 | `Flock/Derive.lean`: a type's own rows by the v2 rule (input port groups as self rows, one row per AND item in item order, the output copy rows, the constant last). Calls are inlined by `expand` (#191's), so any unit that has no reads derives to what `ir_lower.layout` lays out today. Also `lake exe flock-rows`, which writes `flock-ir-unit/v2` | none | 400–700 lines of Lean |
| S2 | **`compose_sound`, flat case** (mine) | flock-soundness | S1 | `FlockSoundness/Types/`: `Ty.eval` over #194's `CircuitType`, the own-rows lemma, `compose_sound` for flat and inlined types stated over S1's `derive`, `flatten_eval` (against the Boolean export's gate lists), and `rope_sound` as a corollary. #187's chunked kernel check stays as the regression test | `compose_sound`, `flatten_eval` | 700–1,000 |
| S3 | **Placed calls, exported inputs and reads** (mine) | flock-soundness, with the verifier lane for `table/v2` | S2; the placement format (below); the verifier lane's `table/v2` build | `derive` for placed callees: shifted to aligned offsets, binding copies generated from the call item's forms, the constant copy, and reads at a placed sub-range or inline. The rule lemmas: call, rows after a call point, exported input, read (`build_computes` for v2). `compose_sound` by induction over the DAG, and `decide` examples: a call, an exported input, an 8-bit read | `compose_sound` restated for the DAG | 800–1,200 |
| S4 | **Units on the circuit-type graph** (mine) | flock-soundness, with the verifier lane (#176) | S2, #176 | Each type's call graph read off its items, so primitive calls are the word gates and forms carry the reads. Q_word v1 runs over it through #176's `Qword` functions, unchanged. Each unit's type is built from its member calls. Proved: the units are an `Audit.Partition` of the flattened circuit, and W6, `IsRowsUnit u (derive unit type)`. No IR anywhere | the partition theorem, W6 | 800–1,200 |
| S5 | **The mirror test** (1c) (mine) | flock-soundness, with M0 | S1 (S3 for reads) | `check` compares `flock-rows` with `ir_lower.netlist`, byte for byte, on every pinned unit: RoPE's `933c4ef8…`, #192's pins and #195's. Then on the backend stress test's classes, and later on the hierarchical layouts. Completeness only: a mismatch can only make honest proofs fail | none | ~200 lines of Python |
| 1d | Placement of composed rows | audit-lean, with me | #154, #156, #177, S3 | `Rows.compose`, `compose_topo`, and `placement_compose` from `setupH` through `WellFormed` | theirs | 1,000–1,500 |
| 1e | The verifier derives | flock-verifier, with me | S3, 1d, the constant rollout's steps 2 and 4 | `Stmt.setup` folds `derive`'s rows. Hierarchical statements carry no row sections: `own.rows` goes (below). Old tags stay for old cells. Proved: an accepted `setupH` places `derive`'s rows | theirs | ~1,000 |
| S6 | **Retire L1** (1f) (mine) | flock-soundness | 1e | `ASSUMPTIONS.md`: L1 is proved for statements in the new format. It stays named for old ones, with S5's byte-for-byte match as their evidence. The end-to-end pin | the end-to-end theorem | docs and pins |
| S7 | **`RowsOf c`, specified** (F) (mine) | flock-soundness, with the private-track lane (bc-096c9b8d) | S3 | Φ's clause, beside `WellFormed c`, in `PROTOCOL.md` and `DESIGN.md` | none | docs |

**Order:** S1, S2, S5 (flat units), S3, S4, then 1d, 1e and S6. S7 can go any time after S3.

**What each step buys:**
- **S1–S2:** L1 as a theorem for every flat or inlined unit type. That's today's statements without reads, RoPE's
  among them, for any partition that makes such units.
- **S3–S4:** L1 for every type DAG and every Q_word unit, with no IR.
- **1d–1e:** the executable verifier relies on it, and statements stop carrying rows.
- **S6:** L1 leaves `ASSUMPTIONS.md` for the new statements.

## The format change: dropping `own.rows`

Sent to the constant rollout as a separate note (`20260928T0156Z-note-to-constant-api-from-flock-soundness-placement.md`).
In short:
- a layout record keeps only what the verifier can't derive: its type, its range, its port groups (`in_split`,
  `out_split`), and, per call item, placed (layout and aligned offset) or inlined;
- own rows, bindings and call points come from the type (design §1.9, question 1).

1e needs this in the constant rollout's steps 2 and 4. S1 and S2 don't: a flat type's own rows are fixed by the v2 rule
(design §1.9, question 2).

## Holding

- **Phases 2 and 3** are parked, as Daniel said.
- **D** (the statement builder running `flock-rows`) isn't planned: builders keep their Python layout, and S5 holds it
  to `derive`.
- **The parked per-template branch** (`922b400a`) stays parked. S1–S3 replace it.
