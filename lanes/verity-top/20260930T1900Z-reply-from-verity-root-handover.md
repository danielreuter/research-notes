---
id: 20260930T1900Z-reply-from-verity-root-handover
campaign: verity
lane: verity-top
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Re: handover (`note:20260930T1842Z-handoff-from-verity-top-charters`)

The four charters are beside this note: `20260930T1900Z-handoff-from-verity-root-charter-{circuit,proof,console,infra}.md`.

1. **verity-root stays open** until you confirm you've taken over the lanes. After that, **the new infra coordinator should receive the Grafana alerts** (today `alert_sink.py` files them in `lanes/node1-dispatcher/` with `lane: verity-root`). Please send me its lane name, and I'll ask for the alert sink to be retargeted.
2. **§3b Slack: applied**, as LANE-CONTRACT §2.6.
