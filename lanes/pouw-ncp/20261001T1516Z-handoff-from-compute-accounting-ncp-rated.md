---
id: 20261001T1516Z-handoff-from-compute-accounting-ncp-rated
campaign: verity
lane: pouw-ncp
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-2f661c92: the assessor's ratings are in. NCP-FP8 can't reach γ ≤ 1% on rated assumptions, even credited

From compute accounting, 8:16 AM PDT. Re `note:20261001T1505Z-reply-from-f9af3acc-ncp-salt-epoch-epsilon`.
- **F-NCP-salt at 40 is D.** The centre and scale steps fuse into one HFMA2 (4.5 salted instructions per element). Restated at
  f_salt = 36, it's C.
- **Per-epoch weights are X-R9-2: confirmed.** F₁ is fixed before the activations are committed, so ε ≈ 6.8% at r = 1.
- **ε is charged at the worst cell,** 0.78% at k = 8,192 and 1.27% at 16,384. γ at 8,192³ is then **2.02% uncredited and 1.73%
  credited**.
- **The morning claim:** your speed result stands (17.1× and 18.6×, bit-exact, timed). Restate γ as "≥ 2.0% uncredited, 1.73%
  credited at f_salt = 36 (C)". No reading reaches 1%.
- **Next:** stop GPU work. In `lanes/pouw-ncp`, write what would have to change for NCP-FP8 to reach 1% (the forming cost, ε's
  worst cell, or the binding), so Daniel can decide whether NCP stays a γ ≤ 1% candidate.
