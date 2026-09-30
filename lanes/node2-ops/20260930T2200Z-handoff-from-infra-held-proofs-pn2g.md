---
id: 20260930T2200Z-handoff-from-infra-held-proofs-pn2g
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: infra held 12 of proofs' `pn2g-*` fill jobs, the whole-row guests the research review cut. Don't requeue them without proofs' named question

At 2:58 PM PDT infra moved 12 `pn2g-*` jobs (owner bc-8416bc72, 9 `gpus=1` chunks and 3 stage jobs) from `queue/` to
`/workspace/pouw/fill/held-proofs-pn2g/`. The research-value review had cut them as filler past a few chunks, and Daniel's rule is
that idle beats padded. One `pn2g` job was already running and was left alone. Nothing is deleted.
- **Move them back** only if proofs answers in Slack thread `1790805508.948949` with the job and the research question it answers.
- **Otherwise** infra deletes them on 1 Oct.
- **Not affected:** the 8 `verity-build-cov-*` Builds (kueue-fold's offload, circuits' work) and `verity-commit-cov-g153` (n2-commits,
  circuits' approved Commit) stay queued.
