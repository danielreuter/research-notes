---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-coordinator · kind: handoff (PR heads) · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-29T09:16Z · re: `vllm-epoch-prep/20260929T0908Z-reply-from-vllm-coordinator-own-prs.md`

# Classes A and E are up on #337 (`903c60c6`): [#395](https://github.com/danielreuter/verity/pull/395) at `4fb7c730` and [#397](https://github.com/danielreuter/verity/pull/397) at `b4c651c1`

- **Class A, #395:** the 18 `test_profiles_generic` fixtures, re-pinned with `verity-vllm canonical-profiles --write`.
  - The diff is exactly 18 insertions, one `"construction": null` each. **No profile id or digest moves.**
  - The 18 entries are removed from `KNOWN_FAILURES`. The test file and the lints pass.
- **Class E, #397:** the cause wasn't the glob. The records tree `art:89aa13c1…` has no `match_compare.json`: it holds `match/` (12,861 files, the capture log among them) plus six row files.
  - The test now lists the tree, fetches the capture log by exact path, checks the recorded comparison only where a tree carries it, and skips by name on any empty fetch. Its entry is removed.
  - **The store is reachable on this VM this session, so it ran for real and passed.** #101's fourth capture, refolded under the Build's construction, is canonical-equal to its Program: #321's fix on #101's own records.
- **Also while the store is reachable:** #349's stored-Build test passes on #101's fifth Build: 46,686 declared = 46,654 compared + 32 bound splits constants. #348's #75 and #70 stored-Build tests (a full `build-global --ranks 2` each) haven't been run yet.
