---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
lane: coordinator
kind: handoff
from: flock-zk (bc-2a9978cc)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T08:32Z
---

# Merge request: #265 (a coin-tree server with no OS random source refuses Hello), after #258

This is the follow-up promised in `20260928T0827Z-merge-request-flock-zk-258.md`. The merge order is #229, #252, #258,
then this PR.

- **The PR:** [#265](https://github.com/danielreuter/verity/pull/265), branch `cursor/flock-zk-coin-server-refusal-5659`,
  head **`21689ff5339108e390b0fe0bf89b04c5a61690ac`**. It is stacked on #258 at `1053c0c9`, so retarget it to `main` once
  #258 is in. It's a draft; I'll mark it ready if the red team is content, or you can merge it as is.
- **Contents:** the red team's non-blocking note 1 on #258 (`private/red-team-reviews/zk-proofs/pr258-coin-tree-v2-impl.md`).
  - A server configured with a coin tree but with no OS random source now refuses `Hello` itself. Before, it answered
    `Ok`, and the prover then failed closed.
  - Replaying a record is exempt, because a replay reads the recorded key and coins instead of drawing them.
  - This is one field and one check in `backends/flock/live/src/lib.rs`, plus a unit test.
  - No statement, pin or transcript bytes change.
- **Evidence:**
  - `flock-live` units: 51 passed, including the new
    `coin_server_tests::a_coin_tree_server_answers_hello_once_and_refuses_without_an_os_source`.
  - The zk selftest cases `record_replays_offline`, `honest` and `zk_verifier_coin_off_its_commitment` pass.
  - CPU only: no pod.
