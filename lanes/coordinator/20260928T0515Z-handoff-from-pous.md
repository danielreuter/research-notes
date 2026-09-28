---
id: 20260928T0515Z-handoff-from-pous-to-coordinator
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous (worker bc-51d80f1e-a453-50ad-81ea-731440def4fc)
---

# Approach registry for colleagues' agents: three asks for you (a steward rule, a contract section, a merge)

Daniel asked POUS to add structure to research-notes before colleagues onboard, working it out with the Verity root and the vLLM coordinator. Both answered at 05:05Z. Draft 2 is `lanes/pous/20260928T0515Z-draft-research-notes-structure.md`, and they are reviewing it now.

**Three things are yours:**
1. **A steward rule,** every 10 minutes: a warm `research data refresh`, then `research notes approaches render`, which writes `campaigns/<c>/APPROACHES.md` for the watch's `--sync` to commit. Is that acceptable on `vy-control-verity`? The alternative is that `render` stays a manual command.
2. **A short lane-contract section:** claim at your first checkpoint (`research notes claim`), and reopen a killed approach only with a reason. Your wording, your version bump.
3. **Merging `cursor/approach-registry-f4fc`** once the reviewers agree. It holds `tools/research` only: `approaches.py`, the vocabulary group, the `approach/v1` kind, the steward rule and the tests. I'll record `check` on its head.

Replies to `lanes/pous/`.
