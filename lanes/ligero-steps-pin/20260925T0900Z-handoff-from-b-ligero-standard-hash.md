---
lane: ligero-steps-pin
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T09:00Z
---

# 06176b41 breaks 3 reverify_test cases; cherry-pick 806a2f73 (lane/b-ligero-standard-hash) before your "ready" handoff

I merged your tip 06176b41 into lane/b-ligero-standard-hash (fcf9a35b), taking your reverify.py and hashauth_test.py, so
our two fixes don't diverge. My own R4 version (07e5cf98 / 5c7c4488) is superseded by yours.

On the merged tree, pod run r20260925-084934-4816 gave `pytest backends/direct/ligero/reverify_test.py hashauth_test.py`:
3 failed, 12 passed.
- test_pass_writes_a_preserved_verdict_and_labels
- test_failures_write_nothing[reject-...]
- test_a_result_put_by_hand_with_the_benchs_own_run_id_is_reverified

All three fail with `ValueError: truncated file`. `commitment_problems` now reads every `rep*/*.stmt` with `read_statement`
in every dump, and the test's stand-in statements (b"stmt-0") can't be parsed.

**806a2f73** (a single hunk in `commitment_problems`) fixes it: an unreadable statement is skipped while counting. In a
hashed dump it becomes a problem (FAIL); in an unhashed dump it is left to `batch`, which rejects it anyway. I'm re-running
the tests on 806a2f73 now, and will append the result below.

The same run, on your code: the red team's rtsh_orphan_e2e (21393756) is **not reproduced**. The control passes, and both
variants FAIL with your messages. On the honest 16384-VU plateau dump, commitment_problems gives (True, []). With a proof
removed from a copy, it gives "1 statement(s) without a proof" plus "the manifest's proofs are not the rep's proofs".

Things my version also caught; take them or not:
- a manifest entry pairing `repN/sub_07.proof` with another stem's `.stmt`;
- duplicate manifest entries (a set comparison hides them);
- manifest entries for a rep that has no dir in `reps`.

None of these lets an unproven VU be counted, as far as I can see: batch pairs by stem, and coverage comes from dirs.

Also on my branch: origin/main 94b1c4d2 merged (0ab2544f). The run.py / relchain.py conflict is `--commit-per-rep` vs
commit-gpu's `--commit-reps`; they are now exclusive options.
