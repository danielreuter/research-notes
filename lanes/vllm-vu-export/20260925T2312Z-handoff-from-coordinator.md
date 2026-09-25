---
lane: vllm-vu-export
kind: handoff
from: coordinator
created: 2026-09-25T23:12Z
---

# Every export records the tree it read from (commit sha + dirty flag): pre-epoch rows carry pre-epoch Program digests

Record in each export's metadata the source tree it was produced from (`git rev-parse HEAD` of the checkout, whether it
was dirty, and the branch), and for each row the epoch its Program digests belong to. Rows recorded before the re-baseline
epoch (Ampere k16 step v1 -> v2, c2's tip dedf5313) carry pre-epoch Program digests, so a consumer must be able to tell
which tree and epoch a digest came from. You're in the mirror list now (CLOUD-LANES.txt), so your checkpoints reach the
steward within ~5 min.
