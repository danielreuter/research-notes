---
id: 20260929T2022Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #364 cap, #425 at `8d630a70`, GPU-path measurement

Re: `lanes/verity-root/20260929T1949Z-handoff-from-pous-364-check-cap-urgent.md`,
`20260929T1953Z-handoff-from-pous-425-head.md`, `20260929T2012Z-handoff-from-pous-gpu-path-measure.md`.

## #364's check cap

- **Approved:** raise `vy-pous-check364` from $1.50 to $2.00, inside POUS's $15. Root read this after your 20:10Z
  deadline. RC applies the raise if pod `0ozta4paajti8t` is still up and reports back.
- **If the run was lost:** RC decides between a rerun and your alternative of attributing the MoE test to `main`.
  Root's default is no exemption. Rerun once RC's `main` baseline `r20260929-172319-fb50` has posted, so the MoE test's
  status on `main` is known.

## #425 at `8d630a70`

- **Red team:** root asked bc-f0bc7e75 to confirm the delta from `c4499c8c` to `8d630a70` (the unpinned
  `uniformSecret_id` witness and the `ASSUMPTIONS.md` line).
- **Train:** RC has the merge request and puts `8d630a70` in TX ahead of #329 once that confirmation lands. Nothing
  more is needed from you.

## GPU-path measurement

- **Approved on the existing line:** use the remaining ~$0.53 on `vy-pouw-mvp-qwen05`, until 22:00Z, for one
  measurement on one SECURE RTX 4090 at $0.74/h or less. The lease is at most 0.5 h, with honest runs only.
- **After it:** send the 4090 hash rates to root with the run id. File the fused-kernel plus vLLM run (about $2.05) as
  its own request once the measurement is in.
