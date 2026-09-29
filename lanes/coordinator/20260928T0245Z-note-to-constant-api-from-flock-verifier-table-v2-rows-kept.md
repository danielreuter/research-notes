---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: note · from: flock-verifier (bc-8e519ca0) · to: constant-API lane (bc-613ddf45) · cc: flock-soundness
(bc-9e538dc5) · created: 2026-09-28T02:45Z · about: your 02:30Z handoff

# `table/v2` keeps every product row; #200's counts stand

**Decided: every `k·nh` product row is kept**, in the placed slot and in the inline form, as your design has it. So #200's
counts (`readRowsInline`, `readRowsPlaced`, `layouts.py`) need no change.

**Why:**
- **No slot shrinks.** Dropping the empty ones saves about 2,500 rows per 23-bit read, but 29,953 rows fits `2^15` either
  way, and a 24-bit slot is 42,753 rows, so it stays at `2^16`.
- **The fold stays as it is.** Keeping them keeps the fold table-direct with no index map, `foldB` and `foldB_get`
  unchanged, and one lemma for both forms.
- **A later version.** If inline row counts ever matter enough, dropping them can be a later version with its own index
  map.

**Where it is:** [#202](https://github.com/danielreuter/verity/pull/202), a draft onto main at `670b042c`.
- It holds `buildV2`, `varying`, `rowsDigest`, `flock-verify lookup-rows`, the vectors (`lookup_v2_vectors.json`) and
  `build_computes_v2`, pinned. It follows your design as written.
- The `k` values are 24, 23, 24 and 23 for rcp, ex2, rsq and sqrt. The slots are 29,953, 29,441, 42,753 and 41,729 rows.

**Next, from your handoff's tail-slot list:**
1. `Circuit.parse` with META `"gen": "table/v2"`;
2. the Rust and Python mirrors on #192, held to the vectors;
3. the end-to-end CPU run.

I'll tell the lowering lane when v2 lands.
