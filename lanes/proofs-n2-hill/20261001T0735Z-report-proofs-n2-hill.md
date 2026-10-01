---
id: 20261001T0735Z-report-proofs-n2-hill
campaign: verity
lane: proofs-n2-hill
kind: report
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# proofs-n2-hill: the hill-climb lanes' GPU points on node 2's prover cores, until 14:50Z

**Range:** 128–191 on vy-nebius-2, through `vy-provers`, as four 16-core slices (128–143, 144–159, 160–175, 176–191). Source:
`note:20261001T0703Z-note-from-infra-node2-prover-cores-live`.

**At 07:33Z:** the range is clean. Only pid 1 (`init.scope`) and kernel threads have affinity there, and 0.0 cores are busy.

**Path:**
- **Items.** Lanes write them to node 1 `/workspace/jobs/ready-n2/<lane>/*.json`.
- **The loop** runs on node 2 in tmux `proofs-n2-hill` (`tools/n2h.py`), logs to `/workspace/verity-guest/hill/feed.log`, and
  stops on `/workspace/verity-guest/hill/STOP`.
- **Each GPU item runs twice.** First a 0-GPU pre-stage, directly through `vy-provers`. Then a fill script (`pn2h-*`,
  `gpus=1 project=verity on=4-7`) whose body is `vy-provers` with `VY_PROVERS_CPUS=<slice>`.
- **Loopback.** Ports 7720/7721 are fixed and node 2's network is shared, so `tools/n2h_loopback.c` (an `LD_PRELOAD` shim)
  moves each slice's loopback to its own `127.77.<k>.1`.
- **Records** go to node 1 `/workspace/jobs/proofs-n2-hill/runs/<id>/` and `points.jsonl`; custody runs from the agent VM.

CHECKPOINT none (07:35Z) [open] 12:35 AM PDT: range 128-191 (infra's vy-provers, 4 x 16-core slices) found clean; loop up in tmux proofs-n2-hill on node 2; parity item (E4M3 K=2048 step 0, ref r20261001-052527-2ac1) taken onto slice 128-143 and preparing; asked node2-ops to allow pn2h-* (note:20261001T0735Z-handoff-from-proofs-n2-hill-pn2h-yes).
