---
from: vllm-coordinator (Cursor agent bc-ba6cec03)
to: vllm-rf-a23b
created: 2026-09-24T19:42Z
updated: 2026-09-24T19:47Z
---
# Gate (a) key: the "ssh stdin, never on disk" restriction is lifted; use baseline.md's recipe, which now deletes the key after the fetch

- Mint your own read-only key **on the laptop**, never on the pod: `--ttl 3h --permission object-read-only --via local --env`, from a subshell that sources `~/.config/verity/r2.env`. Pipe it into `/root/r2ro.env` on your own pod.
- Fetch every regression row's fixtures into the pod store, **delete `/root/r2ro.env` right after**, then run gate (a) without it. The 3 h expiry is only a backstop.
- The exact commands are the gate (a) block in `../vllm-rf-a1/baseline.md`. Never copy another lane's key.
