---
id: vllm-refactor/gate-a-credential-route
lane: vllm-refactor
kind: rule
from: vllm-coordinator (Cursor agent bc-ba6cec03), owner-approved 2026-09-24
created: 2026-09-24T19:42Z
updated: 2026-09-24T19:47Z
---
# Gate (a) fixtures: mint the key on the laptop, pipe it into your pod, fetch, delete it at once

**The canonical recipe is the gate (a) block in `../vllm-rf-a1/baseline.md`**, which every lane copies at its regression gate. Its steps:
1. **Mint on the laptop, never on a pod.** Minting needs the R2 parent key, which stays on the laptop in `~/.config/verity/r2.env`. Use `research data mint-credential --ttl 3h --permission object-read-only --via local --env`, piped through ssh into `/root/r2ro.env` on **your own** pod (`umask 077`, never echoed).
2. On the pod, fetch every regression row's fixtures listed in `fixtures.toml` into the pod store.
3. **Delete `/root/r2ro.env` right after the fetch.** The 3 h expiry is only a backstop.
4. Run gate (a) with no key. If a row's fetch failed, mint again, fetch that row, and delete again.

- Never copy or reuse another lane's key.
- **Tooling gap:** the long-term fix is for `research run` to pull a run's inputs onto the pod itself. It's recorded in `kb/ops-tools.md`.
