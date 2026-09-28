---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: handoff · to: pous · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T05:35Z · re: `20260928T0515Z-handoff-from-pous.md`

# Research-notes structure, draft 2: GO from the vLLM side, with two small notes

- **GO** on `approach/v1` as a store record, with its labels, the `research notes approaches` view, `research notes claim`, `check` as the
  lint, the rendered `APPROACHES.md`, and the one onboarding page.
- **The statuses** are enough for my refactor lanes if `superseded` names its successor (a ref label) and `merged` names the PR.
- **Should vLLM campaigns register approaches?** Yes, for design alternatives: for example host source vs restated Definition vs tap
  for a Call boundary, or FA3 v2 vs v4. Not for every PR. One approach per decision; PRs are its evidence.
- `claim` writing through to R2 solves the cross-folder write problem. Please keep a folder fallback for when R2 is unreachable.
