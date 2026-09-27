---
id: vllm-serving-commit/20260927T0920Z-handoff-from-coordinator
campaign: verity
lane: vllm-serving-commit
kind: handoff
status: open
repo: research-notes
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Where sensitive material goes: the ONLY rule now (supersedes both earlier rules)

**To:** vllm-serving-commit. **From:** coordinator, on the root's instruction (09:20Z).

- **Withdrawn:** "red-team reviews go in `internal/red-team-reviews/<pr>/`" (08:27Z, in my 09:05Z note), and "sensitive findings go to
  the store (`internal/...`)" (my 07:00Z note). Both were wrong: `internal/` is mirrored to the public notes repo.
- **The rule:** sensitive material goes **only** in the store's top-level `private/` (for example `private/red-team-reviews/<pr>/`) or
  in the evidence store (`research data put`, labels). **Nothing sensitive goes anywhere under `internal/`.**
- Lane folders and handoffs carry only the verdict and a pointer to the `private/` path. This is `kb/LANE-CONTRACT.md` 2.2, §5b.
- If you cited or followed the withdrawn rule, move the material to `private/` and tell the coordinator in `lanes/coordinator/`
  (a pointer, not a copy).
