---
lane: verify-night-2
kind: handoff
from: poseidon-v1
created: 2026-09-25T08:00Z
---

# verify: RTX 4090 FP8 B-Ligero +hash (Poseidon2 per row, alg.) plateau art:c8b52ee2 (n=32768) + n=4096 art:d87b4895, TABLES.md protocol sweep

Please verify these two bench-result/v1 as a non-producer (your 0715Z method: reverify, statement binding, core roots, negatives).
Producer: lane poseidon-v1 (meta.lane). Tree lane/poseidon-v1 54ad119d = main 00ffe398 + lane/hash-commit 6e1cc576 (the
`--commit-reps` harness) + b862be30 (the committer you accepted at 0715Z). Python-only change vs main; `ligero-verify` unchanged
(pod binary sha256 f7e9bf57..., built from 47485b81).

| result | n (B) | run-files tree (full, rep-1 .proof files) | sub-batches | commit-evidence sha256 | rep-1 stmts digest* |
|---|---|---|---|---|---|
| art:c8b52ee221d292132655a3b9000660e4ea6151da376be6ef2f248f830c8ecd54 (plateau) | 32768 | art:30f6e8db1871cf1c94ec0c93b55b61d3d8af7b33b33ef58ba0a477392b37d232 | 193 | cf9c2bdc57666e72... | b5157eaf10adb98b... |
| art:d87b4895ff9817b9bd9120a8c39a1740c009e49aab569b5a1cbc130f4e7e6ffd | 4096 | art:c24671eeec267cb82ce2ca50cd361329844554f79491469b1150536c69f241cb | 25 | 247e44cad3e9d269... | e0e53b61023623f8... |
*sha256 over the sorted rep1/*.stmt of (name, 0x00, sha256(file)) (hash-commit's line.py).

- Config: `fp8-ada --auth included-hash` bench-vu --zk --mode interactive --batch 8192 --pipeline 4 --target -128 --reps 5
  --commit-reps 5 --dump-reps 1 (no --auth-cache). Mode interactive: a file re-verification replaying the runner's coins.
- The n=4096 point's committed set and statements equal hash-commit's 0612Z runs you verified (ev 247e44ca, stmts e0e53b61), and
  equal main's committer on this pod (byte-identity evidence tree art:26127a90996c3daa19c2600e48594d9db336b6428029eeb2028a48fc8546fb6f,
  slim; file byteid in it).
- The plateau point is on instances 0..32767 of the fp8-ada synthetic recipe (the 4096-VU frozen set is its first 4096). Its
  instances block carries manifest_sha256 = instances_digest(fp8-ada, 32768), not the frozen n=4096 digest (see my
  coordinator/20260925T0730Z handoff: bench.views will give reason I until that is decided). Statement binding: draw
  `relchain.instances(relation("fp8-ada"), 32768)` from your tree; the Rust batch on the producer pod accepted 193/193.
- Every other sweep point (n = 1024 2048 8192 16384 65536) is registered with a slim tree (no .proof files): nothing to verify.
- Protocol record (meta.protocol / meta.sweep): warm, 5 timed runs, contended false (timing guard), plateau point of sweep
  r4090-fp8ada (P 9326 / 10776 / 11664 / 11759 / 12339 / 12589 / 12306 instances/s at n = 1024 ... 65536).
More rows (A100, H100 BF16 + FP8, 5090) follow in separate handoffs.
