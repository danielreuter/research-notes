---
id: vllm-coordinator/20260927T0915Z-handoff-from-coordinator
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: research-notes
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Correction (supersedes my 07:00Z and 09:05Z notes): private material goes in the store's `private/`, never under `internal/`

**To:** vllm-coordinator. **From:** coordinator, on the root's instruction (09:15Z). Lane contract 2.2, §5b.

- **My earlier notes were wrong to say "the store (`internal/...`)" and `internal/red-team-reviews/<pr>/`.** A mirror pass at 08:44Z
  copied top-level `internal/` files to the public notes repo, so `internal/` is not a safe place.
- **Private material** (red-team reviews with exploits against unmerged code, attack scripts and their runs, reproductions,
  private soundness details, an unfixed bug) goes in the store's top-level `private/` (for example
  `private/red-team-reviews/<pr>/`) or in the evidence store (`research data put`, labels). **Nothing sensitive anywhere under
  `internal/`.**
- Lane folders and handoffs carry only the verdict and a pointer to the private path.
- **Already done:** the mirror now forwards only `internal/lanes/`, and never reads `private/`. The mirrored files were removed from
  notes HEAD (`c7706ce4`). History is Daniel's call.
