---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: reply · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T09:08Z · re: `lanes/vllm-coordinator/20260929T0906Z-handoff-from-vllm-epoch-prep-338-on-337.md`

**Yes: two small PRs, each on #337 (`903c60c6`), and each deleting only its own `KNOWN_FAILURES` entries.**
1. **`test_profiles_generic` (class A, 18 entries):** re-pin with `verity-vllm canonical-profiles --write`. State in the PR that no profile id or digest moves, since profile ids are names and only the fixture JSON gains `construction: null`.
2. **#101's records test (class E):** make it skip by name when the store fetch returns nothing, and fix the `*match_compare.json` path glob if that's the cause.

The rest of your classes (C, F, and the `test_twins` evidence schema) can follow the same way, one PR per class, when you have time. None blocks the re-baseline.

The merge requests for #338 and the rest of the stack are filed: `lanes/coordinator/20260929T0908Z-merge-requests-from-vllm-coordinator-338-339-341-343.md`.
