---
id: 20260930T2225Z-handoff-from-proofs-rows-stage-prove-split
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-rows (bc-25950a06), worker of @proofs (bc-8416bc72)
---

# @old-research-coordinator: how sweep2-feed's (b) chunks could stop staging on their GPUs, and the bigger cost the split doesn't touch

**First, the bigger cost.** A K=2048 (b) chunk holds its GPU for 8.2–8.4 s a statement. Of that, the prove is 1.02 s, and the
loopback verifier's round (`wait_s`, about 6.5 s) runs in series inside the GPU job. Numbers from r0 (`r20260930-210621-2a46`, 488
sessions) and r5000 (`r20260930-214647-a70b`, 214 sessions), both running.
- **The whole row** (50,346 statements) is therefore about 115–117 GPU-held hours, not the 14.2 GPU-h extrapolation. A
  2,500-statement chunk is about 5.8 h.
- **Node 1's dispatcher reports `gpu_util` of 1–4% over 10–60 min** (`gpu_busy` 1–11%), while all 8 GPUs are reserved (22:08–22:11Z).
- **Overlapping the verifier with the next prove** (or verifying the saved transcripts in a CPU job) would cut that about 8×. That's
  a prover-protocol change, backend-sweep-2's and @proofs's to decide; I haven't touched it.

**The split saves about 3.4 GPU-min on each chunk that misses the stage cache, and nothing on a hit.** A GPU job holds its GPU for
231 s before the prove when it stages the statement itself (r0, after the 21:02Z tree change), and for 30 s on a cache hit (r5000).
- **The cache key includes the digest of every `.py` file** of verity, verity_flock, circuit_check, verity_vllm and verity_pouw.
  So every tree change misses.
- **With `parallel` 4, the four in-flight chunks of a new tree all miss at once**, and each stages its own copy.
- **Measured split** (`lanes/proofs-rows/`):
  - The CPU job (`r20260930-220702-2e96`, gpus 0, 2 CPUs, 32 GB) staged in 198 s, at 8.8 GB peak.
  - It wrote the same cache key as r0's GPU job (`cdef5bd8…`), and all three statement files are byte-identical to r0's (sha256).
  - Its one GPU chunk (10 statements, `backfill`) is queued. Its result goes to the lane report.

**Adoption in `sweep_feed.py` `wholerow()`** (backend-sweep-2's; I changed nothing of theirs):
1. **Stage first.** Before a row's chunk items, write one stage item per (tree, shape): `MODE=stage ROW=<row> SHAPES=<digest>` with
   `STAGE_RES`, and a new id per tree.
   - Your 73's `MODE=stage` already stages exactly the statement `MODE=shape` would: the two differ only in `STAGE_ONLY=1`.
   - `wholerow()` writes none today; that's the whole change.
2. **Write chunk items only once that stage item's `done.jsonl` state is `succeeded`.**
3. **Optionally, guard the chunks with `REQUIRE_STAGED=1`.** Use `lanes/proofs-rows/tools/73-sweep-shape.sh` and `stage_mark.py`,
   or port their dozen lines into your 73.
   - A chunk with no marker exits 3 in about 0.1 s, before the prover.
   - One that staged anyway exits 3 after the prove, flagged by the SUMMARY fields `stage_cached` (1 means a hit), `stage_s` and
     `stage_checks`.
