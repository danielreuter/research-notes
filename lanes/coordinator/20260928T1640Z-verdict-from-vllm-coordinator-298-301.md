---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: verdict · to: research coordinator (bc-8ece7cde) · created: 2026-09-28T16:40Z

# #298 (`14aea642`) and #301 (`4477061a`): both APPROVED for train D

**Base:** both are based on main `432edb3b`. #301 already merges #298's head, so merging #301 alone brings both.

**#298: the `manifest_of_record` fix,** the one root routed at 15:50Z.
- Commit reuses the Build's manifest when it's built under the query of record, `Q_word`, not only when it says v2-query.
- It also requires that the manifest names a partition and is of the Build's Program digest.
- Changes: `row_stages`, `row_records`, `commit` and `oracle_compare`, with tests in `test_row` and `test_oracle_compare_v2_producers`.

**#301 adds `query.word_check`:** the strict word check's record, written to the manifest header by `manifest.word_record`, and composed per component or rank in `compose._with_partitions`.
- The Commit refuses a `Q_word` manifest without it (`commit.partition`), and `tp/commit` now calls `require_partition`.
- **Digest check:** `manifest_digest` (`query/manifest/format.manifest_digest`) hashes the identities only, and the header isn't among them. So no manifest or rows digest moves, and no record moves.

**Tests,** run on each head:
- `tests/pipeline/test_row.py`, `tests/check/test_oracle_compare_v2_producers.py`, `tests/commit` and `tests/query/test_word.py`: rc 0.
- The vLLM lint suite P01–P12 and `test_no_by_name_rules.py`: rc 0.

**One consequence for the follow-up epoch:** after #301, a stored Build's manifest from before #301 has no `query.word_check`, so its Commit refuses it. That includes today's side-stored Builds. The manifest has to be rebuilt once under the strict check before Commit; #298 then reuses it. That's the intended behaviour. Today's running rows (#4, #73, #23) run on `269829d8` code and aren't affected.
