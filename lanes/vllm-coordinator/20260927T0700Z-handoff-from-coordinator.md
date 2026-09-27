---
id: vllm-coordinator/20260927T0700Z-handoff-from-coordinator
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: research-notes
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# The research-notes repo is public: no secrets or sensitive findings in notes

**To:** vllm-coordinator. **From:** coordinator, on the root's instruction (07:00Z). Daniel has been told.

- **`danielreuter/research-notes` is public.** Anyone can read every report, checkpoint and handoff in it.
- **No secrets there:** no tokens, keys, credentials, private URLs or account details.
- **No sensitive findings there:** an exploitable soundness bug before its fix is merged, a red-team attack on unmerged code, or
  anything else that would help an attacker. Write those under the store (`internal/...`), and put only a one-line pointer in
  notes ("finding in the store: internal/<path>").
- **The same rule covers the store's lane folders.** The mirror forwards `internal/lanes/` (handoffs and cloud lanes' reports) to
  the notes repo, so a handoff you write there becomes public too.
- **If something sensitive is already in notes,** tell the coordinator in `lanes/coordinator/` with a pointer, not a copy.
