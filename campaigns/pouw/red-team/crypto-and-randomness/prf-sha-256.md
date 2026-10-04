---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `prf/sha-256`: A

30 Sep 2026, 08:20Z. Independent assessor (bc-d7d4b0d1). A literature rating: no run.

**The row.** `verity.randomness.derive` and its streams are indistinguishable from a random function when `source` is uniform and unknown to the adversary at the time it fixes `ctx`.

- The construction is secret-prefix SHA-256: `derive` = SHA-256(tag ‖ frame(source) ‖ frame(domain) ‖ frame(ctx)); `stream` = SHA-256(tag ‖ key ‖ frame(index) ‖ counter[8]); `shard` = SHA-256(tag ‖ key ‖ frame(index)). A frame is tag ‖ 8-byte length ‖ body (`verity/randomness/__init__.py`).
- **Length extension, the table's open check, is closed.** Every input is prefix-free: a fixed tag, length-prefixed frames, and a fixed-width counter. An extension appends bytes after the canonical end, so it is never the encoding of another (domain, ctx) or index, and it yields no output the scheme uses.
- What is left is the prefix-keyed PRF assumption on SHA-256's compression function, the standard basis of NMAC and HMAC-style security.

**Rating.** **A.** Standard construction, correctly framed.
