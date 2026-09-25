---
lane: b-ligero-standard-hash
kind: handoff
from: b-ligero-sha256
---

# SHA-256 half: first cell preserved; bf16-hopper-x4+sha256 pinned; vllm-v1 deferred (design only)

For your standard-hash table, the SHA-256 column. Full ids are in `lanes/verify-night-2/20260925T1150Z-handoff-from-b-ligero-sha256.md`.

**fp8-hopper-x4+sha256** (H100, l4096 p4, `--commit-per-rep`, sweep plateau 32768 VUs):
- Timing: t.total 5.077 s + commitment 0.240 s = e2e 5.317 s, 6162 VU/s.
- Overhead and soundness: e2e overhead vs native peak 1.045e8, 2^-128.07.
- Size: m = 89,356 rows per column, 6.68x the bare relation's 13,383. The SHA-256 gadget is 18,128 rows per block.
- Artifacts: bench-result art:4aa258ee…, proofs art:61842848…, both PRESERVED. Tree da74b03e, now in main 767115db.

**bf16-hopper-x4+sha256:**
- PINS row b009fdc8 (not in main yet: a one-row cherry-pick), m = 88,381.
- Gate: 13 honest sub-batches + 86 negatives, 0 failures.
- Re-sweep 5a5f: plateau 8192 VUs, 3062 VU/s, Rust 49/49 ACCEPT. Ids follow.

**Custody lesson:** a failed runner custody push (`RemoteDisconnected`) can leave the pod's store without most of a tree's
blobs (271 of 299 here). `data push` then fetches each missing blob from R2 serially, and those GETs stalled at ~24 MB.
- Fix: re-ingest the blobs from the run dir (`evidence/pod-scripts/61-blob-census.py ART TREE --ingest`), then run
  `data push RUN --verify head`.
- The objects were in fact all on R2 already.

**vllm-v1 position leaves:** not built.
- 26-byte prefix `verity/pos-leaf/v0 || u64be(len)`. The blocks straddle columns at offset 38, so there's no verifier-side
  midstate, and all 25 compressions per leaf are in-circuit.
- That needs a third gated compression slot per column (~1.4x the hash rows), a vllm-v1 tree in hashauth, and a Rust leaf
  change.
- Design note is in my report.
