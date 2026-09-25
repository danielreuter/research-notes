---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-epoch
created: 2026-09-25T17:50Z
---
# epoch: deadline ask (pods past 20:30Z) and scope

- **Pods need the vyv- deadline past 20:30Z: until about 2026-09-26T01:30Z.** The MoE rows are the long pole: #67 and #68
  (1x L40S each, PAIRS=1) run Build ~2.7 h + Match ~0.7 h + Commit ~1.5 h from about 18:30Z (after bootstrap), so they end about
  23:30Z; `rebaseline.py run/table/write` follows on the pods that recorded the rows. Expected last row end: ~23:30Z.
- Pods (all `vyv-rf-epoch-*`, registered, guard 90): moe67 `mzp252g5m1qswn`, moe68 `4ltk4vvdjnoq3o`, g1 `k9n58r873y9d0s`
  (1x L40S $1.09/h each), tp70 `m635zk3ooaylcm`, tp75 `3svupto9cex43o` (2x L40S $2.18/h each); g2 (1x L40S) and h100 (H100 SXM)
  still retrying on stock. About $9.7/h once all are up; lane estimate ~$55 of the $110.
- Recording tree: `lane/vllm-rf-epoch` @ `a784d421` = b4c `5494e29f` + `30427930` (c2b `dedf5313`, Ampere v2) + `a784d421`
  (C3/D12: profile id without pod id; profile-fallback raises).
- **Deferred as larger than S** (details in `lanes/vllm-rf-epoch/STATE.md`): 2c (`sm89-eager` label from probed capability),
  3 (G1–G8 artifact key names: two namespaces, ~30–40 files, no agreed name map), 4 (host `chunk-leaf-v1` label: the padding
  leaf rule is keyed off the same label, so it needs a label/rule split first; none of the 13 rows uses a host committer).
  Golden corpus re-record (item 5) goes in its own commit, flagged owner review.
