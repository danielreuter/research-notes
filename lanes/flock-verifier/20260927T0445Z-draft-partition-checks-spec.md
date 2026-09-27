---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: flock-verifier · kind: draft · status: adopted · created: 2026-09-27T04:45Z · repo: danielreuter/verity (PR #85)

# The partition checks the Lean verifier still needs: a spec, and who owns each part

**Design change (Daniel, 2026-09-27 05:28Z): the partition is a named query, P = Q(C).**

This supersedes §2's stored `owner` and `committed` arrays, and the 04:32Z block below where they differ.
- **The partition object** holds only the program digest and the query's name, version and parameters, for example
  `Q_word_v1{X=16,W=32,R=no-recompute}`.
- **The verifier evaluates the query** on its own copy of the program, then checks the invariant (P1) and the width rule
  (P2) on the cut it computed.
- **Units and committed values are derived**, never read: units from the evaluated cut, and the committed set from
  #111's `derived_committed`, where a value is committed exactly when another unit reads it or the Call returns it.
- **Core.** cross-call-check writes the canonical evaluator in core (#111), with exact structural ids and a written
  algorithm. Its current tip (`7ddb7cca`) still stores a cuts table; the change is theirs to make. #111's
  `verity/ir/cut.py` already holds the graph (`CallGraph`) and the width rule (`fits`, `boundary_widths`, `check_cut`).

**The Lean verifier's order,** each step with a conformance test against core:
1. P2: the width rule and derived committed set on a cut (`check_cut`).
2. P3: membership.
3. Graph extraction (`CallGraph`) from the verifier's copy of the program.
4. The query evaluator, in place of any stored-partition reading.

P4, leaf positions, is unchanged. The `unit-cut` command stays as the invariant's test harness on explicit cuts.

**Dependency for step 3.** `CallGraph` runs on the in-memory IR: a one-Call `Program`, `layout.resolve`, refs, batch
members and wide fan-in. For Lean to derive it from bytes, core must pin two things:
- the program's serialized form the verifier holds (the descriptor codec, or `program.json`);
- the canonical-layout semantics graph extraction uses.

That is **core's** (`verity.ir`), unless #111's written algorithm covers it.

**Decided (coordinator, 2026-09-27 04:32Z).**
- The coordinator adopted §2's `verity/partition/v1` object and its SHA-512 digest.
- The cross-call-check lane (`bc-f7aadce6`) owns the partition checker. It implements the object in core and moves the
  width and graph references there.
- The order in §4 holds: the Lean verifier adds P2, then P3, then graph derivation as those references land.
- P4 waits for the position function and M0's port-to-row map.

The short answer below is the original proposal; this block supersedes its owner and decision lines.

PR #85 has the partition invariant on one explicit cut (`flock-verify unit-cut`, PROTOCOL.md §16.7). It agrees with
`verity.ir.partition.validate_unit_cut` on 5000 random cuts. Three parts are still pending: the width rule, checking that
the claimed units belong to the partition, and deriving leaf positions from the partition. This note specifies them and
the objects they read, and names an owner for every piece I can't settle myself.

The target statement is the one in `docs/boolean-core-architecture.md` §1.5: program digest, partition digest, a circuit
digest shared by every unit in the table, units as indices into the partition, and root ids. The verifier derives every
leaf position itself.

## Short answer

- **No lane owns the partition checker.** The routing doc
  (`internal/commitments-decisions-routing.md` §2) names the role, but no lane holds it. M0 is waiting on it too: #83's
  next statement binds a provisional partition digest, `flock-circuit/unit-cover/v0`, "until the partition checker defines
  one" (`internal/flock-netlist-serving-row-leaf.md`).
- **Proposed owner: the vLLM VU-export lane** (under the vLLM coordinator). It wrote `Q_word_v1`, the cut
  (`integrations/vllm/verity_vllm/query/word.py`: `Graph`, `partition`, `units`) and `validate_unit_cut`. The graph, the
  cut and the width rule are all its code.
- **Daniel decides** the partition object's format and digest (§2 below), because both M0's statement and the roots bind
  it.
- **The Lean verifier** (this lane) ports each reference once it is in core, and keeps the checks in §3.

## 1. What the verifier holds

Everything comes from the verifier's archive, keyed by SHA-512 (PROTOCOL.md §16.8):

- **The program.** The Verity IR Program the roots were registered against.
- **The partition** (§2), whose digest the statement and the roots bind.
- **Each class's circuit.** This is the unit circuit a table proves, the file M0 stages today.

The prover supplies none of these; it only names them by digest.

## 2. The partition object (proposal: `verity/partition/v1`)

~~~text
{"format": "verity/partition/v1",
 "program": "<SHA-512 of the program>",
 "calls": [{"call": <the Call activation's index in the canonical layout>,
            "owner": [<unit within the Call, per computing gate in canonical order>],
            "committed": [<computing gates committed at serving, ascending>]}, …],
 "units": [{"call": <index into calls>, "unit": <owner value>, "class": "<SHA-512 of the unit's circuit>"}, …]}
~~~

- **The digest.** `SHA-512("verity/partition/v1\0" ‖ canon(object))`. It replaces `flock-circuit/unit-cover/v0` in M0's
  statement. The roots bind it (architecture §1.6).
- **Unit indices.** A unit's global index is its position in `units`: ordered by Call in canonical layout order, then by
  owner value, which is the order `word.partition` creates units in. The input unit is not in `units`. It is always
  checked and never drawn.
- **What stays out.** The query that produced the cut is provenance (architecture §1.6: "the query or cut policy that
  produced the partition is provenance, and no root binds it"). The width rule's parameters therefore come from the
  verifier's pinned profile (§3.2), not from the partition.
- **What is not partition data.** Reads, widths, outputs, input reads, recomputes, and the total and structure gate
  counts are properties of the program. The verifier derives them from its own copy (§3.1) and never reads them from the
  partition.

## 3. The checks

### 3.1 P1, the invariant, on graphs the verifier derives

`validate_unit_cut` runs per Call, on `owner` and `committed` from the partition and on the Call's computing graph. This
part is done: PR #85, §16.7.

**Pending: deriving the graph.** Today `flock-verify unit-cut` reads the graph from the cut file, so the build's graph is
trusted. The verifier must instead compute, from its own copy of the program, what `word.Graph` computes:
- the computing gates, with wiring (`WIRING`) and constants removed and reads re-pointed through them;
- each gate's width (`prim.ret.w`);
- the returned gates, in return order;
- the Call's parameter reads, the recomputed pairs, and the total and structure counts.

- **Reference.** `integrations/vllm/verity_vllm/query/word.py` `Graph`. It needs moving into core (`verity.ir`, beside
  `validate_unit_cut`), because a backend's tests may not import an integration. Owner: **vLLM VU-export lane**.
- **Lean side.** Decoding the IR program, the canonical layout, and the graph extraction. This is the largest piece of
  work; owner: **Lean verifier**. It needs the IR program's serialized form pinned: the descriptor codec in `verity.ir`,
  or `program.json`. Owner: **core**.

### 3.2 P2, the width rule

Per computing unit `u` of each Call:

~~~text
out(u)   = { g : owner[g] = u  and ( g returned  or  some read (g, q) has owner[q] ≠ u ) }
ob(u)    = Σ_{g ∈ out(u)} w(g)          (bits)
og(u)    = |out(u)|
u passes ⇔ ob(u) ≤ X + E  or  ( og(u) = 1  and  ob(u) ≤ W + E )
~~~

- **Parameters.** X, W and E are `Q_word_v1{X, W, EXTRAS}`'s parameters (today X = 16, W = 32, E = 0), pinned by the
  verifier's profile.
- **Failure code.** `unit-too-wide`, listing the units and their `(ob, og)`.
- **The input unit is exempt.** A computing gate's own width is a separate program property, `readiness_32bit`.
- **Which width is meant.** `word.py`'s docstring says the rule counts elements, but its code (`units`: `out_bits`,
  `out_gates`, `ok`) counts bits. This spec follows the code. `verity.ir.partition.validate_width` (w_out(S) ≤ w_max) is
  the older single-threshold form, and the verifier does not use it.
- **Reference.** `word.units(...)["ok"]`, to move into core next to `validate_unit_cut`: for example
  `validate_unit_cut(..., width=, limits=(X, W, E))` adding the code `unit-too-wide`. Owner: **vLLM VU-export lane**. The
  Lean side is small, and I can port it the day the core reference lands.

### 3.3 P3, the claimed units belong to the partition

For a session's statement `{program, partition, circuit, units, roots}` and its unit draw (PROTOCOL.md §7.3):

1. `program` and `partition` name objects the verifier holds, and `partition.program = program`. P1 and P2 pass on every
   Call. A partition is checked once and cached by its digest.
2. The draw's `population` is `|partition.units|`: the units the partition defines, never a number the prover states.
3. `statement.units` equals the draw's `units` (ascending, distinct, each below the population). Instance `i` of the table
   is unit `units[i]`. This is U1–U3, already in PR #85, once the statement names its units.
4. Every claimed unit's `class` is `statement.circuit`: one table per class. M0's coming multi-table statements need one
   `circuit` per table, and the rule then applies per table.
5. The roots were registered before the draw. This is a live-side ordering fact, recorded by `flock-live serve` (M0) and
   checked offline from the record.

- **Owners.** The format is **Daniel's decision** (§2). The statement fields and the draw on the live side are **M0**,
  which already binds per-block unit indices checked against the range at load. The checks are the **Lean verifier's**,
  and are small once M0's format lands.
- **Gap until the verifier lowers circuits itself.** The verifier takes `class → circuit` from the partition. The
  architecture's target (§1.5) is that the verifier lowers each unit's circuit itself and compares digests; that is Lean
  work on top of §3.1.

### 3.4 P4, leaf positions

For each claimed unit `u`, take the committed values it touches:
- `in(u)`: the committed values `u` reads, meaning the sources of reads into `u` from other units, plus the Call's
  parameters;
- `out(u)`: the values `u` produces that are committed.

For each such value `v`, the verifier computes `pos(v) = (root, leaf, offset within the row)` from the program, the
partition and the commitment layout, and nothing the prover sends. The checks:

- The table instance for `u` exposes its public rows per port. These are M0's serving row leaf: `frame-v3-sha512` leaves
  under `hm96-sha512/row/v1`, with the public `b ‖ c`. Each must be the leaf at the position derived for that port's
  values.
- Each leaf's Merkle path checks natively against the registered root.

Pieces:

- **The commitment layout.** Which committed tensor and which row each committed value lands in, with rows "in the
  orientation the consumer reads them" (architecture §1.6), and the tree's leaf order (`vllm-v1`'s node and lift rule with
  frame-v3's derived positions). Owner: **core commitments** (`verity.commitments`), with **vLLM serving** for which taps
  commit which tensors (`word.committed_today`, `tap_kernel`). This needs a reference function in core:
  `position(program, partition, layout, value) -> (root, leaf, offset)`.
- **Ports to rows.** Which of a unit circuit's ports (`META` ports: name, words, chunks, nb) holds which committed rows,
  in what order. Owner: **M0**, in the next statement format with the serving row leaf.
- **The Lean side.** A port of the position function, and checking the Merkle paths against the roots. The SHA-512 frame
  and HM96 leaf code is already in the verifier. Owner: **Lean verifier**.

## 4. Order of work

1. **Daniel** settles the partition object and its digest (§2). **M0** swaps `flock-circuit/unit-cover/v0` for it.
2. **The vLLM VU-export lane** moves `Graph` and the width rule into core, beside `validate_unit_cut`, with vectors.
3. **The Lean verifier** adds P2 (small), then P3 (small, once M0's statement names program, partition, circuit and
   units), then graph derivation from the program (large).
4. **Core commitments and M0** specify the position function and the port-to-row map. **The Lean verifier** then adds P4.

Until step 3 lands, PR #85's unit-cut check establishes the invariant on a cut whose graph the build supplies. It does not
yet establish it on the program.
