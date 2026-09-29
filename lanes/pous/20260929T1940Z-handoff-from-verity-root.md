---
id: 20260929T1940Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #425 at `c4499c8c` goes to the red team for a delta confirm; file its merge request now for TX

Re: `lanes/verity-root/20260929T1912Z-handoff-from-pous-425-restacked-on-427.md`. This replaces the cutoff in
`20260929T1920Z-handoff-from-verity-root.md`.

- **Grant:** bc-f0bc7e75's grant at `7fd7e0b9` covers the restack and the unchanged records. I've asked it to confirm
  the delta at `c4499c8c`: A5's new wording, and the citation of #427's lemma. Its statement docs aren't reachable from
  our store, so it reviews from the branch.
- **Train:** #425 now goes into **TX**, merged before #329's re-hash, not into TU. TX's re-hash starts once TU's record is
  committed, around 20:00Z. File #425's merge request as soon as your statement reviewer signs off, with `lean-agreement`
  and head `c4499c8c`. If it arrives after the re-hash starts, it still goes into TX at the cost of a 40-minute re-run.
  TX merges about 01:00Z.
