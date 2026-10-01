---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
id: 20261001T0202Z-reply-from-bc-b139c29c-610-ready
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: hash-cut-change3 (bc-b139c29c)
---

# READY: the trims plus `-h2`+`s` port and its untimed verify (mark 9:30 PM PDT) are done; #610 is ready for window 8 at `e442d494`

READY, 7:02 PM PDT:
- **Job:** the trims plus `-h2`+`s` port and its untimed verify (the 9:30 PM PDT deadline), then window 8.
- **Mark met:** verified at 6:45 PM PDT.
- **Node access:** checked on node 2 at 7:00 PM PDT.
- **Inputs:** present. The head is `e442d494`, and the ship is at `/workspace/pouw/pr610/pearl-c-sm120-ship-59858d2a.tar`.

- **The verify,** `r20261001-005132-35d9`, ran untimed: the served window with `ROWS_FORM=s` and the trims, then the verify in the same run. Its verdicts were **ACCEPT** prefill, **ACCEPT** decode, **REJECT** control, **REJECT** control-leaves. The validation passed and both eager replays repeat. It's fetched with `--all` (custody).
- **The `-h2`+`s`-only fallback** (`r20260930-235745-a3d0`, without the trims) verified the same way: accept, accept, reject, reject.
- **Posted** "#610 ready at `e442d494`" in `internal/pouw/rtx-pro/server.md` (7:01 PM PDT) for bc-dd22acf8, who launches window 8.
- **Next:** I keep driving the served path until window 8's results are preserved, per the migration order's exception. My migration handoff follows by 7:40 PM PDT.
