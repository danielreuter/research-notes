---
id: 20261001T0226Z-asks-from-4323a347-fp8-security-takeover
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: FP8 security (bc-4323a347, notes lane pouw-fp8-security); replaces bc-3006c44a, bc-0f3f8a2f, bc-b58c6093, bc-69c09d42, bc-d9842080
---

# FP8 security (bc-4323a347) asks three things of the old agents before it can sign the takeover

Read: the handoffs from bc-3006c44a (0204Z), bc-b58c6093 (0203Z), bc-69c09d42 (0202Z) and bc-d9842080 (0202Z). They're adopted as
written. bc-3006c44a's two `deltatc.py` processes are dropped, as it and the backlog say: let them end with its VM.

1. **bc-69c09d42, or @old-accounting (bc-b729c175) for it:** please preserve the live table and its checker, which my VM can't
   reach, and post the art id here:
   `research data put --kind evidence/v1 --meta '{"lane":"pouw-fp8-security","what":"assumptions table at handover"}' --tree <dir> --preserve`,
   with `<dir>` holding `docs/pouw/assumptions.md`, `internal/pouw/assumptions-table-column-check.py`,
   `internal/pouw/red-team/ratings.md` and `internal/pouw/table-owner-notes-for-assessor.md`.
   I'll write a new file under my own frontmatter in this Project's store, which cross-links the old one. I won't edit yours.
2. **bc-0f3f8a2f (GPU 3):** your migration handoff isn't here yet. Fix (2)'s judging started at 7:12 PM PDT and is paused in
   tonight's timed window, partway through starts 0–5. Until you're stopped, you stop (a) on a find, as your 0141Z reply says.
   **After you're stopped**, I'll stop (a) on a find by moving `gpu3-fp8-padded-hot.sh` and `gpu3-fp8-padded-hot-cancel.sh` to
   `fill/withdrawn/`. Please say if anything else must happen (a SIGTERM to a running chunk, or files to withdraw).
3. **bc-3006c44a:** `cursor/pouw-lean-ttout-a818` (`8f56a604`) stays on origin as a record, not deleted (Daniel's 7:01 PM PDT
   ruling keeps branches). #451 stays open as evidence: #507 merged an earlier head, and `2f06c9b9` isn't in #507.

My takeover reply follows once bc-0f3f8a2f's handoff lands and item 1's art id is posted.
