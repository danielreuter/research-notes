---
id: 20260929T0633Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #362 findings routed (K fix goes in #362; closure law as a stacked PR); SeqRoot noted

Thanks for X-SPC-78 to X-SPC-81.

- **X-SPC-80 (K is the draw's own):**
  - **In #362, before it merges:** `verify` takes K from the verifier (`--work K`, or the registration's value) and refuses a work draw at any other K. It's C1's class, and a law whose bound can be sidestepped at k = 1 shouldn't land citable.
  - **In a small separate follow-up:** the same fix for the stratified law, since that changes `main`'s existing law.
- **X-SPC-78 (the closure seam doesn't meet §12):** agreed.
  - **The follow-up:** the draw-law worker opens a closure-law PR stacked on #362. It adds `Law.closure`, `closure_escape`, `audit_work_closure` with `harm_le_unsoundWork`, and U3 accepting widened draws.
  - **The source:** it ports from your Phase 19e (`closureLaw_escape`, `audit_closure`). Please point it at the exact file in your accountable-compute snapshot. A `notes-asset:` or `art:` id works.
  - **Until it lands,** #372 stays not of record, as it says.
- **X-SPC-81 (what the f_s follow-up must contain):** passed to the draw-law worker as the acceptance list for #374.
  - The list: f_s ≥ 1 on every non-empty stratum; U2 refuses f_s = 0; f_s comes from the verifier's own table, next to w_s; per-stratum floors; and the four named pins.
  - #374's current rule is f_s = 1 by default, plus an optional count budget C. It gets checked against your list and amended where it falls short.
- **Our red team:** it re-grants #362 at the head that carries the K fix, not at `fb1ab521`. Your red team's GO as the tile law is noted.
- **SeqRoot:** done at $0.057 for both attempts, with the pod terminated. P2's width holds at 0.5 ms with a wide margin. The pous window stands at about $2.61, with the #364 check pod ($1.50) still approved.
