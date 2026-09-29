---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: note for the README drafter (bc-00f2c5c0), #337's owner (relayed by Daniel or root) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T08:43Z

# #337: a ready head to push, `903c60c6` (it fast-forwards `c39292ac`)

**The bundle:** `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/artifacts/pr337-903c60c6.bundle`, ref `refs/heads/pr337-rebased`, sha256 `e275e279…`. It needs main `180f8771` and `c39292ac`.

**Push it:** `git fetch <bundle> pr337-rebased && git push origin FETCH_HEAD:cursor/gate-vllm-suite-f880`. It's a fast-forward.

**The two commits on top of `c39292ac`:**
1. **`26944a5d`:** merges main `180f8771`. The one conflict, in `tools/check/check.py`, is resolved as main's Lean-ordered groups (`AFTER_LEAN`, `lean-suites`) without `"--skip", "verity-vllm"`, since gating the vLLM suite is #337's purpose.
2. **`903c60c6`:**
   - `integrations/vllm/tests/conftest.py` `KNOWN_FAILURES` gains the CPU check pod's 29 failures on main, each with its cause and owner (the 02:27Z triage classes A–F, plus the `test_twins` evidence-schema test);
   - `integrations/vllm/pyproject.toml` `[tool.verity.tests] inputs` gains `.gitignore`.

**Verified:** on a `git archive` export (no `.git`, like the check pod), with CPU torch:
- the whole vLLM suite has 0 unexpected failures;
- `tools/check/tests` gives 34 passed.
