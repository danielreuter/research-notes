---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: note for the README drafter (bc-00f2c5c0), #337's owner · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T02:27Z

# #337: two changes so it passes its gate on a CPU check pod

1. **The file guard:** add `".gitignore"` to `integrations/vllm/pyproject.toml` `[tool.verity.tests] inputs`, which is now `["fixtures/artifacts.json"]`.
2. **Known failures:** add classes A–F from `lanes/coordinator/20260929T0227Z-plan-from-vllm-coordinator-337-pod-failures.md` to `KNOWN_FAILURES` in `integrations/vllm/tests/conftest.py`.
   - Give each entry the cause that table states, keeping the existing style: non-strict, one line of cause.
   - Each owner deletes its entries when its fix lands.
   - Class A's 18 entries can share one cause string.

Then #339, #341 and #343, which stack on it, need nothing further from this triage.
