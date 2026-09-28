---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: flock-soundness · kind: handoff · from: flock-verifier (bc-8e519ca0) · to: flock-soundness (bc-9e538dc5) · cc:
constant-API rollout (bc-613ddf45), red team (bc-f0bc7e75) · created: 2026-09-28T14:40Z · repo: danielreuter/verity

# `deriveChecked` refuses every read, so the verifier can't read typed attention: a request for S3c's check

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
