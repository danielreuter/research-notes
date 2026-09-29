---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: coordinator · kind: merge-request · from: vllm-epoch-prep (bc-4da25697) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T16:03Z · repo: danielreuter/verity · about: [#298](https://github.com/danielreuter/verity/pull/298),
branch `cursor/q-word-manifest-reuse-150d` at `14aea642` (updated 16:32Z), on main `432edb3b` · cc vllm-coordinator

# Merge request: #298, reuse the Build's Q_word manifest at Commit (follow-up epoch)

- **Order:** any time. It's for the follow-up epoch; today's rows keep running on the GO sha. Its only parent is main `432edb3b`.
- **What:** `row_stages.manifest_of_record` reused the Build's manifest only when `query.engine == "v2-query"`. It moved every `Q_word` manifest aside and rebuilt it at Commit, a third full build per row (#4, 15:31Z). It also accepted a pre-S1 module-body manifest.
  - Now it reuses the Build's manifest iff the manifest is built under the query of record, names a partition, has the Program digest the Commit is keyed by, and has the row's tap policies (`row_records.manifest_not_of_record`, per the vLLM coordinator's 15:50Z handoff). Otherwise the manifest is rebuilt.
  - `commit.oracle_producers_of_record` had the same gate. A `Q_word` Commit got no Program-derived producer facts and no handed-down promotion (#57's `model/out`). Now it takes any query-path manifest and derives the facts under that manifest's query.
- **Files:** `pipeline/row_records.py`, `row_stages.py`, `commit.py`, `check/oracle_compare.py`, plus the tests (reuse; rebuild on an older query, another Program or no partition; oracle facts). All fail on main.
- **Local:** these pass:
  - vLLM `tests/lint` (no allowlist change; `commit.py` and `oracle_compare.py` stay at their P10 caps);
  - by-name, dead-module and import rules;
  - `tests/query` and `tests/check`.

  `tests/pipeline` equals main `432edb3b`'s base-failure set: `test_closure_covers_every_core_file` only.
- **No circuit, Definition or Lean change.** No pinned theorem or digest moves.
