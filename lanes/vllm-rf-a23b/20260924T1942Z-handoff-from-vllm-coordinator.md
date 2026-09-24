---
from: vllm-coordinator (Cursor agent bc-ba6cec03)
to: vllm-rf-a23b
created: 2026-09-24T19:42Z
---
# Gate (a) credential: the "ssh stdin, never on disk" restriction is lifted; follow the new route

- The owner approved an interim route. Mint your own short-lived read-only R2 credential on the laptop and pipe it onto your pod. Prefetch every regression row's fixtures into the pod store, delete the credential immediately, then run gate (a) without it.
- Exact commands: `../vllm-refactor/20260924T1942Z-gate-a-credential-route.md`.
- Never copy another lane's credential, including a1's `/root/r2ro.env`.
