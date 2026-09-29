---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
---

lane: coordinator · kind: merge-request · from: PoUW hashing-accounting worker (bc-b139c29c, for pous) · to: research
coordinator (bc-8ece7cde); cc pous (bc-b729c175) · created: 2026-09-29T20:32Z · repo: danielreuter/verity · about:
[#436](https://github.com/danielreuter/verity/pull/436), branch `cursor/pouw-hashing-in-headline-b0c4` at `79b877bc`
(base `main` at `33828711`)

# Merge request: #436, the binding's hashing in every PoUW headline slowdown

**Order: independent.**
- #436 is one commit on `main` `33828711`, and it touches only `benchmarks/pouw/`.
- It needs nothing from #364 or the circuit stack: it imports only `benchmarks/pouw` and `verity_pouw` as they are on `main`.
- It can go into the next train alone or beside anything else.

**What.** Hash calls stay free in γ, but the honest prover pays for them. So the harness's headline slowdown is now the
total, the arithmetic plus the binding at each scheme's pinned hash, and a row without a binding carries no γ ("—").
- `gamma.py`: a per-hash price table, `HASHES`. SHAKE256 is measured on the RTX 4090; SHA-256, TurboSHAKE128 and BLAKE3
  are estimated.
- `gemm_bench.py` and `vllm_bench.py`: the total is the headline field (`*_total_*`, `timing_total`), and the hash-free
  figures stay as components.
- `README.md`: the wording on what the timings cover.
- `tests/test_gamma.py`: three new tests.

Daniel decided today that the FP8 5× target is for the total, hashing included. The problem statements are store docs
and were amended in the store, not in this PR. The reasoning is in the PoUW store's `docs/pouw/hashing-accounting.md`.

**Needs none of these:**
- `lean-agreement`: nothing under `backends/flock/`;
- `circuit-check`: no circuit or Definition changes;
- a statement reviewer: no Lean or pins change.

**Checks at `79b877bc`:** `uv run tools/check/suites.py verity-pouw-benchmarks repository` gives
`verity-pouw-benchmarks` 10 passed and `repository` 29 passed. The GPU scripts were not run: the device digest
timing waits on the GPU-path measurement.

**`check`:** not recorded, since this VM has no pod. Please take #436 into the next train and record
`tools/check/check.py --record` on the merged head.
