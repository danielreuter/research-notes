---
id: 20260929T1628Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: window-pin statements would be granted as stated; #364 must refuse a call with two working strata

Re: `lanes/pous/20260929T1608Z-handoff-from-verity-root-window-pin.md`. The red team's verdict is `lanes/pous/20260929T1622Z-redteam-window-pin-statement.md`.

- **Verdict:** it would GRANT all seven `Audit/Window.lean` statements as written: `max`, not the sum, and 2⁻⁴⁰ at K = K_y = 27,713. The actual grant comes at the PR head, once the proofs are in. The work-law lane writes the proofs next and adds an 8th pin for the claim #364 cites: the per-call split plus y's floors at 27,713.
- **For #364, the one code change:** the per-call cap is unsound when a call has more than one stratum doing work. The red team built a window where ten wrong units escape with probability 0.156, against a claimed 2.4·10⁻⁴. #364 is safe today only by construction. So `WorkLaw.budget` should refuse a call with more than one stratum doing work, with a test.
- **What #364 carries when it records X-SPC-105 and X-SPC-106 closed** (the verdict lists these):
  - the verifier derives each call's budget and the dequantization floors itself;
  - call indices are distinct and come from the verifier;
  - every commitment comes before the window key;
  - the per-call ε_ks and δ_link aren't cited as the window's.
