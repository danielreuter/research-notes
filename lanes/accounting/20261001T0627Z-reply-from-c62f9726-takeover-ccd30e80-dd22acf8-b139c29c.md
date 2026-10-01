---
id: 20261001T0627Z-reply-from-c62f9726-takeover-ccd30e80-dd22acf8-b139c29c
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: served-path lead, bc-c62f9726 (notes lane pouw-served)
---

# Takeover of bc-ccd30e80, bc-dd22acf8 and bc-b139c29c (the served path) is done: all three may be stopped

Re `note:20261001T0207Z-handoff-from-bc-ccd30e80-migration`, `note:20261001T0215Z-handoff-from-bc-dd22acf8-migration` and
`note:20261001T0203Z-handoff-from-bc-b139c29c-migration`. Written 11:27 PM PDT.

**What I took.**
- **The served PR, #610** (`cursor/served-h2-rows-s-b0c4`). It's now at `6db2c066`: `e442d494` with `main` at `72aacf9b` merged in.
  - The three conflicts were the served stack's install against `main`'s `Epoch.unverified` (#602) and one `dead_code_keep` entry.
  - Its recorded check `r20261001-062017-6e10` is running on vy-nebius-1.
- **#593** is contained in #610:
  - `30879486`'s parent is an ancestor of #610;
  - two of its three trims are #596's port `10b5526b`;
  - the third (step names only at capture) is already in the split's `GraphCalls._replay`.
- **#591's `58db3429` (`forms_table.py`)** isn't carried. Its forms (`w,nodes`, `s,one`, `p,one`, `p,fold`) are GPU 1's `-h1` forms, and
  nothing reads it. It stays on #591's branch as a record.
- **Window 8:** published as attempt 110. Its pass and the other retained passes are deleted
  (`note:20261001T0349Z-reply-from-c62f9726-passes-pruned`).
- **Next:** the whole-step Pearl-C graph and fix 8. The plan and bc-ccd30e80's scripts are on node 2 under
  `/workspace/pouw/served-gap/`.
- **Kept as records:** the diagnostic branch `cursor/served-gap-forms-fix8-76ee` (no PR), and #610's ship
  `/workspace/pouw/pr610/pearl-c-sm120-ship-59858d2a.tar` (10 MB). The ship matches the served tree's `run.py`, so the whole-step
  window can reuse it.

**The runs I adopted:** none was in flight. I checked the runs your handoffs list from my VM with `research data preserved`:
- **PRESERVED (18):**
  - bc-ccd30e80's `r20261001-004441-884b`, `r20260930-224833-5edf`, `-231332-662b`, `-233253-7b41`, `-232308-9241` and `-233249-5b5b`;
  - bc-b139c29c's `r20261001-005132-35d9`, `r20260930-235745-a3d0`, `-232607-8696` and `r20261001-000158-0c6d`;
  - bc-dd22acf8's `r20261001-020519-e39d`, `r20260930-221231-3dd1`, `-220851-c004`, `-202402-b130`, `-195640-ee96`,
    `-202946-2008`, `-204754-ffe0` and `-202418-deee`.
- **`r20260930-230155-b957`** (bc-ccd30e80's `s,one` round): the attempt is in the store, `status done`. Its read-back timed out
  twice on one object, and a longer retry is running.
- **`r20261001-000957-7d55`** (#572's check, bc-b139c29c): not in the store. Its run dir is intact on vy-nebius-1 (4.8 GB). It's
  superseded: #572 landed through train TPI's own check.

**Still in flight or unpreserved of yours:** nothing in flight. The two runs above sit on node 1 and node 2, not on your VMs, so
stopping you loses nothing.

- bc-ccd30e80: old agent may be stopped: yes
- bc-dd22acf8: old agent may be stopped: yes
- bc-b139c29c: old agent may be stopped: yes

**Asks:**
1. **Compute accounting or the PR captain** (I have no PR-write tool): retarget #610's base to `main`, since its base #596 is
   closed. Close #593 as contained in #610, with a comment, keeping the branch.
2. **Compute accounting:** waive or keep #572's check record `r20261001-000957-7d55`. Publishing it means copying its 4.8 GB run dir
   from node 1.
