---
id: 20261001T0640Z-order-from-compute-accounting-all-overnight-launch
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# GO: the overnight GPU plan, launched at 11:40 PM PDT (Daniel's yes, 11:33 PM PDT)

The plan is in the Project store at `docs/overnight-gpu-plan.md`, section "Compute accounting (PoUW)": six items, about 68 GPU-h.
Daniel approved all of it:
- `-h3` per-row seeds on the served path;
- two new workers, for NCP and for a fresh design;
- served window 2 ahead of 70B if time runs short.

**Who does what:**
1. **Served decode hill-climb:** bc-c62f9726. In order: whole-step CUDA graphs for Pearl-C's calls, the hashing per-call host
   overhead, then `-h3`.
   - Timed windows on node 2 at about 4:30 AM and 7:00 AM PDT.
   - Targets: decode below 2.9× and prefill below 1.5× over graphed stock FP8.
2. **Pearl-C4 on Llama-3.1-8B:** bc-e8ffd7f2. The timed window on node 2 is 3:00–3:30 AM PDT, with 4:00 AM as the fallback.
   The order is `note:20261001T0603Z-…-pearl-c4-llama8b-overnight`.
3. **NCP with a speed target:** a new worker, lane `pouw-ncp`.
4. **A fresh non-Pearl design:** a new worker, lane `pouw-design`, then the red team (bc-d545bc2a) and the assessor (bc-f9af3acc).
5. **Llama-3.1-70B FP8 served:** bc-c62f9726, after item 1. Its timed window is about 6:00 AM PDT, and it yields to served window 2.
6. **Lower FP8 γ:** bc-4323a347 with the assessor. Classify the W1 inventory's 114 unpriced families
   (`note:20261001T0627Z-…-w1-inventory-checks`), then finer floors.

**bc-c066b30c books node 2's timed slots,** each 20–30 min of the whole node:
- 3:00 AM, Pearl-C4 (booked);
- 4:30 AM, served window 1;
- 6:00 AM, 70B;
- 7:00 AM, served window 2.

**Rules for every job tonight:**
- Every job goes through `--queue` with its research question, and uses `--custody-r2 --custody-ttl 8h`.
- Node 1 work ends, or checkpoints to the store, by 5:10 AM PDT. Nothing new starts there after 5:15 AM, and its `/workspace` is
  offline 5:40–5:55 AM. Tell compute accounting by 5:00 AM about anything that will still run past 5:10.
- **GPU priority when GPUs run short** (the top-level arbitrates):
  1. circuits' Commits reclaim GPUs, except during our timed windows and PoUS's timed audits;
  2. timed windows run uninterrupted;
  3. proofs keeps its floor of 2 GPUs;
  4. then our untimed work, then PoUS's untimed work, then proofs beyond its floor.
- Bring any GPU or core conflict to compute accounting in `lanes/accounting`. I take it to the top-level; don't settle it
  between lanes.
- Times in prose are Pacific.
- Keep under the PR cap: open no new PR unless one of ours lands or closes first, and use branches for the work.
- **Checkpoints, one line each in your lane:** 2:05 AM (running, with a first number), 4:50 AM (the timed and long work done or
  safely parked), and 7:50 AM (the morning number, preserved).
