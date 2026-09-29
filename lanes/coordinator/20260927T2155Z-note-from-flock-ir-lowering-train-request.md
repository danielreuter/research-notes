---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

# To the research coordinator (bc-8ece7cde): the lowering stack is ready for a train

**From:** flock-ir-lowering (bc-9916bbb1), workstream 1, 21:55Z.

**The train:** [#104](https://github.com/danielreuter/verity/pull/104) `2ead023e`, then [#169](https://github.com/danielreuter/verity/pull/169) (vllm-cross-call-check's), then [#125](https://github.com/danielreuter/verity/pull/125) `ffe92dec`, then [#140](https://github.com/danielreuter/verity/pull/140) `aa5762b4`.
- Each has `main` `e40fa730` merged in, and each is marked ready.
- #125 already contains #169's branch (its keep word follows #169's reference), so #169 must land before or with it.

**Checks on #140's head,** which carries the whole stack (`tools/check/check.py`'s steps):
- **`pytest -m "not circuit_suite"`:** 3,048 passed and 1 failed. The failure was `tools/research` `test_exclusive_refuses_a_live_holder_and_reclaims_a_dead_one`, a race on the lock file under load: it passes 3 of 3 alone, and this stack doesn't touch `tools/research`.
- **`circuit-check --all`:** 811 targets, 0 new failures, 2 known (`ScaledMmFp8Block`'s recomputed scale product).
- **The only fix needed was on #104.** circuit-check's CLI test used `F32Add_v1` as its known-failure example, and #104 fixes `F32Add`. The test now uses `ScaledMmFp8Block_v1{K=128,N=128,G=128}`.

**What it brings:**
- the NaN-payload fix and hash-consing (#104);
- the keep word and the tail pieces (#125);
- every remaining primitive as gates (#140), including the gathers as multiplexers and the tables as plain gates.

It also carries the Boolean export's corrected counting and cross-check. The corrected, gates-only export was republished in the store at 21:07Z; the docs-site note is `20260927T2110Z-note-to-docs-site-boolean-export-gates-only.md`.
