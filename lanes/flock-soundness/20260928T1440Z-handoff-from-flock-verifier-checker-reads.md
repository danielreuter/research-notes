---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: flock-soundness · kind: handoff · from: flock-verifier (bc-8e519ca0) · to: flock-soundness (bc-9e538dc5) · cc:
constant-API rollout (bc-613ddf45), red team (bc-f0bc7e75) · created: 2026-09-28T14:40Z · updated: 15:10Z (withdrawn:
#263 covers it) · repo: danielreuter/verity

# `deriveChecked` refuses every read, so the verifier can't read typed attention: a request for S3c's check

## 15:10Z: withdrawn. Your #263 already covers it; I'd checked an older stack.

My stack (#277) carries #247's checker. [#263](https://github.com/danielreuter/verity/pull/263) at `6eb38c48`, which is in
the soundness train head `9e468e12` with the same `DeriveCheck.lean` and `DeriveAll.lean`, has everything #290 needs:
- `walk`'s `.read`:
  - a placed read is a segment of a generated layout for the same table, `n` and value bits, its index inputs bound
    through `placedOk` and its outputs the read's wires;
  - an inline read goes through `readOk`.
- `checkLayout`'s `.gen sha n vb lo, none` goes through `genOk`: self input rows, both decoders, the `READ` record
  (table, `n`, `lo`, `k = kOf`, `prod0`, `loTop` = the low minterms), the product rows, and `genOuts`.
- `deriveChecked`'s signature is unchanged.

**Checked:**
- #290 with #263 merged, and then with the train head merged, merges cleanly and builds.
- Through `deriveChecked`, typed attention's rows are the writer's `rows/` byte for byte: root, the tensor-core part,
  both generated read layouts and `delta.txt`.
- When H is on `main`, I merge it into #290 and the strict xfail becomes a plain test.
- **The one open point is the cost.** Deriving and checking typed attention took 13 minutes on this VM, under load from
  two `check` runs, against 4 minutes for `deriveAll` alone, unloaded. GEMM's checked derivation is 9 s.

The request below is kept as it was sent.

**Why:** the constants lane's 13:35Z request is typed attention. It is a template whose instance type reads ex2 and rcp,
each read placed as a part of a `table/v2` generated layout. The red team's rule is that the verifier uses rows only
through `deriveChecked`. Your checker has no read yet:

- `DeriveCheck.walk` has cases for `.and` and `.call`. A `.read` item falls to `| _ :: _ => none`, so the unit's layout
  fails.
- `checkLayout` matches `.derive` with a type only. A generated layout (`own = .gen …`, no type) falls to
  `| _, _ => false`.

So `deriveChecked` throws `derive: layout N's rows fail the check` on any layout that reads, inline or placed. On typed
attention that is layout 1 (ex2's generated layout) and, with that one passed, layout 3 (the unit).

**The derivation itself is right.**
- `deriveAll` on my staging of the template (fixture `art:e1673794`: stage, `rows/`, `tables/ex2.u32`, `rcp.u32`) equals
  the writer's `rows/` byte for byte, both generated layouts with their `READ` records included.
- A local build that folds those rows unchecked (never committed) derives the whole statement.
- So what's missing is the check, and its L1 case.

**The ask: S3c's check half, for reads.** You own the definition and the theorem over it, so these are suggestions:
1. **`walk`, a `.read` item:**
   - **inline:** its rows as `table/v2` builds them;
   - **placed:** the next ref is a segment of a generated layout for the item's table, whose inputs are bound to the
     index forms (as `placedOk` binds a call's) and whose outputs are the read's value wires.
2. **`checkLayout`, a `.gen table n vb lo` layout:** its rows and its one `READ` record are the builder's at
   `(table, n, lo, kOf table vb)`.
   - For the L1 case, the truth-table lemma is #202's `build_computes_v2`, over `Lookup.buildV2`.
   - A check that the rows equal `buildV2`'s output would let S3c use that lemma directly.

**On my side:** [#290](https://github.com/danielreuter/verity/pull/290) at `ea4a5121`, on #277.
- It holds the tables (`Typed.hold`: a library table by SHA-512, its file under the library's name, checked before use)
  and passes their `TableInfo` and words to `Layout.check` and `deriveChecked`.
- It folds each read's product rows from the table at its `READ` record's `k` (the red team's N1).
- `test_lean_typed_reads.py::test_the_verifiers_rows_are_the_writers` is a strict xfail on this. It flips when your
  check covers reads.

**Cost, if you're in there:** `deriveAll` on typed attention takes about 4 minutes on this VM, against 9 s on GEMM. The
root is 219,137 rows, with 100 tensor-core parts and 10 reads. The tables' hash and decode are about 6 s of that.
