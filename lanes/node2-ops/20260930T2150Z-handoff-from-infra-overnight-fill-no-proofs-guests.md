---
id: 20260930T2150Z-handoff-from-infra-overnight-fill-no-proofs-guests
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: proofs' whole-row guests are cut, so none go to node 2. Plan the overnight fill from three sources, and leave GPUs idle rather than pad them

The research-value review (the old research coordinator, about 2:45 PM PDT) cut proofs' Llama-3.2-1B whole-row guest jobs: past a few
chunks they were filler. This supersedes the "Verity GPU guests" line in `note:20260930T2132Z-handoff-from-infra-glide-path-rows-node2-ops`.
Node 2's roughly 60 GPU-h overnight gap is mostly open again.

**Fill, in the reviews' ranked order:**
1. **The assessor's W1 search, which lifts `w1-complete/sm120`:** about 30 GPU-min once it's coded. It arrives through PoUW (compute-accounting).
2. **bc-2aa33ad8's overnight backlog,** due 10 PM PDT, with a GPU 3 run on 16,384-wide units. compute-accounting's keeper, bc-829aa649,
   queues it.
3. **Circuits' 1-GPU Commits for the small models staged on node 2,** once n2-commits (bc-698052e1) passes the environment check
   (driver, vLLM pin `d9105ea80`, clock state recorded). They run as `gpus=1 project=verity` guests, with their CPU replay on node 2.

**Rule (Daniel):** an idle GPU beats a padded one, so don't backfill with filler. If the queue is under 12 GPU-h, report the gap
and its owner every hour, and leave the GPUs idle. For T2 (6 PM) and the morning readout, report useful GPU % honestly, with idle time
shown as idle.
