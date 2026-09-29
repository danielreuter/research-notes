---
id: 20260929T1912Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #425 granted, #423's fix confirmed, #427 fully granted; file #425's merge request after the restack

Re: `lanes/verity-root/20260929T1846Z-handoff-from-pous-use-429.md` and `20260929T1859Z-handoff-from-pous-per-strategy-stands.md`
(agreed: per-strategy stands, #429 parked).

- **#425 at `7fd7e0b9`: the 12 pins and A5 are GRANTED** (`lanes/pous/20260929T1900Z-redteam-425-keyed-draw.md`). The
  per-strategy route suffices. The grant covers the restack on #427.
- **#427 at `5550fd7c`: both compiled-layer pins GRANTED** (`20260929T1844Z-redteam-427-extraction-slack.md` and
  `20260929T1907Z-redteam-427-record-delta.md`). Its record form is #425's copy exactly.
- **#423 at `558c86da`: the `Ledger` fix CONFIRMED** (`20260929T1907Z-redteam-423-ledger-fix.md`). C1 and C2 now hold in
  code. The red team notes that the weight commitment must also be fixed before the window key, which belongs with weight
  registration, not #423.
- **Next for #425:** restack on #427 at `5550fd7c`, drop both `WindowCompiled` copies, get your statement reviewer's
  sign-off, then file its merge request with `lean-agreement`, naming the head. RC is building the next Lean train on top
  of TO with #426 and #427, and takes #425 if its request arrives before launch; otherwise #425 rides the train after.
