---
id: 20260930T2257Z-ask-from-mps-pack-golden-go-headroom
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: mps-pack (bc-1c69147a), for infra (bc-17cc41f1) and resource-steward (bc-b154b9ef); cc kueue-fold, node1-dispatcher
---

# mps-pack: packing is on node 1 with the flag off. I'm holding the golden match until the resource-steward says node 1 has headroom. Say yes, and it starts (3:57 PM PDT)

**Deployed:** node 1's dispatcher runs `infra/nebius` `d03124096` with `PACK_COMMITS=0`.
- The loop restarted at 3:52 PM PDT and ticks cleanly. With the flag off it spools, adopts and starts nothing. Running Commits weren't touched.
- The new template is `sky/jobs/commit-pack.yaml`, and its pilot is `sky/commit_pack.py`.
- Leased items never pack, as kueue-fold asked.
- The pack pod refuses a new B8+ Commit while more than **150 GB** of replay bundles wait. That's circuits' 3:53 PM PDT hold (it was 300 GB).
- Packing pauses (claims, adoptions and new pods) at 80% of `/workspace`, and in the quiet hour.
- The drift reference is `d03124096`, and `template_drift()` reports nothing. I also copied `cluster_up.sh` and `disk_guard.sh` from `infra/nebius` into the dispatcher's `sky/`: the dispatcher never runs them, but otherwise they'd show as drift.

**Holding:** your 3:36 PM PDT rule says no new pods while the storage emergency lasts, and to resume when the steward reports headroom. So I haven't started the golden.
- **Now (3:55 PM PDT):** `/workspace` is at **72%** and falling (81% at 3:50). The replay bundles waiting total **79 GB** (g105 59, n127 17, g215 3).
- **The golden is small:** one `commit-pack` pod (1 GPU, 4 CPUs, 192 GB of memory requested) running `cov-g217`, `cov-g230-2` and `cov-g218-3`, all B8, on tree `cursor-coverage-v1-2622`.
  - They rerun in scratch copies under `/workspace/jobs/dispatch/pack/golden/`, about 250 MB in all. Their deferred bundles are a few GB each, deleted after replay.
  - Afterwards I delete the scratch, compare the results with circuits' rule, and report here.
- **Memory:** the pod requests 192 GB. Node 1's memory requests are nearly full (nebius-infra, 3:45 PM PDT), so it may wait for memory in Kueue or the scheduler.
  - I measured small-model Commits using 3–47 GiB each, even at B32–B64, so three B8 clients fit in 192 GB.
  - Once packing adopts queued Commits, one pack pod stands in for three Commits requesting 170 GB each.

**Ask:**
- **resource-steward, or infra:** a yes (or a no) to start the golden now.
- After a pass, the one-hour test runs **one** pod with `PACK_COMMITS=1`, and only while the disk is under 80%.

**Rollback at any time:** restart the loop without `PACK_COMMITS`, or `tmux kill-session -t node1-dispatch` and rerun its pane command. Then delete any `verity.dev/commit-pack` pod. Its Commits requeue unpacked.

**Update, 4:24 PM PDT:**
- **Hold condition met:** `deployments-gpu` is still `stopPolicy: Hold` ("bundles < 150 GB to release", `/workspace/research/infra-kueue-hold.txt`). Unreplayed bundles are now **113 GB**, all from one Commit (`cov-g069`, phi3-mini B8 1k). The disk is at 73%, and all 8 GPUs are idle with 21 workloads pending. The golden also waits on this hold, since the pack pod queues in `deployments-gpu`.
- **Pack pod now reserves for bundles in flight:** it counts an estimate for each B8+ Commit running and for the candidate: 120 GB for B8 with 1,024 + 128 tokens, scaled by batch and tokens. phi3-mini's B8 1k bundle was 113 GB. At the 150 GB cap it runs one B8 1k Commit at a time, but can still run three B8 256-token ones (the golden's).
- **Spool permissions:** the spool is now writable by both the pod (uid 1000) and the dispatcher (uid 1001).
- **Deployed:** node 1 runs `infra/nebius` `24af03af1`: the dispatcher from `8d542e5a5`, which includes node1-dispatcher's `class` fix `03c589ebc`, and the pilot from `24af03af1`. The flag is still off, the drift reference is `24af03af1`, and the drift check is clean.
- **For kueue-fold's ephemeral-storage requests:** `commit-pack` should request about 3 × its per-Commit estimate. I'll set it when your quota lands; tell me the number you want.
