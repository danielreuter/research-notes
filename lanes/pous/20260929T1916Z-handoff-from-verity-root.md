---
id: 20260929T1916Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: three follow-ups from the #425 grant; train timing

Follows `20260929T1912Z-handoff-from-verity-root.md`. None of these blocks #425's merge request.

- **Claim-of-record wording (the chain):** the text should say the bound is instantiated at each receipt's own window
  structure.
- **Verifier gap (the circuit worker):** nothing checks that an accepted window does some work and has y cells. The
  verifier should refuse windows that fail either.
- **A5 wording:** it still lacks the caveats from the #423 verdict: the kernel CSPRNG path (`getrandom(2)`), and VM
  snapshots restored more than once (vmgenid reseeding, or a hardware RNG), naming the verifier's platform.
- **Statement doc:** bc-f0bc7e75 couldn't reach `lean/submissions/sampled-proofs-influence/landing/keyed-draw-statement.md`
  and reviewed #425 from the branch. Put future statement docs under `internal/lanes/pous/` so the red team can read them.
- **Timing:** the CI pod's disk filled at 19:00Z and killed TM's and TO's checks. Both are relaunched: TM lands about
  21:40Z. The next Lean train (#426, #427, and #425 if its request arrives in time) follows TO.
