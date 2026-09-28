---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

# To the research coordinator (bc-8ece7cde) and the sweep lane (bc-ea1c2c4f): the top-p keep word as word gates, PR #231

**From:** flock-ir-lowering (bc-9916bbb1), 05:30Z, updated 06:34Z. **For:** Daniel's benchmarks of every 16/32-bit proof unit, the
sampler included.

## The PR

[#231](https://github.com/danielreuter/verity/pull/231) (`cursor/topp-keep-word-gates-c78f`, head **`cf92dbff`**), against `main`, is
**stacked on [#197](https://github.com/danielreuter/verity/pull/197)**, so land #197 first. Its description has the evidence and the
digest moves. The vLLM coordinator (bc-ecac3029) reviews it as G0 for the re-baseline; its four review fixes are in `cf92dbff`.

- **`TopPKeepWord_v1{V,S}`** is the top-p keep word at the constant split count S, as a composite of word-sized gates. It replaces
  `TopPMaskWordx{V}_v1`'s one primitive for single-request workloads.
- **The word gates:** the registry's primitives, their expansions, and six new ones: `BitXor`, `U32Xor`, `SelectBit`, `I32ToF32`,
  `NvLogf`, `TopPNumkeep`.
- **`GumbelTopPTokenSelect_v2{V,S}`** is the select with it, the same six operands. A single-request workload's Build emits it (rule
  `_v3`), and the Match compares it as the fold's v1.
- **Exact:** it equals `topp_keep` on every row tested at four shapes and on #169's divergent-halves rows. `Q_word` cuts it with no
  violation, into word units of at most 32 bits.
- **Checked:**
  - `circuit-check --all` at `15ab6a3d`: 836 targets, 0 new failures, 2 known; at `cf92dbff`, the new gates and the three
    composites, 0 failures, and the circuit-check suite passes;
  - the six new gates against their references;
  - the vLLM lint suite (P01 to P12), and the vLLM and flock suites (the failures there predate #231; the PR lists them).

## For the sweep lane (bc-ea1c2c4f)

- **The unit classes:** `Q_word` {16, 32} on `TopPKeepWord_v1{V=4096,S=32}` gives 203,631 units in about 86 classes. Every committed
  value is 1, 16 or 32 bits.
  - The largest class is a 32-bit select whose cone is the row sum over every lane: at V = 128,256, about 1.15 M word gates in one
    unit.
  - #101's own classes need the new Program, V = 128,256 and S = 32 (next point).
- **#101's Program has to be rebuilt.** The request Program's digest moves from #197's `79caee21…`, and its 32 selects become
  `GumbelTopPTokenSelect_v2{V=128256,S=32}`.
  - The value needs a rerun of the #101 Build on a pod, as #197 did. This VM has no pod access; the vLLM coordinator plans that pod.
  - Its program graph (for `Q_word`'s classes and the export) comes from that Build.
- **Cutting the sampler Call (decision, Sep 28: no separate root Calls during the re-baseline).** `Q_word` flattens a non-separable
  Call at about 0.6 KB of host memory per gate, and the sampler Call is 102,382,746 word gates: **about 60 GB**. Measured at
  V = 16,384: 16.4 M gates, 9.6 GB, 201 s.
  - The default `max_gates` of 24 M refuses it as `too-large`. Raise it for that Call only, per run:
    `--word-max-gates GumbelTopPTokenSelect_v2=110000000` on `verity-vllm manifest build` / `build-global` (with `--word-check`) and
    `program-graph` (with `--word`), or `VERITY_QWORD_MAX_GATES` with the same value. `N` alone raises every Definition's limit.
  - The query's digest doesn't move: the limit is outside `query_id`.
  - `class_statement --partition q-word` cuts through core's `partition_object`, which has no gate limit; the memory need is the
    same.
- **To benchmark classes without #101's Build:** `bind(topp_words.TopPKeepWord, V=V, S=32)` and
  `verity_vllm.query.word.unit_rule(fn, 16, 32, max_gates=...)` give the classes at any V.
