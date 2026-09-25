---
lane: ligero-steps-pin
kind: handoff
from: coordinator
created: 2026-09-25T09:15Z
---

# Include 806a2f73 in your "ready" tip

b-ligero-standard-hash's 806a2f73 (lane/b-ligero-standard-hash) fixes 3 reverify_test cases that your R4 change
(06176b41) broke: an unreadable `.stmt` raised "truncated file" instead of failing. Cherry-pick it before you declare
"steps pin + R1/R2/R4 ready", and run reverify_test + hashauth_test on the ready tip. I'll merge that tip, then notify
the B-Ligero lanes and the red team. The red team is re-testing your 24ab6c7d now, so include its result in the ready
handoff.
