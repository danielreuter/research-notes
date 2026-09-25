---
lane: red-team-standard-hash
kind: handoff
from: ligero-steps-pin
created: 2026-09-25T09:37Z
---

# ligero-steps-pin: the ready tip is c8a16e2b; please re-run your harnesses there

The ready handoff to the coordinator names `lane/ligero-steps-pin` c8a16e2b. It is not 24ab6c7d + 806a2f73 + 943d5e96:
b-ligero-standard-hash's 806a2f73 is **not** cherry-picked. Instead, c8a16e2b does the same thing on top of your
pinned-relation reading:
- an unreadable statement in a hashed dump is a FAIL;
- the manifest check also refuses a proof paired with another sub-batch's statement, and a proof listed twice;
- a v6 dump fails closed (943d5e96).

I ran your harnesses on my pod against 06176b41 through 8e2f793c:
- remap `--set-binding`: rc 1;
- orphan `--vus 3`: rc 1, control PASS;
- steps: 48 accepted, 64 refused by both verifiers. steps 32 with blake3 crashes in the honest prover, because the gadget
  refuses rows of 1 chunk.

Evidence: art:61aedd2762f64fe16c5189c5378cab94dc86b221188922931a1fe85d307ad7b7.
