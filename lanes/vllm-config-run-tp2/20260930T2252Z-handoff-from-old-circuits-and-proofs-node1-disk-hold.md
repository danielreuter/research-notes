---
id: 20260930T2252Z-handoff-from-old-circuits-and-proofs-node1-disk-hold
campaign: overnight-sep30
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-ecac3029)
---
# Node 1 disk emergency: hold staging on node 1 now

Infra (Slack 1790808720.423549, 3:53 PM PDT): node 1's /workspace is at 81% and growing about 1.2 TB/h. All node-1 ClusterQueues are on Hold (marker /workspace/research/infra-kueue-hold.txt).
- Don't start any new `research run` staging or out-of-Kueue job on node 1 until that marker is gone.
- No B8 or larger `--replay-deferred` Commits anywhere on node 1.
- If a job of yours is writing more than 10 GB on node 1, say so in a -handoff- to lanes/old-circuits-and-proofs/ with its path and size.
- Node 2 is fine for guests (n2_build.sh / n2_commit.sh) outside PoUW windows.
