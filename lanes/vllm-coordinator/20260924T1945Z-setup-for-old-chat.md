---
id: vllm-coordinator/setup-for-old-chat
lane: vllm-coordinator
kind: setup
from: vLLM coordinator (Cursor agent bc-ba6cec03)
to: old vLLM chat eb746331
created: 2026-09-24T19:45Z
updated: 2026-09-24T19:46Z
---
# For the old vLLM chat (eb746331): your role in the new Project setup

You can't read the Project store, so this note is your copy of the Project's setup doc (`docs/project-context.md`). The full doc, copied at 12:46 PM PT, is below. The vLLM coordinator refreshes this copy when the doc changes in a way that affects you.

**Your role:** you are a passive host for lanes a1, f1, f24, f3 and f56.
- **Don't delete this chat.** That may kill the five lanes.
- When a lane finishes, write its final message word for word into `~/.research/notes/lanes/vllm-rf-<lane>/`, then do nothing else.
- Don't merge, launch, message or resume lanes, and don't touch pods or the `vy-control-verity` daemons.
- The vLLM coordinator (`20260924T1920Z-took-over.md` in this directory) handles READY.md checks, relaunches, deadline extensions, and merge requests to the owner.

---

# Verity Project: setup and standing decisions

Current truth for every agent in the Verity Project. Correct it in place when it's wrong; don't append history.

## Who runs where

| Agent | Runs on | Owns |
|---|---|---|
| Project root coordinator | Cursor cloud VM (no laptop access, no `~/.research`) | Talking to Daniel, routing work, relaying between coordinators, `notes.md` |
| [Research coordinator](https://cursor.com/agents/bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388) | Daniel's laptop, via My Machines | Afternoon campaign (verifier-cost, arith lanes); **all merges into `main`** from `~/projects/verity-main-wt/main` |
| [vLLM coordinator](https://cursor.com/agents/bc-ba6cec03-e2aa-5a7e-9db3-6bc124a205aa) | Daniel's laptop, via My Machines | vLLM refactor workstream (lanes a1, a23b, f1, f24, f3, f56 and their `vyv-rf-*` pods); pushes branches, never merges `main` |
| Old vLLM chat | Cursor app on the laptop | Nothing new. Passive host of five lane subagents (see below) |

My Machines agents run as a background worker process, not inside the Cursor app window, so they don't add to the app's memory load. Their shell commands still use the laptop's disk and memory, so heavy work goes to pods (`research run --on ...`).

The Project store is `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/` on cloud VMs. That path doesn't exist on the laptop, where the same store is `~/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/`. My Machines workers can read it there. The old vLLM chat in the Cursor app can't, so its copy of this doc is `~/.research/notes/lanes/vllm-coordinator/20260924T1945Z-setup-for-old-chat.md`.

## The old vLLM chat and its five lanes

- Lanes a1, f1, f24, f3, f56 are subagents of the old vLLM chat. Only a23b is a Project agent.
- Nobody can message a running subagent, not even the chat that started it. They can only be steered through their files (`STATE.md`, handoffs), their pods, or by restarting them as Project workers.
- **Don't delete the old chat**; that may kill the five lanes. It stays idle and wakes only when a lane reports.
- When it wakes, it writes the finished lane's final message word for word into that lane's notes folder (`~/.research/notes/lanes/vllm-rf-<lane>/`) and takes no further action. The vLLM coordinator decides what happens next.

## How messages flow

- Daniel talks to the root in the Project chat, and can open any coordinator's chat directly for deep work.
- The root messages coordinators; coordinators report back to the root when a turn ends.
- Coordinators can't message each other. They go through the root, or leave notes under `~/.research/notes/`.
- The vLLM coordinator's merge requests go to the root, which forwards them to the research coordinator.

## Secrets

- **Cursor runtime secrets** are set in the Cursor dashboard and injected as environment variables into Project agents on cloud VMs: `R2_ACCOUNT_ID`, `R2_BUCKET`, `R2_ENDPOINT`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (R2's S3-compatible keys), `RUNPOD_API_KEY`, `RUNPOD_SSH_KEY_B64`. The root verified at 12:00 PM PT that R2 listing and the RunPod API both work.
- **The Cursor secrets don't reach My Machines workers.** Checked at 12:38 PM PT: the vLLM coordinator's worker has no `R2_*`, `AWS_*` or `RUNPOD_*` environment variables.
- **Laptop agents** use the laptop's existing config:
  - `~/.runpod/config.toml` (`apikey`, `apiurl`) and the ssh key under `~/.runpod/ssh/`;
  - `~/.research/machines.toml` and `~/.research/store.toml`;
  - `~/.config/verity/r2.env`, the R2 parent key pair (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`, `R2_BUCKET`, `R2_ENDPOINT`), which `research data mint-credential --via local` signs with.
- **Pods never get the Cursor secrets or the R2 parent keys.** There are two exceptions to "no credentials on pods":
  - `vy-control-verity` keeps an account RunPod key in `/root/.runpod/config.toml` for the `vyv-` daemons;
  - every RunPod pod carries RunPod's own pod-scoped `RUNPOD_API_KEY` in its container environment, which can only terminate that pod.
- **Interim exception for regression-gate fixtures:** a lane mints its own read-only R2 key **on the laptop** (`--ttl 3h`) and pipes it into its own pod. Never mint on a pod: that would need the R2 admin key there. The lane fetches the fixtures, then deletes the key from the pod right away; the 3-hour expiry is only a backstop. It never copies another lane's key. The recipe is the gate (a) block in `~/.research/notes/lanes/vllm-rf-a1/baseline.md`, which the five old-chat lanes copy when they reach their regression gate. The long-term fix is for the research tool to pull a run's inputs onto the pod itself, recorded as a gap in `~/.research/notes/kb/ops-tools.md`.

## Money

- **The RunPod account auto-tops-up** when the balance drops below about $100, so the balance itself isn't a limit. About $14.76/h was going out at 12:36 PM PT. At 12:41 PM PT the vLLM pods alone were $12.14/h, after f1 replaced a 2-GPU pod with a 1-GPU one, and vLLM had spent $245.52 of its $600 cap. If the balance goes below about $90 without refilling, report it.
- `balance_floor.py` on `vy-control-verity` terminates every `vyv-` pod below $25. It's a backstop that should only trip if auto top-up fails.
- **vLLM limits:** the budget daemon caps vLLM spend at $600, and that cap is the binding limit. The deadline daemon was set to 8:00 PM PT (03:00Z); the vLLM coordinator pushes it back a few hours at a time so it still works as a dead-man switch.
- **`vy-control-verity` is the single shared control pod** (also called `vy-control`). Never terminate it. The vLLM coordinator manages the `vyv-` daemons on it. At 12:31 PM PT those were its only daemons: `budget_cap.py`, `deadline.sh` and `balance_floor.py`, with state and log in `/root/dm/` (`CAP`, `dm.log`).
- **Research campaign:** each lane has $10, and the leftover verifier pod ($0.44/h) is kept until its sessions are preserved.

## Standing decisions

- Report times to Daniel in California time (PT; PDT is UTC−7), not Z. Filenames and note ids keep their `YYYYMMDDTHHMMZ` convention.
- One owner for `main` merges: the research coordinator.
- Don't touch another workstream's lanes or pods.
- Moving lanes to cloud agents comes after the current lanes finish. It needs a remote for the notes, a way to register results remotely, and command-line fallbacks to the `RUNPOD_*` environment variables.
