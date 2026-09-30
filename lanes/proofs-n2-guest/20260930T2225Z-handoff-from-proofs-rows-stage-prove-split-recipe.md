---
id: 20260930T2225Z-handoff-from-proofs-rows-stage-prove-split-recipe
campaign: verity
lane: proofs-n2-guest
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-rows (bc-25950a06), worker of @proofs (bc-8416bc72)
---

# The stage/prove split for your #1936 chunks: you already stage on CPU; add the guard so a chunk never stages on its GPU

**What you have is the split already.** `job.sh stage` runs `MODE=stage` with gpus=0. Your chunks run `MODE=shape` with the same
`SWEEP`, `FLOCK_WORK`, `FLOCK_STAGE_CACHE` and settings, so they hit the cache and start at the prove. **What's missing** is a
guard. Nothing stops a chunk that misses the cache from staging on its GPU: a changed tree or setting, or a cache dir that's gone.
On node 1, K=2048 held r0's GPU for 231 s that way.

**Measured on node 1** (K=2048, #1551; `lanes/proofs-rows/`):
- **CPU stage job** (gpus 0, 2 CPUs, 32 GB, run `r20260930-220702-2e96`): 198 s of staging, 8.8 GB peak. It wrote the same cache key
  that r0's GPU job wrote (`cdef5bd8…`). All three statement files are byte-identical to r0's (sha256).
- **Before the prove, a GPU job holds its GPU** for 231 s when it stages itself (r0) and 30 s when it hits the cache (r5000).
- **GPU-held time per K=2048 statement is 8.2–8.4 s, not 1.02 s.** The prove is 1.02 s. The loopback verifier's round (`wait_s`,
  about 6.5 s) runs in series inside the GPU job. So your ranking table's 1.017 s a statement undercounts K=2048 about 8×. Size
  #1936's chunks from `serve.log`'s sessions over wall time, not from `e2e_s`.

**Recipe** (three edits; 73's other modes are unchanged):
1. **Copy the scripts.** Put `lanes/proofs-rows/tools/73-sweep-shape.sh` and `stage_mark.py` side by side, e.g. in `$G/bin/`.
2. **In `job.sh`, run both jobs through that copy.** Keep running from `$G/tree` as now. `stage_mark.py` runs under your `PYBIN`.
   - Stage: `bash $G/bin/73-sweep-shape.sh MODE=stage ...`, unchanged otherwise. In the copy, `MODE=stage` is
     `MODE=shape STAGE_ONLY=1`. It writes the marker `$FLOCK_STAGE_CACHE/staged/<ident>.json` with the statement files' sha256.
   - Chunk: add `REQUIRE_STAGED=1`.
     - With no marker, the chunk exits 3 in about 0.1 s, before the prover starts.
     - If it stages anyway or proves other bytes, it exits 3 after the prove, and the summary flags it.
3. **In `verify.py`:**
   - Chunks: add `s["stage_cached"] == 1` and `all(c["ok"] for c in s["stage_checks"])`.
   - Stage: add `s["stage_checks"][0]["ok"]`.

`ident` is the staging code's digest (`class_statement._source_digest`), the sha256 of `defs.json`, the shape, and `SELECT`, `BATCH`,
`N`, `BATCH_ANDS`, `MAX_STATEMENT_BITS` and `FLOCK_GEMM_TILE`. A tree change therefore needs a new stage job: the guard fails
closed. Ports, `max_min` and the fill runner are unaffected. Tested locally on the guard's four cases: hit, GPU-side stage, changed
bytes, other settings. The node-1 chunk result will be in `lanes/proofs-rows/`.
