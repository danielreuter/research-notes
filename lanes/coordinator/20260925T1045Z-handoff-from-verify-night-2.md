---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T10:45Z
---

# verified: all four 4090 fp8-ada+blake3 cells accepted @3301c435, plus x4 art:017a7069; the x4 8192 plateau is running

All were re-verified with ligero-verify 596529d2 (main 3301c435) and main's reverify: roots recomputed, stems = proofs =
entries, batch n = count. 04 is BOUND, 06 ROOTS-MATCH, and the 05 negatives behave (base ACCEPT, 3 REJECT). Run
r20260925-102219-11de. Every label's `verifier` names main 3301c435.

| result | cell | reverify | verdict |
|---|---|---|---|
| art:e9932b72 | fp8-ada+blake3 4096, live same-pod verifier | 49/49, 2^-128.40 | art:2cd1052bd55d6eb0a46292cf8ed89bb82c97cba1e0b9b46b3ec4ec5c266776da |
| art:e7d59ab6 | fp8-ada+blake3 4096, x1 GPU committer | 49/49, 2^-128.40 | art:0a3efdafc658134df191c9eb0928358effb475d8f7c75b3707c4a70129cc334b |
| art:5d20ad00 | fp8-ada+blake3 4096 frozen, host committer | 49/49, 2^-128.40 | art:2ba7f87352dbe11de2b17ffa9ec6aa2379f02eda7be5e79a722888793fc3f0a7 |
| art:d6328cf5 | fp8-ada+blake3 16384 plateau | 193/193, 2^-128.40 | art:ddf49ecce7d6dd473dcca7caed6b3c152c4c5cee01a96957207066400dfffe67 |
| art:017a7069 | fp8-ada-x4+blake3 4096, steps 12 | 13/13, 2^-128.33 | art:953851f2e60587878a4a4f75c08f3ef412c7985a36aa35efc4eaab3ebf9b86e3 |

- **Findings:** none of the four fp8-ada+blake3 cells carried a `finding` label, so there was nothing to mark CLEARED. The
  red team's grant (1027Z) covers them.
- **x4:** the red team's 1027Z scan includes the x4 fold's 8:2 shape (0 free rows), but its headline grant names
  fp8-ada+blake3. Whether x4 counts is your call. The x4 instance-equiv file art:f70cf39f `--check` runs after the 8192 plateau.
- **SP1 art:49695f7c:** I recorded `finding=CLEARED`, with ref my verdict art:58978516, next to the UNDER RE-VERIFICATION one.
- **Next:** poseidon-v1's 5090 NVFP4 pair (art:70f275ac, art:6740eb22) is queued. For the +sha256 x4 plateaus I'll sync the
  pod to main 767115db once the queue drains, and name 767115db in the labels. Please send or point me at their ids.
