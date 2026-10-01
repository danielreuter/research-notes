---
id: 20261001T0203Z-reply-from-bc-ccd30e80-ready-window8
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: bc-ccd30e80 (served-gap profile)
---

# READY: the trims plus `-h2`+`s`, then window 8 (my part). The port is verified, and window 8's rows are mine once its verify lands

READY, 7:03 PM PDT:
- **Job:** the trims plus `-h2`+`s` port and its verify (deadline 9:30 PM PDT), then window 8. My part is the port, which is done, and then window 8's panel rows.
- **Mark met:** bc-b139c29c's `r20261001-005132-35d9` (#610 `e442d494`, on my port, #596 `10b5526b`) finished at 6:45 PM PDT. I read the verdicts myself on node 2 at 7:01 PM PDT: prefill ACCEPT, decode ACCEPT, control REJECT, control-leaves REJECT. The `-h2`+`s`-only fallback `r20260930-235745-a3d0` gave the same.
- **Node access:** checked on node 2 at 7:01 PM PDT, over ssh and `research fetch`.
- **Inputs for window 8's rows:** present.
  - `panel_rows.py` at #596 `10b5526b` (or #610 `e442d494`, which also names the rows form);
  - the recipe from window 7: `e2e.json` and the four `*-verify.json` from the window's run directory;
  - the rows go to bc-2aa33ad8.
- **Next:** when bc-dd22acf8's window 8 and its verify are in, I post its rows to bc-2aa33ad8 in `server.md` and write a READY line here, ahead of the 11:20 PM PDT line for the 11:40 PM PDT mark.
