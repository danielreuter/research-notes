---
lane: fp4-port-2
kind: handoff
created: 2026-09-24T04:08Z
---
# fp4-nvf4+poseidon2 is green on main's leaf interface: lane/fp4-port @ 1aa1f00e (sys_id 8c6d260c reproduced) — your column 2

**Commit:** `lane/fp4-port` @ `1aa1f00e` (base main @ 24f252b1; 3 commits: 92f7defd, 8729f457, 1aa1f00e). Not merged into main.

**Status (4090 pod vy-fp4-port):** hashed sys_id 8c6d260c reproduced byte for byte (no re-pin); Rust pinned verifier accepts
(`cargo test` 66/66 incl. the fp4-nvf4-hash fixture; every bench dump 7/7 ACCEPT pinned as `fp4-nvf4+hash`); gates 0 failures
(hashed 4 honest / 92 negatives; bare 2048 / 116 / 3015); FS non-ZK dumps byte-identical to lane/fp4-decode-3@6ffa0351
(hashed) and to main (bare). 4090 local coins p4, 4096 VUs: hashed 0.2404 s, bare 0.0613 s (median of 3 alternating rounds).
Details: `lanes/fp4-port-2/*report*`, `kb/fp4-nvf4.md`.

**How to run the +hash cell on your 5090 (sync this commit to the prover pod):**

~~~sh
python -m backends.direct.ligero.run --relation fp4-nvf4+poseidon2 bench-vu --auth included-hash \
  --zk --mode interactive --batch 16384 --total-vus 4096 --reps 3 --target -128 --device cuda --pipeline 4 \
  --auth-cache /workspace/auth-cache-fp4h --out result.json --dump-dir proofs --dump-reps 1
~~~

* `--auth included-hash` goes AFTER the subcommand; the `+poseidon2` suffix alone does not select it.
* Pinned Rust check: build `backends/ligero-verify` from this commit (main's binary has no fp4 hashed pin and would refuse
  the system); `ligero-verify batch --dir proofs/rep1 --system proofs/system.bin` should say `pinned_relation fp4-nvf4+hash`.
* Live verifier: your verifier pod must also run this commit (Python `serialize._runner` dispatches a v5 fp4-nvf4 statement
  to the hashed runner only here, and its Rust needs the pin). The pipelined hashed prover's live path is main's
  `HashedRelationRunner._pipelined(live_statement=...)`; I did not exercise it live (local coins only).
* First run on a fresh 5090 JIT-compiles the hashed fused witness kernel via main's compute_89 PTX route (~46 s cold,
  fp4-decode-3 §3); the warm-up absorbs it.
