---
id: 20260929T0640Z-handoff-from-pous-367-and-flaky-guard-test
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: PoUW circuit gate #367; a hanging `tools/research` test; #315 not in T1

- **[#367](https://github.com/danielreuter/verity/pull/367) (draft):** the vLLM gate now admits "PoUW + sampled proofs" for `ncp-v2` only, asking `verity_pouw.circuit` rather than the adapter. Every other scheme is refused with exactly the old message.
  - It's based on `main` `e1ac9466` (#311 and #312) with #364 merged in, plus one commit, `79241b7d`. #364 merges first.
  - vLLM tests passed under torch 2.14 (`r20260929-052814-83aa`). `check` `r20260929-063330-7377` passed, but every step came from cache; see the next item.
  - A run can't be of record until #315's adapter executes `ncp-v2` through the circuit. That work is now a stacked draft in progress. Until then, a `pouw:ncp-v2` Commit fails closed.
- **A test in `tools/research` hangs, for its owner:** `tools/research/tests/test_budgets_guard.py::test_the_cli_refuses_unreadable_budgets_a_second_guard_and_status_stop_read_the_recorded_pid`.
  - In fresh run `r20260929-052903-241e` it missed its helper process and started a real budget-guard loop that never ends. The suite has no timeout, so it hung for about 40 minutes until it was killed.
  - No pods were touched, because the suite runs without the RunPod key. It passed at 01:46Z, and the `research` suite then passed on its own (530 passed), so it's flaky rather than broken.
  - It could use a per-test timeout, and a guard that refuses to loop when it has no key.
- **#315:** T1 took #311 and #312, but not #315 (`109e12f6`, full recorded check passed, merge-ready after #312). Is it queued for the next train, or does it need anything from us?
