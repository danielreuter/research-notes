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
CHECKPOINT none (08:00Z) [open] 1:00 AM PDT: parity decided (note:20261001T0755Z-finding-node2-parity): E4M3 K=2048 x3 on node 2 vs r20261001-052527-2ac1, overhead/GPU-held mean -2.0%, verify -4.3% -> node-2-only (MXF4 check queued); handoffs to proofs-flock-fp, proofs-bf16-hill (ready-n2/<lane>/ open) and proofs-arch (its item ran, rc 0); custody labels each GPU point node-2-only.
CHECKPOINT none (08:15Z) [open] 1:15 AM PDT: proofs' 08:02Z ruling applied: node-2 points count beside node 1's on overhead (FP4 back to node-2-only if MXF4 K=2048 parity's mean overhead is off >3%); 3 GPU points relabelled (note + hardware, by proofs-n2-hill), custody labels new ones from tools/n2label.py; cutoff moved to 17:00Z (loop restarted 08:04Z, RANGE comment updated), windows 15:00/15:30/16:00Z and keep-free GPU 7 honoured; lane notes to proofs-flock-fp, proofs-bf16-hill, proofs-arch; 4 slots hold staged GPU points waiting for GPUs (Commits hold most), 3 bf16 + 5 fp items waiting for a slot.
CHECKPOINT none (09:00Z) [open] 2:00 AM PDT: proofs' 08:18Z tasks: 5 node-2 copies held in ready-n2/<lane>/held/ (+ MXF4 K=8192 step 1 withdrawn), notes to bf16-hill and flock-fp; main's full-K stage check placed on node 1 08:58Z, run r20261001-085949-c20c on slice 160-175; MXF4 K=2048 parity +9.4% overhead -> FP4 node-2-only (FP4_NODE2_ONLY on node 1), 2 repeats running; offset rule (08:30Z) labelled on all 27 node-2 GPU points; infra's 92-123 slices live since 08:43Z (6 slots); reply note:proofs/20261001T0900Z-reply-from-proofs-n2-hill-held-confirm-running-fp4-node2-only.
CHECKPOINT none (09:45Z) [open] 2:45 AM PDT: MXF4 K=2048 parity mean of three +6.7% overhead (+9.4, +4.9, +5.7%) -> FP4 stays node-2-only, labels cite the mean; 92-123 returned to circuits by proofs_lend.py at 09:24:26Z (circuits-range load 61), no point running there then, loop back to 4 slots; fold + lincheck grants (note:proofs-n2-hill/20261001T0910Z-handoff-from-proofs-fold-and-lincheck-granted-drop-both-flags): n2-hill has no gemm_hill.py or roll-ups of its own, node-2 points' flags come from the lanes' trees and the lanes re-label their roll-ups, nothing to change here; flock-fp moved MXF4 K=8192 step 1 back from held/ (ran 09:29Z, a node-2 baseline); main full-K check r20261001-085949-c20c: BF16 4/4 and E4M3 3/4 equal so far.
CHECKPOINT none (10:25Z) [open] 3:25 AM PDT: main full-K stage check r20261001-085949-c20c done (rc 0, 10:21Z): all 16 (class, K) equal to node 1's records, outputs art:adcd31bcc27d12dc280f949115d38740cc68fe5c5a8b128c28ff9063a7670811, notes to red-team-proofs-554 and proofs; Q3c grant (note:proofs-n2-hill/20261001T0948Z-handoff-from-proofs-q3c-granted-drop-c0-once): n2h writes no flags of its own and ships each item's tree per commit, so bf16-hill's accepted fix reaches node 2 with its next items; loop on 128-191, custody running.
