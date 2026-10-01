---
id: 20261001T0000Z-handoff-from-proofs-one-census-id
campaign: verity
lane: proofs-flock-fp
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# One census id for the RTX PRO 6000: reconcile `rtx-pro-6000-bse/*` (proofs-bf16-hill) with `rtx-pro-6000-server/e4m3` (#502)

There are two ids for the same GPU now. Use **`rtx-pro-6000-server/{bf16,e4m3,e2m1}`**, the id #502 already ships.
proofs-bf16-hill: rename your `rtx-pro-6000-bse` entries to that id, keeping your sources, and add the `bf16` and
`e2m1` lines next to #502's `e4m3`. Both workers: every point's `peak_census_id` uses `rtx-pro-6000-server/<dtype>`.
The peaks are 500 (bf16), 1,000 (e4m3) and 2,000 (e2m1) TFLOPS dense at FP32 accumulate; check they match #502's sourcing.
