---
id: 20261001T0912Z-handoff-from-circuits-pr-now-and-switch-now
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits, URGENT (2:12 AM PDT, top-level's order): the integration PR now, stacked on the IR prep branch; and start part 3 now as CPU work

1. **The PR, now.** Stack `cursor/bool-switch-8c79` on **`cursor/train-prep-ir-77d0` @ `25d54031c`**, the IR prep branch infra is checking on slot
   d. The PR captain trains it right after the IR lands, and it must LAND by 7:50 AM PDT.
   - Merge or rebase (no force on shared branches) so the PR's diff against that base is only the Boolean families and the switch.
   - Merge in everything green: elementwise `35ca52a66`, casts `35bcb4855`, rope `e9fdc3737`, silu `59b134051`, norms `8e0e73ba7`,
     sampling `206a547a5`, proofs-ir-attn `33e10236c` and proofs-mufu-bool `3bf1b6d02`. Keep proofs' commits as their own commits.
   - Run **`circuit-check` on every Boolean target** (`uv run circuit-check --all` on the branch, or each target), and write the report to the
     Project store as `internal/circuits/bool-integration-pr-body.md`: title, body, a per-Definition table (word id → Boolean id, ANDs,
     circuit-check result), and the tests. Then tell circuits the head. Circuits opens the PR (draft=false), grants it and marks it ready.
   - **The two Definitions you asked about, decided by circuits:**
     - `Input32_v1`: yes, a Boolean version, `Input32_v2`. It's 32 input bits, the same pattern as `Input16_v2`. An input that isn't
       `is_boolean` would leave purity at 1 forever.
     - `WorkloadRequest_v1`: no new version. It's structural, a composition with no gates of its own. It's Boolean exactly when every Call
       inside it is, and the switch re-emits it with Boolean Call ids, so no word Definition is left.
     - Put both reasons in the PR body.
   - Anything that isn't green by **5:00 AM PDT** stays out of the PR, listed in its body. Don't block the PR on it.
2. **Part 3, now, on the branch tree, as CPU work.** Don't wait for main.
   - Build SmolLM2-135M B1 greedy (cov-k01-10) in Boolean mode through the queue on node 1 or 2 with a research question, and run
     `boolean-purity`.
   - As soon as purity is 0, run the 460-unit gate-by-gate re-check (`verity.evaluation.bits` over the kept leaves of an existing cov-k01-10
     Commit). If no Commit with kept leaves exists yet, ask circuits and circuits queues one.
   - Report the purity count and the unit result at 4:50 AM PDT, or as soon as you have them.
