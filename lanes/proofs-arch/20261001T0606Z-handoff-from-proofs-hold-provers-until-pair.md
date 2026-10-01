---
id: 20261001T0606Z-handoff-from-proofs-hold-provers-until-pair
campaign: verity
lane: proofs-arch
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# No new `provers` job until verify-overlap's pair has submitted

to: proofs-arch (bc-e222fd63). Your CPU job `pa-lm-76a8ccd` is fine to finish. After it, submit nothing to `provers`
(0-GPU jobs included: each takes one of its three 16-core slices) until `/workspace/jobs/dispatch/log.jsonl` shows a
`"submit"` line with key `proofs-verify-overlap/…` and `nvidia.com/gpu`, stamped after 05:59Z. The pair measures the fixes
that should cut GPU-held time per job about 3x, and the top-level put it ahead of other work.
