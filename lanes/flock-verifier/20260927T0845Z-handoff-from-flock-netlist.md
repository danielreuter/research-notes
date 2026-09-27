---
id: flock-verifier/20260927T0845Z-handoff-from-flock-netlist
campaign: verity
lane: flock-verifier
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 68ae79f2
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Identity text fix: `hashes.round_digest`, `statement_digest` and `sigma` now read `sha512`

For `note:flock-verifier/20260927T0445Z-handoff-from-flock-netlist-format`. The backend identity's `hashes` object said `sha256` for
these three, which have been SHA-512 since `eb90718f`. From `68ae79f2` it says `"round_digest": "sha512 (framing: …)"`,
`"statement_digest": "sha512"`, `"sigma": "sha512"`; `coin_derivation` stays `sha256 (verity.randomness)`, which it is. Only the
statement digest's value changes (it hashes the identity); no format, binding or byte layout changes. If you pin the identity's
text, update those three strings.
