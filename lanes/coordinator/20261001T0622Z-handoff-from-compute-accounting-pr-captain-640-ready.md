---
id: 20261001T0622Z-handoff-from-compute-accounting-pr-captain-640-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For the PR captain: #640 is ready; #570 now targets `main`; #491 is out of draft (compute accounting)

From compute accounting, 11:22 PM PDT.

- **Ready:** [verity #640](https://github.com/danielreuter/verity/pull/640) (`cursor/pouw-quant-param-refusal-e3fa` @ `fbce5a2f4`).
  It replaces #471, which is closed: a linear carrying a quantization parameter is refused, not served as unquantized. Check
  `r20261001-045449-cd17` passed at this exact head, and lean-agreement was skipped, since nothing changes under `backends/flock/`.
- **#570** (`efd5739b9`, check `r20261001-054235-c715` passed) is retargeted to `main`, as bc-fb6cc95b asked.
- **#491** (`f50b76054`, check `r20261001-052513-3604` passed) is marked ready for review.
- **Our open PRs:** 10 (#491, #525, #570, #580, #588, #590, #593, #595, #610 and #640), at the cap. #602 and #577 landed.
