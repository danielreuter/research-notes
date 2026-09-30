---
id: 20260930T1436Z-merge-request-build-v2-kv-517
campaign: overnight-sep30
lane: coordinator
kind: merge-request
status: superseded
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507)
---

**Superseded 16:15Z:** #517 is in `research queue` (ready at `872be036`, `main` 6a815cc7 merged), waiting only for the
`vllm-coordinator` grant (`note:20260930T1615Z-handoff-from-build-v2-kv-grant-517`). Nothing to do here.

# Merge request: #517, key/value references shared as a prefix (Build plan change 3), at `a309b142`

- **PR:** [#517](https://github.com/danielreuter/verity/pull/517), branch `cursor/build-v2-kv-prefix-d717` at **`a309b142`**, with `main`
  1c10b00c merged in.
- **Touches:**
  - core `verity.ir`: `refs.py` (`PartLog`, `prefix_runs`, `Concat.slice` bisect), `codec.py` and `liveness.py`;
  - `integrations/vllm`: the attention rule, derive, emit, workload, manifest, and a new torch-free `program/replay.py`.
- **Doesn't touch:** circuits, Lean or `backends/flock/`, so no `lean-agreement` and no statement reviewer.

**What it does.** Call `t` of an attention layer used to rebuild its `t`-row key/value reference sequence, and every later pass walked
all `t` parts again. That is `O(L²)` parts per layer. Now the rows are one append-only `PartLog` per layer, and each pass does the shared
prefix once. The change is representational only: the Program, descriptor, workload Program, manifest and correspondence bytes are
unchanged.

**Evidence** (vy-nebius-1, serial derives, no rule cache). Every row is byte-identical: workload, manifest, component and correspondence
digests, and gate counts.

| Row | Build wall, tip vs `main`, same time on 16 vCPU each | Peak RSS GiB, tip vs `main` |
|---|---|---|
| llama32-1b prefill B8 I512 | 384 vs 509 s (0.75×) | 2.57 vs 3.77 |
| mistral-7b prefill B8 I512 | 520 vs 833 s (0.62×) | 3.70 vs 6.43 |
| llama32-1b B8 I1024 O128, the Build owner's 28-min target | 1480 vs 2231 s (0.66×) | 6.40 vs 11.93 |

- **Runs:** post-merge `r20260930-133103-9fef` (tip) against `r20260930-133041-d53d` (`main`), and pre-merge
  `r20260930-092548-94d4`. The post-merge runs end rc 3 only because the 1k row had no row in the six-row baseline, a harness
  bug that is now fixed. Their digests match.
- **Dashboard:** attempts 0 and 1 on line `build-v2` are labelled (`r20260930-072938-7ebd`, `r20260930-095541-fa3e`, every
  `ov.gate=pass`).
- **Tests on the merged tree:**
  - vLLM lint: 43 passed;
  - vLLM `program`, `observe` and `correspondence` plus the tree-wide import checks, without slow tests: 1,665 passed;
  - core `ir`, `evaluation` and boundaries: 306 passed.
  - Slow tests are left to `check`.
- **Fixed on the branch:** P10 failed on the branch alone. `derive.py` and the fold kept verbatim copies of one replayer, and both now
  import `program/replay.py`.

**Ask:** please put #517 in the next train. It merges cleanly onto `main` be3149a1 (14:36Z), and vLLM lint passes on that merge.
