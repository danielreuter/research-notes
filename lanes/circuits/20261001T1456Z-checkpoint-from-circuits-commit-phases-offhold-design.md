---
cursor:
  subagentId: "bc-2840854d-2bab-5494-9ec4-56acb28b827a"
---

lane: circuits-commit-phases · kind: checkpoint · to: @circuits · created: 2026-10-01T14:56Z

**Off-hold design (7:56 AM PDT).** The warm-up's host evaluation can leave the GPU hold now, with no root question. The record pass's
evaluation can't leave it without a ruling, because its words are leaves of the run root. Prototype for the warm-up:
`cursor/commit-boundary-offhold-8c79` @ `fd6b22332`. Goldens next.

**Where the hold goes.** The Gemma-2-2B B1 golden (`cov-cg04-cbp-after`) has a 516 s Commit:

| Phase | Time |
| --- | --- |
| Engine build | 201 s |
| Committer setup | 42.5 s |
| Weight registration | 38.9 s |
| Instrumented warm-up | 126.1 s |
| Control arm | 1.8 s |
| Instrumented pass | 122.2 s |
| Checks after finalize | about 7 s |

Both instrumented passes are almost all the logits-processor body's `dense_rows` chain: the exact `lm_head` emulation, 256,000 × 2,304
weight words per row, one row per step over 33 steps.

**What the root binds.** The call-boundary source acquires every target into its step (`committer._acquire`). So its words are chunk
leaves under the step roots, and the run root is folded at `com.finalize()` inside the GPU task. Every draw comes after that fold: the
64 openings, the population picks, the after-release openings, and the replay seed.

**Why the record pass can't just move.** An unchanged root that is fixed before release needs these words before release. Evaluating
them after release leaves two options:
- fold the root after release, so it depends on post-release values;
- bind something other than these words, which gives a different root.

So capturing the inputs and evaluating later can't satisfy both the same-root goldens and the constraint for the record pass.

**The warm-up already doesn't touch the root.** Its root is discarded (`com.reset()`), nothing draws from it, and its words reach no
bundle or check. It exists to size the pinned pool and learn the bounded-staging plans, which read the tensors' names, shapes and dtypes,
not their words.
- **Prototype A:** around the warm-up, `taps.warmup(com, on)` sets bounded staging's `learn_only` as before, plus the source's
  `placeholder`. With `placeholder` set, each target is committed as zero words of its shape. Operand shapes are still checked, and
  nothing is evaluated.
- **Effect on the record pass:** none, so the root, binding, seed and verdict match by construction.
- **Expected saving:** about 120 s of the 516 s. One-time costs move into the pass: weight fields to host, the `lm_head` W-side
  preparation, and the step-shared cache.
- **Size:** `commit.py` is net zero lines (P10). There is a new unit test: zero words of the record's names, shapes and dtypes for
  packed, per-request and step-shared bodies, no template evaluated, and the IR's words once the flag is off.

**For the record pass, two routes. Both need your ruling:**
1. **Bind the served logits.** vLLM's logits processor already holds the `lm_head` output on the GPU. Tap it as a claim (`CLAIMS`, like
   the pre-bias GEMM taps), commit it, and let the deferred replay check the sampled `lm_head` Calls, as it does for any served GEMM.
   - The root binds only words acquired before release.
   - It stays unchanged only if the served words equal the Program's at every coordinate. With M = 1, cuBLAS may not run the k16 chain.
   - Test first with one debug row that compares the served logits to the committed words, before any protocol change.
2. **Fold the root after release.** The GPU task dumps the store and the captured operands, then releases. A CPU task evaluates the
   words, rehashes the affected chunks and trees (chunk-leaf-v1), folds the same root, and only then runs every post-finalize check and
   draw.
   - No draw comes before the root.
   - But the root does depend on post-release values, which needs the advisor's ruling.
   - It moves `finalize` and every check after it out of the GPU process.

**Recommendation:** land A. For the record pass, take route 1 if the debug row shows equal words; otherwise route 2, with a ruling.
