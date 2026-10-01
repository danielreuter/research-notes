---
id: 20261001T1135Z-reply-from-proofs-bf16-hill-ladder-done-what-next
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: proofs-bf16-hill (bc-89f3138c)
---

Re `note:proofs-bf16-hill/20261001T0730Z-handoff-from-proofs-750-is-a-deadline-not-a-stop`: every K's environment levers are
measured, so the BF16 ladder is done, and here is what I'd run next. Nothing of mine is queued or running on either node.

**Where each K stands** (overhead; node 2 raw, then /0.95):

| K | node-1 best | node-2 best |
|---|---|---|
| 2048 | 4.20e7 (3265, s12 HS_DMA; s6 4.25-4.36e7 is the same within noise) | 4.36e7 (af2b; 4.59e7) |
| 4096 | 2.30e7 (188b, s3 re-run) | 2.20e7 (bf9b; 2.32e7) |
| 8192 | 2.32e7 (ec06, s7) | 2.24e7 (a7b2; 2.36e7) |
| 16384 | 2.61e7 (6c85, s4) | none |

Clean step 0 to step 1 (the column-major fold): K=16384 5.82e8 (ef42) to 1.83e8 (e54c), 3.2x; K=8192 2.84e8 (3cd7) to 1.47e8
(a814), 1.9x.

**Measured and done:** the fold, verifier overlap, structured lincheck, 2 verifier servers, device prefetch, pipeline depth 2,
HS_DMA (neutral at K=2048, a loss at K >= 4096), and RUNS=96 (a measurement check). Tiles are stopped (0822Z).

**Where a session goes now.** Medians of 24 timed sessions, 2 reps each, at the best points:
- A session costs about one prove. The gap between end-to-end and prove time is 0.01-0.03 s at K <= 8192 and 0.07 s at
  K=16384 (6c85).
- The prove takes 0.68-0.76 s at every K. Zerocheck is 30-33% of it and Ligerito 24-30%, so 55-62% together, both on the GPU.
- Encoding commitment is 12-14%, ring switch about 10%, and witness 9-14%.
- Lincheck grows with K: 4.2% at K=2048 (0.028 s) to 9.6% at K=16384 (0.073 s).

**What I'd run next, in order:**
1. **K=16384 s4, re-run once NUMA node 1 has room.** 5c86 (3.66e7) and a048 (3.94e7) had the same prove-only overhead as 6c85
   (2.49e7). Their session gaps spiked to 1.2-3.6 s against a steady 0.8 s, with 21 GB free on NUMA node 1, compact_stall at
   6.2M and pgsteal_direct at 213M. That is host memory pressure, not the step, and no flag catches it. My recommendation: a
   flag like cpu-slice-shared, from the compact_stall and pgsteal_direct deltas over the timed sessions, so a stalled point
   doesn't count. That changes the cell-count rule, which is yours to decide; I haven't added it.
2. **Prover code, now that the environment levers are spent.** First zerocheck and Ligerito (55-62%): an nsys profile of one
   K=2048 session for kernel occupancy, which is cheap and needs no new statement. Then the prover's lincheck at K=16384, the
   one bucket that scales with K. Both need C-Flock prover changes, which belong to flock lanes rather than environment
   points, so this needs a route from you.
3. **Tiles: wait for Daniel's ruling on cross-Call grouping** (already on his list). If tiles resume, the stager should refuse
   a tile whose units per verifier unit (VU) are not a power of two. The 3x2 tile (6 per VU) failed only at the verifier.

I'm not submitting item 1 yet. A point recorded now would stay in my local store: 0d6a's record step exited 1 with no remote.
Once the store's remote is back, tell me and I'll place it at or after 12:55Z, if NUMA node 1 has room.

The store's remote is missing from my VM. Since this session resumed at 10:55Z, the Cursor secrets (RUNPOD_API_KEY,
RESEARCH_NOTES_TOKEN, the store's keys) are absent from my shells, and ~/.runpod/ and ~/.research/store.toml were gone at
about 11:01Z. I haven't recreated them. 0d6a's 4 labels are in my local store only; `research data push --pending` sends them once the
store's remote is back.
