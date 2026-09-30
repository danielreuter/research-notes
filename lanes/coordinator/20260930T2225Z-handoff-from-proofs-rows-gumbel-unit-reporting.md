---
id: 20260930T2225Z-handoff-from-proofs-rows-gumbel-unit-reporting
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-rows (bc-25950a06), worker of @proofs (bc-8416bc72)
---

# @old-research-coordinator: (a)'s summary.json can report the Gumbel top-p unit on its own; recipe for sweep2-feed

**Why:** the old vLLM coordinator's condition (`lanes/vllm-coverage-defs/20260930T1020Z-decision-from-vllm-coordinator-topp-option3-and-queue.md`).
The top-p sampler Call is one unit, not provable in practice. Today `MODE=sampled` drops it without a word: `class_statement --select`
leaves out every Call matching `class_sweep.SAMPLER`. So a deployment's summary never says a unit is missing.

**What `lanes/proofs-rows/tools/73-sweep-shape.sh` adds, in `MODE=sampled` only**, beside the existing totals:
- `sampled_units`: the draw's picks from `picks.json`, one Call each.
- `units_proved`: picks whose Definition had every shape proved and accepted.
- `units_not_proved`: counts by Definition, for the rest.
- `units_excluded`: each pick the sweep leaves out, with `definition`, `spec`, `request_id`, `step`, `op_path` and `why`.
  - `GumbelTopPTokenSelect*`: "`<name>`: not provable in practice (the top-p sampler Call is one unit over the whole vocabulary
    row)".
  - Any other sampler: "`<name>`: left out by the sweep (--select drops the token-select Calls), not attempted".
- `fully_provable`: true only when every unit was proved.

The map from Definition to shapes is `$SWEEP/sampled/<slug>/counts.json`: `class_statement --counts-only` over the same `defs.json`
and `--select`. `MODE=sampled-stage` writes it (26 s of CPU for 52 Definitions). A prove job whose stage came before this writes it
itself, inside its GPU job.

**Tested** on the b8 top-p deployment's own `defs.json` and `picks.json` (node 1, read only), with synthetic prove results:
- 460 units: 458 proved, 1 not proved, and 1 excluded, the `GumbelTopPTokenSelectSharedGreedy_v1{V=128256}` pick (r4, step 28,
  `runner.sampler`).
- The one unproved unit is on purpose: the test marked one Attention shape unproved.
- `fully_provable: false`.
- `MODE=shape` summaries are unchanged.
- It hasn't run in a GPU job: Daniel's rule allows no proving beyond the one split chunk.

**What the three deployments already drawn under `/workspace/jobs/sweep2/sampled/` show** (read only):
- **greedy b1:** the draw picks `TokenSelect_v1` once. The sweep drops that too, so `fully_provable` is false with "left out by the
  sweep, not attempted". If TokenSelect is provable, the fix is to stop dropping it in `MODE=sampled`. That's class_statement's
  `SAMPLER` exclusion, backend-sweep-2's code, so it's your call.
- **top-p b1:** no sampler pick in its 460, so it can be fully provable.
- **top-p b8:** one Gumbel pick, excluded as above.

So whether a top-p deployment shows the Gumbel unit depends on its draw, not on top-p alone.

**Adoption in `sweep_feed.py` `sampled()`:**
1. Run the (a) items' `MODE=sampled-stage` and `MODE=sampled` through the copy, or port its two blocks into your 73: the
   `counts.json` step and the `MODE=sampled` part of SUMMARY.
2. Add `sampled_units`, `units_proved`, `units_excluded` and `fully_provable` to `st["first"]`, and to whatever reads the 17 top-p
   deployments after the gate deployment.
