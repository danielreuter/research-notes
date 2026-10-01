---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# vLLM coordinator: hourly sweep checkpoints

One line per sm_120 sweep fire, newest last.

- 20261001T2129Z (2:29 PM PDT): late sweep fire, covering the 21:18Z one. The old control pod (213.173.105.92:11754) was wiped when infra moved to the new pod `nv7h6w1pairkcu` (38.80.152.147:39007, 20 GB disk, from the RunPod API; the registry's `vy-control` entry still points at the old pod). The `research` source is re-copied to `/root/ecac-research` on the new pod. Checkpoints now go here in the store (`RESEARCH_NOTES`). No new sm120 lane handoffs, no open vLLM grants. `vy-sm120-` read $0.00 on the new pod: the move reset the file, so the earlier $24.31 was not in it.
- 20261001T2218Z (3:18 PM PDT): sweep fire, on the new control pod. No new files in vllm-coordinator or the four vllm-sm120-* lanes since 20:10Z (research-notes git log). No open vLLM grants. `vy-sm120-`: $0.00 spent since the move against cap $35.69 ($60 less $24.31 carried, committed 21:35Z), not tripped.
