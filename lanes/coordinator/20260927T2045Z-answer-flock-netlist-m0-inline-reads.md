---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: report
from: flock-netlist / M0 (bc-ff572e70)
to: the research coordinator, for Daniel; cc workstream-3 backend stress test (bc-ea1c2c4f)
created: 2026-09-27T20:45Z
---

# Table reads inlined as plain gates on M0's generic path: measured on CPU

**Verdict.** Naive inlining is **not** a non-starter at `Q_word` granularity, with one read per unit. Both requested classes
prove and verify on a 4-vCPU, 16 GB VM:

- each read-bearing class costs a 0.9–1.8 GB circuit and 3.2–5.6 GB per process;
- it takes 8–18 s to load, then under a second to prove and verify at 16 instances.

It **is** a non-starter at the coarse attention cell's 131 reads per unit, computed rather than run:

- about 20.2 G matrix entries, needing about 400 GB per CPU process;
- 4.7× over the GPU path's 32-bit per-circuit limit.

Gemma's 27-bit tanh tables are marginal even at one read per unit: 1.7–2.2 G entries, about 33–43 GB per process.

## What ran

- **Lowering.** `ir_lower.layout` now lays out each table read (`gf2` lookup bits from #140) inline, as ordinary rows of
  the unit. It uses the one-hot construction the red team reviewed (`private/red-team-reviews/m0-statement/review.md` §5):
  - the low and high index halves decode to minterms;
  - there is one product row `hi_h ∧ (⊕ low minterms whose table bit j is set)` per live value bit j and high minterm h;
  - there is one copy row per value bit.

  Empty product rows are left out. There is no slot type, no second net and no wires. Units without reads get
  byte-identical netlists: M0's pin test passes.
  - Branch: `cursor/flock-inline-reads-4d6a` @ `9a4eeed9`, stacked on #83 `73a273d4`. It is inert until #140's `gf2`
    lookups are in the tree.
- **Integration.** The classes come from a local, unpushed merge of #83, `main` `467e7450`, #140 `c37bb04d`, #178
  `6054f205` and #182 `21a0a7cb`. I staged them with #182's own `class_statement.stage`, on synthetic lanes lifted
  through the flat Definition, and proved them with `flock-circuit serve` (verifier) and `prove` (prover) on loopback.
- **Environment.** CPU only. Features `sha512,glue,seed-injection`, `RAYON_NUM_THREADS=4`. No pod was used, and nothing was
  spent.
- **The parked slot branch.** `cursor/flock-unit-reads-4d6a` is kept as local commit `d3b7e64b`, labelled PARKED and
  unpushed.

## Measured, per class

| class (tiny `Q_word`) | reads | own ANDs | unit rows (slot) | matrix entries | circuit file | statement build | peak RSS per process | `verify_s` | proof per rep |
|---|---|---|---|---|---|---|---|---|---|
| `7ec44f2b` attention-exp (`AttentionHead{T=2}` u19, 56 units) | 1 ex2 | 4,231 | 41,473 (2^16) | 153.8 M | 0.89 GB | 8.3–9.0 s | verifier 3.16 GB, prover 3.33 GB | 0.43 s | 555,649 B |
| `99da1701` norm-rsqrt (`LayerPost` u128, 15 units) | 1 rsq | 52,165 | 96,513 (2^17) | 289.5 M | 1.80 GB | 17.9 s | verifier 5.60 GB, prover 5.60 GB | 0.59 s | 555,649 B |
| `70d35316` `LayerPre` u144 (5 units) | 2 (rcp + sqrt) | 79,691 | 160,001 (2^18) | 454.2 M | 2.93 GB | 28.1 s | 9.04 GB (prover and verifier in one process) | — | — |

The first two rows are at n = 16, `k_log` 22, 4 units per block, and all were accepted. The third ran as a selftest subset.

**Checks:**

- **Reference agreement:** every staged class's laid-out rows agree with the reference on every lane; `stage` asserts
  this.
- **Full selftest:** attention-exp passed all 31 cases.
- **Selftest subset:** norm-rsqrt and `LayerPre` passed `honest`, `unit_internal_bit_flipped`,
  `unit_input_differs_from_its_message_bits` and `output_claim_false`. Each ran as its own process, because the full
  suite re-parses the circuit inside one process; that harness peaked at 14.5 GB on ex2.
- **Forcing check:** every row of both requested classes reads only earlier rows or the pinned constant, and there are
  no assertion rows. So the inputs fix the whole witness.

## Per class or per instance

Attention-exp at n = 16, 64, 256 and 1024 instances:

| n | prover wall | build | witness | prove (2 reps) | prover RSS | verifier ready | `verify_s` | verifier RSS | proof per rep |
|---|---|---|---|---|---|---|---|---|---|
| 16 | 10.9 s | 8.9 s | 0.59 s | 0.83 s | 3.33 GB | 7.8 s | 0.43 s | 3.16 GB | 555,649 B |
| 64 | 10.7 s | 8.3 s | 0.77 s | 0.88 s | 3.54 GB | 8.0 s | 0.48 s | 3.16 GB | 584,609 B |
| 256 | 12.3 s | 8.7 s | 0.97 s | 1.82 s | 3.87 GB | 8.0 s | 0.51 s | 3.16 GB | 568,289 B |
| 1024 | 16.3 s | 9.0 s | 3.58 s | 2.84 s | 5.78 GB | 8.8 s | 0.53 s | 3.16 GB | 735,905 B |

- **Per class (the shared circuit).** The table's cost is paid per class:
  - the circuit file, which is pinned and parsed by every verifier;
  - both processes' memory;
  - the statement build;
  - the lincheck fold.

  None of these move with n. The verifier is flat at 3.16 GB and about 8 s plus 0.5 s from 16 to 1,024 instances.
- **Per instance.** The read adds its rows to every instance: 36,007 rows for ex2, 43,109 for rsq. That grows the unit
  slot from 2^13 to 2^16 (ex2), 2^16 to 2^17 (rsq) and 2^17 to 2^18 (`LayerPre`). A lookup slot would commit the same rows
  per read, so per instance, inline and slot cost the same.
  - At these class sizes, each instance's share of the block is 2^20 bits, dominated by M0's input-row hashing. So the
    unit slot holding the read is 1/16 (ex2) to 1/4 (`LayerPre`) of an instance's committed bits.
  - The witness costs two passes over the matrix per 64 instances, about 3.4 ms per instance for ex2 at n = 1024.

## Scaling with reads per class

Cost is linear in the class's matrix entries. Each inlined read adds its table's set bits:

- **Circuit file:** about 6 B per entry.
- **Peak RSS per process:** 19–22 B per entry.
- **Statement build:** 56–62 ns per entry, single-threaded.
- **Verifier fold:** about 1.2 ns per entry, over two reps.

The 1-read ex2, 1-read rsq and 2-read `LayerPre` rows fit this within the ranges above. Per read:

| table | index bits (low + high) | output bits | words | rows per read | entries per read | about per class per read |
|---|---|---|---|---|---|---|
| ex2 | 23 (13 + 10) | 31 | 2^23 | 36,007 | 153.7 M | 0.9 GB file, 3.1 GB RAM, 9 s load |
| rcp | 23 (13 + 10) | 31 | 2^23 | 34,728 | 143.9 M | 0.9 GB, 2.9 GB, 9 s |
| rsq | 24 (14 + 10) | 31 | 2^24 | 43,109 | 288.8 M | 1.8 GB, 5.6 GB, 18 s |
| sqrt | 24 (14 + 10) | 31 | 2^24 | 44,359 | 309.4 M | 1.9 GB, 6.2 GB, 19 s |
| `gelu_tanh_bf16` | 16 (10 + 6) | 16 | 2^16 | 1,903 | 0.39 M | negligible |
| `tanh_mufu` (Gemma) | 27 (16 + 11) | 31 | 2^27 | 104,750 | 1,658.6 M | about 10 GB, 33 GB, 100 s |
| `tanh_rn` (Gemma) | 27 (16 + 11) | 31 | 2^27 | 117,053 | 2,172.4 M | about 13 GB, 43 GB, 130 s |

The 23- and 24-bit rows are measured. The tanh rows are counted from the pinned tables, with the costs extrapolated.

**Repetition is what grows.** The table is paid once per read-bearing class, and in the tiny model that is 10 of the 31
classes:

- 2 ex2 classes, 6 rcp, 2 rsq and 1 sqrt (`LayerPre` holds one rcp and the sqrt);
- 2.06 G entries in total, about 12 GB of circuits, ≤ 9 GB per class.

The five rcp classes are `AttentionHead` T=1…5: FA2's 1/sum adds T terms in the same unit as its rcp read. So a served row
has one read-bearing rcp class, with its own copy of the rcp table, per distinct T in its histogram.

## The coarse data point: the attention cell, 131 reads per instance (computed)

I computed this from its circuit (`k_log` 26, one instance per block) with the reads inlined into its tail:

- **Rows:** the tail's 1,154,051 stage rows plus 130 × 36,007 + 34,728 read rows gives 5,869,689 rows, a 2^23 slot. The
  block is 50.15 M of 2^26 = 67.1 M bits, so `K_MAX` still fits. The slot version used 52.2 M.
- **Entries:** 45.0 M stage entries plus 20.13 G read entries gives **20.17 G**, against 154 M for one ex2 read.
- **At the measured rates:**
  - about 400 GB per CPU process;
  - a 120–160 GB circuit file;
  - about 20 min of statement build per process;
  - about 25 s of verifier fold.
- **On the GPU:**
  - the entry count is 4.7× over the 32-bit CSR limit;
  - the columns alone would be 80.7 GB at 4 B per entry.
- **Per instance:** the witness is about 2 min per 64 instances. That is not the binding cost.

## Blockers, exactly, and the smallest plain-gates fix

1. **Block size `K_MAX = 26`: not a blocker.** One-read `Q_word` classes run at `k_log` 22, and even the coarse cell with
   131 inlined reads fits (50.15 M of 67.1 M bits).
2. **GPU range.** `cuda/prove_circuit.cuh` stores each circuit type's CSR offsets, columns and nnz as `uint32_t`. So one
   unit class holds at most 4,294,967,295 entries: 27 ex2 reads, 13 sqrt, 2 `tanh_mufu` or 1 `tanh_rn`.
   - One-read `Q_word` classes fit.
   - Past that limit, the fix is 64-bit offsets (columns stay 32-bit).
   - The coarse cell would then still need 80.7 GB of device memory for columns. No type fix makes it fit.
3. **CPU memory.** It is about 20 B per entry because:
   - `IrUnitNet` stores `usize` columns;
   - `Stmt::new` clones each unit matrix into a padded copy and leaks it (`pad(&net.a)`, `Box::leak`);
   - the circuit text is held during parse.

   The smallest fix is to move instead of clone, and store `u32` columns. That brings it to about 4–8 B per entry: ex2
   about 1 GB per class, `tanh_rn` about 10–17 GB. The coarse cell stays at 80 GB or more, which is still a blocker.
4. **Per-class repetition (not a limit, but the growth term).** A partition that cuts before each read, so the read and
   its own pre- and post-logic form their own unit class, makes read-bearing classes independent of T. That gives one
   copy of each table per (table, piece), and every unit is still one plain Boolean circuit. It is a partition choice, not
   a prover mechanism, and costs one committed boundary word per read.
5. **Staging tooling, not the prover.** The Python writer holds the whole netlist text several times over: 5.5, 10.0 and
   14.1 GB peak, and 74, 141 and 234 s, for the three classes. A streaming writer fixes it.

## The red team's conditions

The runs stay inside C1 and C2:

- **C1:** no read has a wire, and every read's bits are rows forced by the unit's own index forms (the forcing check
  above).
- **C2's refusals:** `unit_internal_bit_flipped` and `unit_input_differs_from_its_message_bits` are refused on every
  inlined class.

I did not add a separate "flip a read's value and carry it downstream" negative. M0 publishes the unit's outputs, so that
cheat would usually be refused on the output claim, not on the read's row.

## Not measured

- **GPU:** not run (CPU-first).
- **The Lean verifier (bc-8e519ca0):** it would parse the same 0.9–2.9 GB circuit per read-bearing class; its parse cost is
  the open risk.
- **Constant value bits, an aside (not pursued):**
  - bits 23–29 of every ex2 and sqrt word, and bits 24–29 of rcp and rsq, are constant 1;
  - bit 30 is constant 0;
  - so 35–38% of each table's entries encode constant bits.

## Records

- **Measurement data:** `internal/lanes/coordinator/20260927T2045Z-inline-reads-measurements.json` holds every stage,
  session and selftest record, the forcing check and the per-table counts.
- **Code:** `cursor/flock-inline-reads-4d6a`:
  - `9a4eeed9`: the inline lowering and its test;
  - `88db6ee5`: the selftest's input-flip case, fixed for single-unit blocks, as the stress lane reported at 20:50Z.
