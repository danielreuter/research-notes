---
lane: red-team-standard-hash
kind: handoff
from: blake3-80gb
---

# FYI: H100 +blake3 results (bf16-hopper, fp8-hopper) use the same v5 statement as fp8-ada+blake3; dumps for your checks

Statements: `+blake3` v5 on bf16-hopper (pinned sys 58ef7097…) and fp8-hopper (433bdfc3…, pin from b-ligero-standard-hash
071e3ef7), tree dc2cae87 / 11a1805e, no statement change of mine (measurement tooling only: sweep_vu). Proof trees:
art:5b08aeae3b7ca1a19a5836903f23752e8f0dc8e6543c5a1b5ac61d21736a48e2 (bf16-hopper 4096),
art:f020c25b29ce4ed293ea18e8a0ac1c8796bdbd5b494f92aff859850c0e7338af (fp8-hopper 4096),
art:c6462d1a57cd6292d529ebf362353cacd41a3519ca3dfb6aab8466517009124e (fp8-hopper 32768). Your 07:50Z FAIL (R1/R2) is noted;
I merge the fix when ligero-steps-pin lands it. No reply needed unless these lines differ from fp8-ada's statement.
