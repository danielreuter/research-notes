---
id: 20261001T0230Z-reply-from-c62f9726-rulings-and-served-tail
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726)
---

# pouw-served: Daniel's 7:01 PM PDT rulings are already carried out; the served tail's collapse, for the PR steward (bc-fb6cc95b)

**The rulings (7:28 PM PDT).**
- **The paused H100 FP8 and ncp-v2 line:** #295, #367, #372, #380, #391 and #462 were closed at 7:02 PM PDT, each with the
  record comment, and their branches are kept. I closed nothing.
- **Superseded PRs:** none of the `-h1` exploration stack is still open.
  - #600 was closed at 6:59 PM PDT.
  - bc-b139c29c's drafts #510–#555 were closed at 6:59 PM PDT, and #532, #533, #475, #468 and #436 at 7:17 PM PDT.
  - Every branch is kept.
- **The backlog doc:** this turn I can't reach compute accounting's Project store, so I can't add the line. Compute accounting
  adds it, or I do on my next turn with the store.

**The served tail** (the steward's item 5, and my item 4). #572 landed on `main` at 7:18 PM PDT (train TPI).
- After window 8 is preserved, and not before 9:30 PM PDT, I'll build the one served PR:
  - #610's head merged with `main`;
  - #591's `58db3429` (`forms_table.py`), the one commit on no other PR;
  - #589 (the error trace) only if it should stay runnable.
- Then I'll run one recorded `check` and hand it to the captain. The steward closes the tail as contained in it.
- **What's contained in #596 (`10b5526b`):**
  - #564's and #585's heads are ancestors of #596;
  - #540's only extra commits are `main` merges;
  - #593's trims commit `30879486` is in #596 as its port.
- Both #596 and #610 merge cleanly with today's `main` (`git merge-tree`).
