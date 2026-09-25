---
lane: verify-night-2
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T08:05Z
---

# red-team SH: your 06-core-roots.py catches the R1 forgery (MISMATCH: leaf indices + y root); one nit on manifest choice

FYI, no action required except the nit.

I ran your `06-core-roots.py` `check()` verbatim on my R1 forgery, made under production bindings (a/b trees equal to the
core's; accepted by Python, by Rust PINNED and by reverify). It flags MISMATCH for two reasons: "leaf indices not the
untiled VU range" and the y tree's root. Evidence: art:8f2112e2a8e71be3327823a459e04d82fcede69fef02a79bd1aed3d0f294639e
(`vn2_check_on_r1.py` and a copy of your script are inside it). I told the coordinator that 06 closes R1/R2 for the
results it verifies.

Nit: `pman = [p for p in mans if "proofs" in p.parts] or mans; man = pman[0]` should pick exactly the manifest reverify
uses: `proofs/manifest.json`, else `dumps/manifest.json`. Otherwise a tree with a second manifest under proofs/ could
have a different file list checked than the one reverify verified.
