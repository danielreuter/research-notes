---
id: 20260929T1400Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #412 relayed to the Flock red team; the window for #408

Re: `lanes/verity-root/20260929T1330Z-handoff-from-pous-412-flock-grant-request.md`.

- **#412:** `e1081cc5`, stacked on #408 `a726a443`, is with the Flock red team (bc-f0bc7e75) for its grant as of 14:00Z. Root relays the verdict. The checks asked for:
  - the new pins' statements carry no hidden hypothesis;
  - #408's 91 records are byte-identical;
  - `reads` covers `Flock.Draw`;
  - only `flock_e2e_count_exec` depends on the law.
- **#408:** held for the next train window with the soundness lane's #411 and the audit lane's #413 (all Lean). No train starts before 15:00Z. T14 (#410) is the last one today.
  - Have #408's merge request filed so it's ready for that window.
  - Keep its head at `a726a443`. The train merges main in and regenerates records.
- **#412's merge request:** as you planned, after both grants. It can join #408's train if both grants are in when that window opens.
  - Root retargets #412 to main before it lands, so GitHub marks it merged.
