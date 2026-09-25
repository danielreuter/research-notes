---
lane: flock-backend
kind: handoff
from: coordinator
created: 2026-09-25T21:30Z
---

# red-team-flock GRANTED flock-pure-block/v2 WITH CONDITIONS (NON_ZK_PROOF, 2^-193.44 per 32,768-VU batch; handoffs 2120Z/2125Z): three fixes, then the 65,536 result gets the same label

Conditions to meet, before your cell publishes:
1. **Name the verifier commit and binary in every result.** art:ca6029c1 records "unknown". Put the verifier's source commit
   and the `flock-pure-gpu` binary sha256 in the result meta, and re-register the 65,536 sweep result that way.
2. **Report the union bound over sub-batches.** A 32,768/65,536-VU run is several proofs; the result's security bound is the
   union over them, not one proof's.
3. **Widen the unit self-check's exponent range** (red team's note).
Once the 65,536 result names its commit, red-team-flock writes the same proof_class label on it, and verify-flock-pure
(the non-producer for the H100 Flock cell) replays and labels it. The target is all of this by about 00:30Z for the 01:00Z render.
