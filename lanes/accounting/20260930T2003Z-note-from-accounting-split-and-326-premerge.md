---
id: 20260930T2003Z-note-from-accounting-split-and-326-premerge
campaign: verity
lane: accounting
kind: note
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For @memory-accounting (bc-15ada664) and @network-accounting (bc-ecea50f6): @old-accounting's handoff lands here, and #326 merges cleanly onto main b1c77be0

- **The split (Daniel, 20:01Z).** `lanes/accounting/` is compute-accounting's lane, which covers PoUW.
  - I asked @old-accounting (bc-b729c175) for its full state in `note:20260930T2000Z-handoff-from-accounting-state-for-successor`,
    due 21:00Z. Its reply lands here, as `<stamp>-handoff-from-pous-state.md`, with its store as an evidence-store tree.
  - Take the PoUS and network parts from it. If I learn something that concerns you, I'll add a note here.
  - The charter these rest on is `note:20260930T1740Z-handoff-from-pous-charter-pouw`.
- **#326, for @network-accounting.** I stopped my review when the split landed. Here is what I had:
  - **The merge.** Head `c176adb1` merges into main `b1c77be0` with no conflicts. On the merged tree, `uv lock --check` passes.
    No suite ran on the merged tree.
  - **The pins.** `CheckAxioms.lean` only regroups the same 34 `#print axioms` lines: 31 pinned, and 3 proved but not pinned.
    It changes no `lean-audit.json`, so no statement reviewer is needed.
  - **The request.** The owner's merge request is `note:20260930T1535Z-handoff-from-network-warden-326-merge-request`. Its
    recorded check, `r20260930-151146-adaf`, was run on base `2c4101bf`, 62 commits behind main.
  - **Nothing from me is running** for #326.
