---
id: circuits/20261006T0615Z-draft-private-partitions
campaign: proof-service
lane: circuits
kind: draft
status: open
repo: danielreuter/verity
origin: "@circuits lead (bc-b8aaadaa), items X1-X3 of note:verity-root/20261006T0550Z-report-proof-service-implementation, implementing note:verity-root/20261006T0545Z-draft-daniel-one-recursive-architecture-v2"
---

# Private partitions with public predicates (X1), isolation units (X2), the schedule as advice (X3)

First cut, 06:15Z: X1's predicate list is complete enough for the Lean side (L1) to start. Revised 07:40Z: the advice
encoding as built, measured at m1 scale, and X2 and X3 completed. Code: branch `cursor/private-partitions-8c79`
(`verity.primitives.circuits.partition_v2`, `verity.primitives.commitments.advice`). The width rule's report:
note:circuits/20261006T0655Z-report-strong-reason-unit-output-width.

## Summary

- **v2, not a hidden mode of v1.** v1's contract is that the verifier evaluates the query on a circuit it holds
  (`partition_object.verify`, Lean `Flock.Qword.evaluate`, one-stage's "never takes a population on the prover's word"). A
  private partition breaks that contract, so it gets its own format, `verity/partition/v2`: a public statement (the
  predicates' parameters, the unit count bucket, a hidden root) plus private advice (rows under that root). v1 stays as
  it is for its five consumers.
- **The partition is described per Definition, not per gate.** The advice is a *Call table* (one row per root Call of
  the circuit: its Definition and the index of its first unit) and a *cut table* (one cut per distinct Definition:
  an owner per computing gate, or per-member cuts for a separable Definition). Instances of a specialization are
  layout-identical, so covering, disjointness, the boundary invariant and the width rule hold on the whole circuit iff
  they hold for each cut-table entry, plus the Call table's prefix sums. This is `partition.py`'s tier-A argument and
  v1's `evaluate_definition` memo. The global statement is O(Calls + Σ cut sizes), independent of the unit count.
- **Every predicate a consumer's weighting relies on is global.** A local predicate is checked only on drawn units, and
  an undrawn unit that violates it is just a faulty unit. So the width bound, which turns "≤ k faulty units" into
  "≤ k·W faulty bits", must hold for every unit, faulty or not: it is checked exhaustively, per Definition.
- **"Outputs ≤ 16 bits" is unworkable literally; keep Q_word's single-value exception.** A unit's outputs are at most
  X = 16 bits, *or exactly one value of at most W = 32 bits*. The exception is what the query of record
  (`Q_word{X: 16, W: 32}`) uses today. Without it:
  - the sampler's token id is one I32 value, and the vocabularies served need 17 or 18 bits (Llama 3's 128,256: 17;
    Qwen's 151,936: 18);
  - every FP32 reduction feeds many outputs: RMSNorm's rsqrt, softmax's max and sum. Strict 16 needs each such value
    split into two 16-bit halves, each computed by its own unit: new Definitions, the `report` recompute rule, and
    about +35–38% gates on those Definitions (corrected from the first cut's "×d"; see the report).

  The leakage weighting is then ≤ 32 bits per faulty unit, not 16. As built, the width is a statement parameter:
  (16, 32) is the default, and (16, 16) is the plan's literal rule, which refuses exactly the units in the table.

  Measured on main's Definitions: `Q_word{16, 32}`'s cut, then `cut.fits` at W = 16 (`verity_vllm.query.word.units`).

  | Definition | Units | Units that fail at W = 16 |
  |---|---|---|
  | `RMSNormTriton_v1{N=2048}` | 2,049 | 1: the FP32 scale that all 2,048 elements read |
  | `Attention_v3{T=21, NH=4, KVH=2, D=64}` | 516 | 176, each one FP32 value: the row statistics |
  | `TokenSelect_v1` | 1 | 1: the I32 token |
  | `Gemm_v1`, `SiluMul_v1`, `RoPE_v1` | | none |

  Each failing unit is exactly one 32-bit value.
- **The draft's three unit kinds are not separate predicates.** Dot products rounded to BF16, short scalar chains and
  high fan-in graphs are what `Q_word{16, 32}` produces. Soundness doesn't need them. The width rule gives the leakage
  bound. A count bound stops the prover from splitting units to inflate n. Size caps fix the proving shape.

## X1. The predicates

### Objects

All of these are `verity.primitives.circuits` objects.

- **C.** A Program whose root body holds Calls k = 0..m−1, each an activation of a Definition d_k (`partition_object.calls`).
  In deployment C = Build(P, s): P is the public template (model, engine environment, TP layout), s the private schedule
  (X3).
- **CallGraph(d).** d's computing gates c = 0..n_d−1: not inputs, not structure, compacted in layout order. Structure means
  constants, `cut.WIRING` primitives, and gates computed from constants alone; they are in no unit, and each reader unit
  carries its own copy, as in `units.UnitCircuit`. CallGraph also gives the edges src→dst, the declared widths w(c), the
  returned gates, the reads of d's parameters and the recomputed pairs.
- **A cut of d.** owner_d : [0, n_d) → [0, U_d). Unit (k, j) is S = owner_{d_k}⁻¹(j) in activation k, and its index is
  i = start_k + j, where start_k = Σ_{k'<k} U_{d_k'}. The unit count is n = start_m.
- **in(S) and out(S).** As in `parts.py`: out(S) = {c ∈ S : c is returned by d, or some c→c' has owner(c') ≠ j}.
  ob(S) = Σ_{c ∈ out(S)} w(c) and og(S) = |out(S)|. The committed set is derived, never stored: the Call parameters
  (C's input leaves), the returned gates, and every gate read across a unit boundary (Lean `Verity.Partition.committed`).

### Public statement Σ (what the verifier holds)

`{format: "verity/partition/v2", family, predicates: {width: [X, W], recompute, max_gates, max_in_bits, canonical,
grid_bits}, units: n_b, advice: {rows: R_b, root}}` (`partition_v2.statement`).

- `family` names P.
- `n_b` is the unit count padded to a public grid: the least value ≥ n with at most `grid_bits` significant bits
  (default 4, so fillers are under 1/8 of n). R_b is the advice row count on the same grid.
- `root` is the frame-v3-sha512 root over the advice rows, each a hm96-sha512/row/v2 hiding row, registered before any
  coin that depends on it.
- `canonical` is null (free cuts) or a public query such as `Q_word{16, 32}` v1 (query mode, below).

### Advice A (private, the rows under `root`)

As built (`partition_v2.rows`): 128-byte rows, each a `BitRowLeaf(1024)` committed as a hm96-sha512/row/v2 leaf
(`advice.leaf`: `row_leaf(domain, i, SHA512.tree_leaf(key, commit_string(key, digest(row), salt)))`), in one
frame-v3-sha512 tree over `RangeIndexedDomain(R)`, port `advice`. R is padded to the statement's `advice.rows`.

- A header row: magic, program_sha512(C), n, m, e (entries), rows used.
- The Call table, one row per Call: (root node index, entry index, member count, start_k), 8 bytes each.
- A directory, one row per cut-table entry: (definition digest, kind, n_d, U_d, payload start, payload rows, items).
- The payloads.
  - Flat: owner_d as u32s; then a class index per unit as u32s; then the class digests, 2 per row. A class is a distinct
    unit shape, the SHA-512 of `units.UnitCircuit.form` under the one-hash rule (v1's SHA-256 shape stays as it is), so
    a Gemm's 4,096 equal units store one digest. A one-unit entry stores only its class digest row; its owners and class
    are 0 by definition.
  - Separable (parts): (child entry or NONE, member count) pairs, 8 per row.
- Opening a unit (L1, L2) needs: the header, the Call-table rows a bisection reads, the directory and parts rows along
  the path, the flat entry's owner rows (L2 cuts the unit's gates out of them), the unit's class-index row and that
  class's digest row. The rows read depend on the Definition holding the unit, never on n.

Measured on m1 (SmolLM2-135M, 16 steps, 519M computing gates, `Q_word{16, 32}` v2's cut): 15,740 rows (2.0 MB), built in
13 s; G1–G7 checked in 14 s at about 630 MB under `report`, and in 93 s under 1.4 GB under v1's `refuse`, where the
one-pass recompute check runs over every parts body; a unit's L1+L2 opening is 41.6 rows on average, 127 at most. Most of the
opening is the owner rows of the flat entry, at 32 owners per row. Not done yet: a per-unit index (each unit's first
owner row and count) would open only the unit's own owner rows.

### Global predicates

These are proved exhaustively, once per registration, in one fixed-shape statement over A. The verifier never sees A.

| # | Predicate | Stated over |
|---|---|---|
| G1 | **Calls.** The Call table lists C's root Calls, the root body's nodes other than input nodes, in body order, each with its Definition's descriptor id. start_0 = 0, start_{k+1} = start_k + U_{d_k}, and n = start_m. This binds A to C | the root body, `partition_object.calls` |
| G2 | **Partition** (covering and disjointness). One entry per distinct d. owner_d is total on CallGraph(d)'s computing gates and its values are exactly 0..U_d−1, so no unit is empty. Inputs and structure are in no unit. A separable entry is valid iff each child entry is (`cut.separable`: no value crosses between nodes) | CallGraph(d) |
| G3 | **Boundary.** `partition.validate_unit_cut` through `cut.check_cut` with the derived committed set: reads cross units only through committed values, and every returned value is committed | CallGraph(d), owner_d |
| G4 | **Width.** Every unit fits: ob ≤ X, or og = 1 and ob ≤ W (`cut.fits`, EXTRAS = 0). X = 16, W = 32 | `cut.boundary_widths` |
| G5 | **Recompute.** No value is computed in two units (`refuse`, v1's rule). Or, with recompute = `report`, Q_word v2's rule: such values are reported, not refused | CallGraph.recomputed |
| G6 | **Count.** n ≤ n_b, and n_b is the least grid level ≥ n, so the fillers n..n_b−1 are fewer than one grid step. Optional (`canonical` set): U_d ≤ U_{Q(d)} for every d, so the cuts make no more units than the public query does. This is the draft's "the fewest steps" as a count, which is what the profile's bound ε·n·W needs | the cut table |
| G7 | **Shapes.** Each entry's shape digests are those of its units' circuits (`units.Activation.circuits(owner_d)`), with ≤ max_gates gates and ≤ max_in_bits input bits | `units.UnitCircuit` |

### Local predicates

These are proved with drawn unit i, inside its unit statement.

| # | Predicate |
|---|---|
| L1 | **Locate.** Open Call-table rows k and k+1 with start_k ≤ i < start_{k+1}, so j = i − start_k. G1 gives their adjacency. Then open d_k's entry and unit j's shape digest. For i ≥ n (a filler), the unit is empty and its proof is a dummy of the fixed shape |
| L2 | **Statement.** The inner proof's circuit digest equals unit j's shape digest. G7 guarantees that this circuit is C's gates of unit (k, j) |
| L3 | **Bind.** The unit's outputs and the inputs it reads inside activation k are the values-tree leaves at (k, local gate). An input that is a parameter leaf of d_k is the leaf of whatever the root body wires that parameter to: another Call's returned gate, or an input leaf of C. Those leaves come from X3's resolution rows, local per Call. Positions follow from (k, j) and the entry's derived committed set (G3) |
| L4 | **Correct.** `Verity.Partition.Correct X u`: the unit's committed outputs are its gates applied to its committed inputs |

### Proving covering and disjointness without revealing the partition

The class argument: G1 and G2 over the Call table and the cut table. This needs no per-gate column, and none of it
leaves the statement.

The general alternative commits owner[g] per gate of C, with a permutation argument. The multiset of owners must equal
⊎_u {u}^{|S_u|}, so a drawn unit whose opened gate list S_u ⊆ owner⁻¹(u) has |S_u| = |owner⁻¹(u)|. It is O(|C|) per
registration. It is worth it only for units that cross Definitions, and there are none today: `units.PartitionUnits`
assumes units inside Calls.

### Query mode

With cut_d = Q(d) for a public Q (`canonical` set and no free cuts), G2–G7 for each d are a public function of d. P is
public, so the verifier, or Lean once per template over its parameter range, checks them offline. The registration
statement then proves only G1 and G6. This is the cheapest migration for vLLM: its programs use Q_word v1 now, so it
keeps the public rule and makes the circuit and its instantiation private.

### What the verifier still learns

It learns n_b, a grid level per registration (log₂ of the number of levels, as PoUW's N), and the parameters (X, W,
recompute, caps, the query in query mode). It learns its own drawn indices and each unit's verdict.

It does not learn C's Calls, its Definitions, the cuts, or the kinds and shapes of drawn units, provided three things
are padded:

- every inner unit statement to the cap class inside the fixed outer shape (P3);
- the values tree to a bucket, since its leaf count is the committed set's size;
- the registration statement to public caps on m and on the cut-table rows, since its shape is otherwise the
  schedule's size.

### For L1 (the Lean side)

1. A spec over `Verity.Partition`, whose type already gives covering and disjointness: `Fits X W P := ∀ u, ob u ≤ X ∨
   (og u = 1 ∧ ob u ≤ W)`, with ob and og read from `P.committed` ∩ `P.gates u`. Add the recompute rule, and n ≤ n_b.
2. Assembly: a Call table and a cut table give a `Partition C n`, with unit g = start_k + owner_{d_k}(local g). The class
   lemma: the per-entry checks (`Flock.Partition.checkCut`, which exists) and the Call-table check imply `Fits` on the
   whole circuit.
3. The audit statement quantifies the partition: ∃ P, Fits P ∧ Commit(A(P)) = root. After registration, binding makes P
   unique, and one-stage's `audit_le` applies to that P with population n_b.

## X2. Isolation units

The code term is open: I write *placement* for the partition and *part* for its pieces, pending Daniel. The Glossary's
"isolation unit" stays NCI's.

### The statement

- **Objects.** A coarse partition P_iu of C's computing gates, with a map from parts to nodes. A node is a machine or VM
  behind exactly one network certifier. The deployment table D is public: the certified nodes and their certifiers' keys.
  The proof units refine P_iu (`Verity.Partition.Refines`).
- **Crossing values.** ∂G = {g : some h reading g has part(h) ≠ part(g)}, plus C's external inputs and outputs, which
  enter or leave through a node. The certificate relation reads ∂G from the values tree at its positions.
- **"A part is at least a whole node or VM".** Placement is a function of the node: every gate a node computes is in
  that node's one part. PCIe and host memory are invisible to the certifier, so a cut inside a node would be traffic
  nobody certifies. A part must not span two nodes either: traffic between two nodes of one part would be certified but
  explained by nothing. So the parts are exactly the certified nodes, over the whole registration. A cut in time would
  turn carried state (KV, weights in HBM) into a crossing value that never crosses the network.

### The predicates

| # | Predicate | Global or local | Stated over |
|---|---|---|---|
| I1 | **Placement.** Each root Call k is placed on one node of D, or, for a collective Definition (a parts entry whose members are ranks), each member on one node of D | global | a placement row per root Call |
| I2 | **Refinement.** Every proof unit lies in one part | global; free by construction | v2's locate: unit i ↦ (Call k, member path, j) |
| I3 | **Crossings committed.** ∂G ⊆ the committed set | global; follows from I2 and G3 | `cut.check_cut` |
| I4 | **Certified.** For each node, the crossing values it reads from other nodes, and those it sends, are what its certifier attests: their count and size, or their digest in wire order | global, per node | D, the certificates, the values tree |

- **I2 is free.** v2 locates every unit inside one Call, and inside one member of a parts entry
  (`units.PartitionUnits` assumes units inside Calls). If placement is per Call or per member, a unit's part is the part
  of its Call or member, and no unit can straddle two parts. The registration statement only checks I1 against D.
- **I3 needs no new check.** A value read across parts is read across units, so G3 already commits it.
- **I4 is the network certifier's relation, and it must be global.** A local check on drawn units would let an undrawn
  unit's crossing go unexplained: certified traffic with no committed value behind it is exactly what the certifier must
  rule out. Its cost is O(|∂G|), the size of the traffic.
- **Privacy.** The placement rows go under the advice root with the Call table. The verifier learns D, the certificates
  (which the network certifier publishes anyway) and the part count. It does not learn which Call ran where.
- **Encoding.** One row per root Call holds a node index, or PER_MEMBER and a pointer to a member-to-node row. This
  follows the Call table, so the registration statement checks I1 in O(m).

### What exists, and what doesn't

- **TP already places by rank.** `query.compose` keys each rank's partition `by_rank`, and `pipeline/global_program.py`
  records one weights root per rank (`per_rank`). A rank is a GPU, not a node. TP-8 on one node is one part, and the
  all-reduces inside it cross no part. Rank to node is the deployment table, which nothing in the repo records today.
- **Not built.** I did not build the placement rows or I1–I4. They need the certificate's format, which is the network
  certifier's (`protocols/network_warden`, renamed at ~09:00Z), and a deployment with more than one node to test against.
- **The bridge to NCI.** NCI's `Complies Γ α` asks for isolation units of at most Γ gates (sessions). A TP-8 session can
  span nodes, so in general neither partition refines the other. The bridge is a separate lemma: a node's certified
  ingress bounds the novelReads of every NCI isolation unit placed inside it.
- **Open for Daniel:** the name ("placement", or "isolation unit" with NCI's renamed), and whether I4 attests counts or
  digests.

## X3. The schedule as advice

### What the schedule is in code

- Per step, `observe.events.StepStart`: rows (request, position), input token ids, positions, seq_lens, num_computed,
  block tables, slot_mapping, logits rows and indices, num_reqs, num_tokens, num_tokens_padded.
- Per run, the workload manifest that `pipeline/global_program.py` builds the workload Program from: request ids, prompt
  lengths, caps, `arrive_step`, LAG.
- The dispatch log (`DispatchEnter/Exit`, `TritonLaunch` with `ViewDesc` args) is the engine's trace, not the schedule.
  Under bit-exact replay in a pinned engine environment, it is a function of (P, the schedule).

### Why Match's fold is not local

`observe/fold/fold.py` runs a `MemoryModel` over every event in order: allocations with generations, interval writes,
and a row cache. An attention instance at step t reads KV slots through `GatherMany(kv_cache_view, slots …)`, resolved
to the latest write before it, at any earlier step (D64). Expanding one unit at step t needs the memory state at t, and
that depends on every earlier event.

### Making it local

Register two things under the schedule root, before any coin:

1. the per-step schedule rows;
2. the fold's resolution: per Call, each operand's producer, as (step, Call, leaf).

Prove the resolution once per registration window with offline memory checking. The reads and writes, sorted by
(address, time), must have each read match the latest write before it. That is a permutation argument, O(reads +
writes), exhaustive, and global.

A unit's expansion is then local:

- from i, the Call table (X1's L1) gives step t and Call k;
- Build(P, s_t) gives d_k;
- the resolution rows give its operands' positions in the values tree.

The trace is not needed: the memory check is over the writes and reads of Build(P, s) itself, so the prover supplies s
and the resolution, and the verifier never sees the dispatch log.

### Measured on m1

SmolLM2-135M, 16 steps, from `fold(…, with_program=True)` with its memory model's counters:

| Quantity | m1 |
|---|---|
| Events | 49,092 |
| Template instances | 14,226 |
| Memory reads resolved | 93,326 (64,860 of them row-cache hits) |
| Writes | 20,112 |
| Allocations | 4,623 |
| Values-tree leaves | about 1.35 × 10^8 input leaves |

- **The resolution is small.** It is about 10^5 records: under 0.1% of the values tree. The memory check is
  about 1.1 × 10^5 operations per 16 steps, or about 7,000 per step.
- **Row-cache hits count as reads.** They are still resolved to a write, so they belong in the memory check. The cache
  only saves the fold's work.

### What is left

- The resolution's row format: in the advice tree beside the Call table, or under its own root.
- The memory check's statement, in core's Lean beside `Verity.Partition`.
- A TP measurement: one fold per rank, plus the collectives' cross-rank reads.
- Whether `StepStart`'s fields are all schedule or partly derivable: slot_mapping follows from the block tables and
  positions. Fewer fields would mean fewer rows to bind.
