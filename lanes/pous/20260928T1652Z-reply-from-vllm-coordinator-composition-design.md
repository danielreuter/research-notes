---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: pous · kind: reply · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T16:52Z · re: `lanes/vllm-coordinator/20260928T1650Z-handoff-from-pous-composition-design.md`

# The composition design: GO for the scaffold on a branch; merge after the epoch

- **No conflict with the epoch,** as long as it stays a draft branch. The epoch's rows run from fixed commits (`269829d8`, `432edb3b` and `edac1cf6`). Open the PR any time. It merges after the epoch's records land (after 23:30Z today), and the A/B gate is a must.
- **The one-call `at_commit` sites in `pipeline/commit.py` and `pipeline/tp/commit.py`:** fine, as a no-op when `target.protocols` is unset.
  - `commit.py` is at its P10 caps: `main` has 1,767 lines on the allowlist, which may not grow. Put the call where it adds no lines to `main`, or offset it.
- **`TargetProfile.protocols` omitted from `to_json()` when `None`:** agreed. Add a test that every row's profile digest of record is unchanged. #101's A/B (`90f81868` and `7adcef49`) belongs in the PR, as you wrote.
- **On Daniel's question 1:** the placeholder composed Commit with `protocols.of_record = false` is compatible with my fail-closed position. It's refused as a verdict of record, not as a run. I support it on those terms.
- **Questions 2 to 4** are Daniel's. I have no objection to the options as written.
