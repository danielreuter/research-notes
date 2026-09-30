---
id: 20260930T2140Z-reply-from-nebius-infra-glide-path-rows
campaign: verity
lane: infra
kind: report
status: done
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Steward → infra: my glide-path rows (2:40 PM PDT)

- **Node 1 disk:**
  - `/workspace` (`/dev/vdc`) has 1.6 TB free of 4.9 TB (70% used).
  - `~/.cache/verity-check` holds 115 GB. It sits on the root disk (`/dev/vda1`), which has 68 GB free of 247 GB (73% used).
  - The root disk is the tighter one, so a few more check caches there would fill it.
- **Hourly busy notes:** they now run through 8 AM PDT Oct 1, one per hour in `lanes/nebius-infra/`. The next is at 3:00 PM PDT.
  - If this VM is suspended, an hour is written up to 50 minutes late. The 30-minute steward timer wakes the VM before that.
  - A slot missed by more than 50 minutes is skipped, not backfilled.
- **Alert sink:** it has written to `lanes/infra/` since 11:45 AM PDT. `LANE = "infra"` is live on node 1, and a copy also goes to
  `lanes/node1-dispatcher/`.
- **Where node 1's GPU time went, 10:16 PM PDT Sep 29 to 2:30 PM PDT today (`art:fd2ad8f1`):**
  - Kueue allocated 90.5 of 130 GPU-hours. A process held GPU memory for 38 of them, and the GPUs were busy for 3.4 (2.6%).
  - So most of the loss is pods that hold a GPU without touching it. Right now GPUs 2 and 4 are a TP2 `config-run-row` in its CPU
    Build (the vLLM coordinator's GPU-less 2-rank Build lane covers this).
  - The other six GPUs hold memory but sit near 0%: three Commits that are progressing, and three `backend-sweep-2` `prover-b` pods
    with 93 GB each.
  - Node 2 was 49% busy over the same span.
