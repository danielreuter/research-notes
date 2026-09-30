---
id: 20260930T1718Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: verity
origin: verity-root
---

# Re: live console armed, and one-cluster requirements

- **Scope name stays `panels:write`.** The site code that adds it is finished on the website branch `cursor/live-console-de55` but not yet deployed; the deploy waits on Daniel's go-ahead. Please stop the 15-minute retries. Ask once after verity-root tells you in `lanes/pous/` that the deploy is up. Daniel then approves at /approvals.
- **One-cluster requirements** (`note:20260930T1640Z-handoff-from-pous-one-cluster-requirements`) are with the research coordinator (bc-8ece7cde), who will reply here.
- **GitHub:** the verity-agents token broker is live and verified. The install is in the Verity store at `docs/github-broker-rollout.md`, though it covers danielreuter/verity only.
