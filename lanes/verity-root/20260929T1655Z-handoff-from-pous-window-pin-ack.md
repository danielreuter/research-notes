---
id: 20260929T1655Z-handoff-from-pous-window-pin-ack
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: window-pin verdict taken; #364 carries its conditions; Daniel already approved tier 3 for keyed draws

Re: `lanes/pous/20260929T1622Z-redteam-window-pin-statement.md`, `20260929T1628Z`, `20260929T1636Z` and
`20260929T1640Z-handoff-from-verity-root.md`.

- **Tier 3 (X-SS-2): don't put it to Daniel.** I asked him directly at 16:36Z, and he approved it. Our Lean lane (the
  author of #408, #412 and #416) owns it, in a new draft PR, and #364, #408, #412 and #416 stay untouched. It needs
  three pieces:
  - a named keyed-stream assumption: distinct contexts under one key give independent uniform streams;
  - `Key.subset` tied to `Flock.Draw.subset`;
  - the lemma that C per-call draws form one stratified law.

  The assumption's wording comes to bc-f0bc7e75 through this lane before anything is built on it. It composes with the
  window pin through `audit_window_of_le`.
- **The window pin's conditions, all going into #364's in-flight push (the `9ac48ce8` merge):**
  - `hone` enforced in code: the budget refuses a call with more than one stratum doing work (`0 < w_s·n_s`), with a
    test, and checks that a call's tiles share one template.
  - Admission inside the draw (X-SPC-107).
  - `PROTOCOL.md` records X-SPC-105 and X-SPC-106 as closed, with the four conditions from the verdict, each citing code:
    - the verifier derives K_c and the floors itself;
    - call indices are distinct and come from the anchors;
    - every commitment precedes the window key;
    - no per-call ε_ks or δ_link is cited as the window's.

    It cites `audit_window_split_of_record`, pending the proofs PR.

  The circuit worker's row-by-row check waits for that PR.
- **#364's recorded check:** held until RC's custody note arrives in `lanes/pous/`.
- **#416:** thanks. We'll file its merge request after the grant and TL.
