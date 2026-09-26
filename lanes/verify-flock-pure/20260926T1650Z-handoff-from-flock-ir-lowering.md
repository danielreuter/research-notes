---
lane: verify-flock-pure
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T16:50Z
---

# flock-ir-lowering: class cell c2 (T = 129..256) is ready to replay, art:b61eafa9

- **Cell:** `art:b61eafa930f2f77a68b7d0db3b2e31d9fed6fed14a57179438df2c9ce9e5364e`, at 8ef6d347: the verifier code is 11f24da6's, and only the harness changed.
  - Verifier run r20260926-153220-186b (vy-flock-ir-lowering-b-ver): `out/verifier` has `class.json` (pin fc9dceb5), `net-t129..256.txt` and `p0-2048/sessions-s0..127`.
  - Prover run r20260926-153234-eeb6.
- **Inputs:** set `art:82c591d1`, `TEMPLATE=attention-head`, `PER=16`: 128 sub-batches.
- **Don't replay these:** `ef10f5fb`, `82f4a9be`, `87a6bcdd` and `a43e5cac` are runner copies and contended runs, labelled `superseded_by` b61eafa9.
- **c1 and c3** (art:4fb2de9c, art:4dd2069b) are as in my 14:12Z and 14:40Z notes.
