---
id: proofs/20261005T0247Z-finding-1150-flockproofs-exempt
campaign: verity
lane: proofs
kind: finding
status: closed
repo: danielreuter/verity
origin: bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4 (proofs coordinator)
---

# #1150 at `6d87facc0`: the `FlockProofs` reads exemption

Verdict: GRANT for `pr:1150@6d87facc0360ab7436a6c40ea4aad172373c3a9a`.

I read `git diff 99f22f0b1..6d87facc0`, which is one commit (`6d87facc0`). It changes one file,
`backends/flock/verifier/lean/soundness/lean-audit.json`, and adds one line: `"FlockProofs"` in `reads_exempt`, with the
same reason as the three existing entries (`Flock`, `FlockLevel3`, `FlockSoundness`): "C-Flock is excepted until proofs
extracts its spec (Daniel, 4 Oct 1:30 PM PDT)".

Why it widens nothing:

- Nothing else in the record changes: no signature, type hash, assumption, reads group or owner.
- Main has no reads check; #1150 adds it. The exemption removes nothing that holds on main.
- `FlockProofs` is the verifier package's proof-side module. `Registered.openPair`
  (`backends/flock/verifier/lean/FlockProofs/Registered.lean`, line 226) is the computable collision extractor that the
  soundness guarantees read. The verifier's own lock (`backends/flock/verifier/lean/lean-audit.json`) already exempts
  `FlockProofs` under the same ruling, so soundness's lock now agrees with it.
- Moving `openPair` into `Flock` would put a proof-only extractor into the executable verifier. That changes trusted code
  and `lean-agreement`'s input, so the move belongs to proofs' spec extraction, which deletes these entries.

The gap was found by core-lock-tc (bc-27962cfc) and flagged to lean and ci in thread 1790957906.278529
(1791167550.287019). Lean's change is the fix proposed there.
