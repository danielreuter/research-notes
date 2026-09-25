---
lane: agkr-bound
kind: handoff
from: coordinator
created: 2026-09-25T06:40Z
---

# UNBLOCK + RETARGET: commitment decision is final; $100 cap; non-hash parts now, in-circuit hash gadget only after the survey

Decision (final): Project store `docs/commitment-scheme-decision.md` (§1, §3, §5, §6.2 "A-GKR", §6.4 "agkr-bound (retargeted)").
Your 0540Z/0550Z estimate (Poseidon2 digests) is superseded. Budget: $100 cap for the retarget (report before exceeding);
FINAL moves to 15:00Z (8:00 AM PT). Table 2 spec: ~/.research/notes/kb/TABLES.md (new) + its Amendment at the end (algebraic
hashes are reported with a mark, not excluded; SHA-256/BLAKE3 stay the target).

Target statement (A-GKR): row-digest layers in the exported circuit, data-parallel over rows, computing frame-v3 SHA-256 row
digests first, then keyed-BLAKE3 (§6.2: commit each round's new words with the carries as inputs, check rounds in shallow
layers, bitwise ops through LogUp-GKR tables); publish the digests; `verity-gkr-verify` checks them natively against the
scheme's trees (frame-v3, `verity.commitments`); own relation name(s) + pins (#13).

SURVEY GATE (user): a survey of efficient SHA-256/BLAKE3 proving (Flock, Lasso/LogUp lookups, GKR hashing, Binius, zkVM
precompiles) is being written (Project store `docs/hash-proving-survey.md`). Until it lands, do the NON-hash parts: the native
frame-v3 tree check in verity-gkr-verify (with vectors from the core reference; the SHA-256 row-leaf schema is being added to
`verity.commitments` by the core-schemes agent: implement against the decision doc §5 framing in one swappable module), digest
publication plumbing in the statement/public words, relation names + pin lines, harness/commitment bucket, negatives scaffolding.
Do NOT lock in the in-circuit SHA-256/BLAKE3 layer design or spend pod time on hash-circuit optimization until I send the survey
handoff; then adopt its recommendations or record why not. Your public-input intermediate (art:559147e1) stays as a drill-down result.

Set your checkpoint to open and continue.
