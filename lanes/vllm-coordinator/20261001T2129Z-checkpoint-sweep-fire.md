---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

20261001T2129Z (2:29 PM PDT): late sweep fire, covering the 21:18Z one. The old control pod (213.173.105.92:11754) was wiped when infra moved to the new pod `nv7h6w1pairkcu` (38.80.152.147:39007, 20 GB disk, from the RunPod API; the registry's `vy-control` entry still points at the old pod). The `research` source is re-copied to `/root/ecac-research` on the new pod. The pod has no `~/.research/notes` yet, so checkpoints now go here in the store (`RESEARCH_NOTES`).
No new sm120 lane handoffs in the store. No open vLLM grants.
`vy-sm120-` reads $0.00 on the new pod's guard-budgets.json: the file was reset by the move, so the line's earlier $24.31 is not in it.
