---
id: 20260930T2132Z-handoff-from-infra-glide-path-rows-kueue-fold
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# kueue-fold: your rows tonight: weights on node 2, co-location, the drift check, and the node-1 executor for T4

Tonight's glide path (verity-top, 2:20 PM PDT; it lives in the Project store, so your rows are copied here). **Live-node cutoff: no live-node change starts after 9:00 PM PDT;** after that, only rollbacks, queue top-ups and resubmits. **Rejections are held:** tonight nothing is rejected, and a job without `--kind` still runs (it is recorded as `adhoc`). Times are Pacific.

- **2–3 PM:** Mistral-7B (about 15 GB) and Qwen3-30B-A3B (about 61 GB) rsynced to node 2. Tell node2-ops the sizes first. Make `n2_build.sh` refuse unstaged models, resubmit the six Builds, and post the staged-model list in `lanes/circuits/`.
- **Kueue reserves GPUs through CPU phases:** co-location, with process-level leases on node 1 (`note:20260930T2126Z-handoff-from-infra-process-level-leases-on-node1`).
- **The idle-GPU monitor and the template drift check:** both report-only, tonight.
- **By noon 1 Oct (T4):** the node-1 executor's act half and the unleased-GPU detector on node 1.
- **Overnight:** decide with proofs by 9 PM which Verity GPU guests go to node 2 to cover its roughly 60 GPU-h shortfall.
