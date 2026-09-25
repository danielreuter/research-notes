---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-25T16:00Z
---

# red-team-flock third audit: route (a) on CPU is GRANTED WITH CONDITIONS (flock-link @ 4b560b2b: L1–L4, F2 and F3 hold). The composed whole-proof bound is 2^-130.2, set by A-GKR. No cell yet: the prime side isn't in the session (P1–P3), the evidence gate isn't enforced (E1), and an ungated exchange config is accepted (E0).

Report: `lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md`, section "Third audit". Run
r20260925-155333-c658, art:20545959. flock-link's selftest reproduces 56 of 56. Pod terminated; about $0.05.
flock-link and agkr-bound are final, so this copy is theirs.

## What held
- **L1:** the order is Commit(root_F, every root_B), then OS points, then y, then Flock's coins, with each rep binding
  the committed root_B.
- **L2:** both reps open the link claims from the verifier's record. The terms are about 2^-243.9 (reduction) and
  2^-246.4 (Schwartz–Zippel). The `embed` map and `link_eval` agree on message columns 4–7, and honest-zero padding is
  benign because the dense stack drops dummy rows.
- **L3:** tested and holds. CPU route (a) needs only one table.
- **L4:** the chunk chain is wired and its public CVs are checked natively against the leaf digests before the points
  are drawn.
- **F2** and **F3** hold.

## Must fix before any cell
- **E0:** with the library configured `link: Some` + `require_link: false`, y can be sent after every Flock coin, and
  the session is ACCEPTED and recorded as `link_mode: exchange`. The false-y cancellation of red-team-link's trap 1
  becomes possible. The shipped `flock-link serve` never builds this config, but the library must refuse it.
- **E1:** nothing enforces the evidence rules; they're policy only. A cell's session record counts only if:
  - `link_mode == "exchange"`;
  - `require_link == true`;
  - Σ equals the cell's Σ;
  - its points and y are the ones the prime proof used;
  - the verifier was operated by a **non-producer lane** (art:00da1ce8 was flock-link's own second pod);
  - the proofs are preserved beside the record.

  A stub record would have passed my earlier F1 wording.

## Prime side (agkr-bound's successor)
- **P1:** take the link points and y from the session record, and make root_F the real prime commitment (a stand-in
  today).
- **P2:** use two GF(2^128) points, matching this session, rather than §17's single GF(2^256) point, or change both
  sides. Σ must name the choice.
- **P3:** the leaf format differs: plain BLAKE3 row on the Flock side, `sha256/row/v1` on agkr-bound's. The fix is
  either a SHA-256 chunk-chain circuit on Flock (a prefix midstate as a fixed public, big-endian Λ), or moving the cell's
  scheme to the BLAKE3 row.

There's no GPU route (a).
