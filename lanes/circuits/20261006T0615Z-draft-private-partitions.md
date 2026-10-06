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

First cut, 06:15Z: X1's predicate list is complete enough for the Lean side (L1) to start; X2 and X3 are initial findings,
completed later in this note. Code: branch `cursor/private-partitions-8c79` (`verity/partition/v2`).

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
  - every FP32 reduction feeds many outputs: RMSNorm's rsqrt, softmax's max and sum. Strict 16 forces each output
    element's unit to recompute the whole reduction. That gives up v1's "no value computed in two units" and multiplies
    each norm unit's proving cost by d.

  The leakage weighting is then ≤ 32 bits per faulty unit, not 16.

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

`{format: "verity/partition/v2", family, predicates: {X, W, recompute, max_gates, max_in_bits, canonical}, units: n_b,
root}`.

- `family` names P.
- `n_b` is the unit count padded to a public grid.
- `root` is the frame-v3-sha512 root over the advice rows, each a hm96-sha512/row/v2 hiding row, registered before any
  coin that depends on it.
- `canonical` is null (free cuts) or a public query such as `Q_word{16, 32}` v1 (query mode, below).

### Advice A (private, the rows under `root`)

- A header: program_sha512(C), n, m, the number of cut-table entries.
- The Call table: row k = (root node index, descriptor id of d_k, start_k).
- The cut table, one entry per distinct d. Either a flat entry (d's id, n_d, U_d, owner_d) or a separable entry (d's id,
  per body node: the child Definition's entry index and its member count).
- Each entry also lists its units' shape digests: the SHA-512 of `units.UnitCircuit.form`, under the one-hash rule; v1's
  SHA-256 shape stays as it is.

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

## X2. Isolation units (initial)

- **Statement.** A coarse partition P_iu of C's computed gates with a placement iu ↦ node: a node or VM behind exactly
  one certifier. The proof units refine it (`Verity.Partition.Refines`). The crossing values are
  ∂G = {g : ∃ h reading g, iu(h) ≠ iu(g)}, plus C's external inputs and outputs. Refinement makes ∂G ⊆ the committed set,
  so the certificate relation reads crossing values from the values tree at their positions.
- **"A part is at least a whole node or VM".** It means placement is a function of the node: every gate the node
  computes is in its one IU (PCIe and host memory are invisible to the certifier). It also must not span nodes: traffic
  between two nodes of one IU would be certified but explained by nothing. So the IUs are exactly the certified nodes
  over the whole registration. A cut in time would make carried state (KV, weights in HBM) a crossing value that never
  crosses the network.
- **These are not NCI's IUs.** NCI's `Complies Γ α` asks for IUs of at most Γ gates (sessions), and a TP-8 session spans
  nodes, so in general neither partition refines the other. The Glossary's IU is NCI's. I propose naming the network's
  partition the *placement* (its parts are IUs in the Glossary's general sense, with no size bound) and stating the bridge
  separately: the certified ingress of a node bounds novelReads of every NCI IU inside it. To check with Daniel's
  "keep code terms".
- **Predicates.** P_iu is a `Partition` (global); PU refines IU (global, per Call: a Call is placed whole, or it is a
  collective Definition whose members are placed per rank, which is how TP Builds output the physical circuit); and
  placement matches the deployment table the certifiers attest. Assembled per Call like X1: a placement table row per
  root Call, which is what TP Builds' `by_rank` already records.

## X3. The schedule as advice (initial)

- **What the schedule is in code.**
  - Per step, `observe.events.StepStart`: rows (request, position), input token ids, positions, seq_lens, num_computed,
    block tables, slot_mapping, logits rows and indices, num_reqs, num_tokens, num_tokens_padded.
  - Per run, the workload manifest that `pipeline/global_program.py` builds the workload Program from: request ids,
    prompt lengths, caps, `arrive_step`, LAG.
  - The dispatch log (`DispatchEnter/Exit`, `TritonLaunch` with `ViewDesc` args) is the engine's trace, not schedule.
    Under bit-exact replay in a pinned engine environment it is a function of (P, the schedule).
- **Why Match's fold is not local.** `observe/fold/fold.py` runs a `MemoryModel` over every event in order: allocations
  with generations, interval writes, a row cache. An attention instance at step t reads KV slots through
  `GatherMany(kv_cache_view, slots …)`, resolved to the latest write before it, at any earlier step (D64). Expanding one
  unit at step t therefore needs the memory state at t, which depends on every earlier event.
- **Making it local (proposal).** Register two things under the schedule root, before any coin:
  1. the per-step schedule rows;
  2. the fold's resolution: per Call, each operand's producer, as (step, Call, leaf).

  Prove the resolution once per window with offline memory checking: the reads, sorted by (address, time), each match the
  latest write. That is a permutation argument, O(reads + writes) per window, exhaustive, the same order as the schedule
  check. A unit's expansion is then local: from i, the Call table (X1's L1) gives step t and Call k; Build(P, s_t) gives
  d_k; the resolution rows give its operands' positions. To be measured: the resolution's size per step against the
  values tree.
