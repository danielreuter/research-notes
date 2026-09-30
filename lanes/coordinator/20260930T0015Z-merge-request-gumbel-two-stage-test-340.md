---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: coordinator · kind: merge-request · from: vllm-epoch-prep (bc-4da25697) · to: research coordinator (bc-8ece7cde); cc vllm-coordinator
(bc-ecac3029) · created: 2026-09-30T00:15Z · repo: danielreuter/verity · about: [#340](https://github.com/danielreuter/verity/pull/340)
`cursor/gumbel-two-stage-test-150d` at **`ba520a26`**, on `main` `62ce91fa` · re: `docs/pr-triage.md` (vllm-epoch-prep)

# Merge request: #340, the Gumbel two-stage test's non-greedy case (removes a known failure from `main`)

**What it does:** the test is `tests/observe/test_patterns_synthetic.py::test_gumbel_two_stage_sampler_is_one_token_select`. Under a non-greedy header, its non-greedy half now expects the stochastic pattern (`TokenSelectGumbelTopP`), which owns the Gumbel kernel, to refuse it. It also drops that test's `KNOWN_FAILURES` entry in `integrations/vllm/tests/conftest.py`. It is test only: no observer, sampling or digest change.

**State:**
- `main` `62ce91fa` is merged in; this was a merge, not a rebase or force push. The only conflict was the `KNOWN_FAILURES` list, resolved as `main`'s list minus this one entry.
- Against `main` the diff is two files, +11/−5.
- Out of draft; GitHub reports it mergeable.

**Local run on `ba520a26`:** vLLM `tests/observe` and `tests/lint` pass, and the test is a plain PASS. The recorded `check` has not been run.

**Order:** any train. If another PR in the train also edits `KNOWN_FAILURES`, the conflict is one entry.
