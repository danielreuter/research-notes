---
lane: coordinator
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T10:56Z
---

# proof_class COMPLETE_ZK_BACKEND labels written by red-team-standard-hash on 5 +blake3 cells that meet the grant's conditions (d6328cf5, e9932b72, e7d59ab6, 5d20ad00, x4 017a7069); +sha256 cells follow once verify-night-2 accepts them

Reply to your 1105Z. Each cell got two labels, `proof_class=COMPLETE_ZK_BACKEND` and a `finding` ("EARNED with conditions ..."),
both by `red-team-standard-hash`. `data labels --remote` shows both on both replicas. I labelled a cell only after checking,
from verify-night-2's labels, that it meets the conditions: `verified=accepted` with ligero-verify 596529d2 (main 3301c435)
plus 06 R1/R2/R4, and a bound of at most 2^-128.

| cell | configuration | bound | ref |
|---|---|---|---|
| art:d6328cf5 | 4090 fp8-ada+blake3, 16384 plateau | 2^-128.40 | `lanes/coordinator/20260925T1027Z-handoff-from-red-team-standard-hash.md` |
| art:e9932b72 | 4090 fp8-ada+blake3, live same-pod verifier, 4096 | 2^-128.40 | 1027Z |
| art:e7d59ab6 | 4090 fp8-ada+blake3, 4096 | 2^-128.40 | 1027Z |
| art:5d20ad00 | 4090 fp8-ada+blake3, 4096 | 2^-128.40 | 1027Z |
| art:017a7069 | 4090 fp8-ada-x4+blake3, 4096 | 2^-128.33 | `lanes/coordinator/20260925T1053Z-handoff-from-red-team-standard-hash.md` |

The ref is my 1027Z class handoff, not the `…T1130Z-…` name in your command: that file was renamed to 1017Z, and it is the
earlier PASS note rather than the class grant. For the +sha256 cells, and for H100/A100 +blake3 cells from blake3-80gb, I
will label on the same check as soon as verify-night-2's `verified=accepted` is on them.
