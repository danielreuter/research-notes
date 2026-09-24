---
id: vllm-coordinator/setup-for-old-chat
lane: vllm-coordinator
kind: setup
from: vLLM coordinator (Cursor agent bc-ba6cec03)
to: old vLLM chat eb746331
created: 2026-09-24T19:45Z
---
# For the old vLLM chat (eb746331): your role in the new Project setup

Full setup: `~/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/project-context.md`. Read it from a plain shell; the `/cursor/stores/...` form of that path exists only on cloud VMs. Your section of it, verbatim at 19:45Z:

> ## The old vLLM chat and its five lanes
>
> - Lanes a1, f1, f24, f3, f56 are subagents of the old vLLM chat. Only a23b is a Project agent.
> - Nobody can message a running subagent, not even the chat that started it. They can only be steered through their files (`STATE.md`, handoffs), their pods, or by restarting them as Project workers.
> - **Don't delete the old chat**; that may kill the five lanes. It stays idle and wakes only when a lane reports.
> - When it wakes, it records the lane's result under `~/.research/notes/lanes/` and takes no further action. The vLLM coordinator decides what happens next.

In practice:
- When a lane's final message reaches you, write it to `~/.research/notes/lanes/vllm-rf-<lane>/<YYYYMMDDTHHMMZ>-result-from-old-chat.md`.
- Don't merge, launch, message or resume lanes. Don't touch pods or the `vy-control-verity` daemons.
- The vLLM coordinator (see `20260924T1920Z-took-over.md` in this directory) handles READY.md checks, relaunches, deadline extensions, and merge requests to the owner.
