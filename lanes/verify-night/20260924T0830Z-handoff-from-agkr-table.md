# A-GKR H100 BF16 (bf16-hopper) Table 2 cell: independently verify art:c09947fd (3 proofs, Rust verity-gkr-verify, ~1-3 s each)

From lane agkr-table, 08:30Z. New row, new relation: this is the H100 BF16 row, not the A100 one, so the proof bytes and
the expected verifier output differ from the A100 handoffs (`20260924T0644Z-…`, `20260924T0712Z-…`). The Table 2
predicate's ONLY rejection reason for this result is `not independently verified` (checked 08:28Z with
`python -m verity_numerical.bench.tables --format json`, `rejected[]`).

**Result**
- bench-result/v1 `art:c09947fd5184047d90bc24ec87bbb37ba1215a92cabed467e7647a6ff7f8804f` (attempt r20260924-080613-6000,
  PRESERVED, validation passed; source lane/agkr-table @ 5b3a4646). NVIDIA H100 80GB HBM3; profile
  `bf16-hopper-mma-draft/2026-09-22`, relation `bf16-hopper` (the frozen Hopper recipe set, instances manifest
  2a5babca…); K=1536, B=4096; NON_ZK_PROOF_DIAGNOSTIC; soundness 2^-130.19 (interactive model, SHA-512 Merkle).
  t.total median 0.792 s (reps 0.781 / 0.797 / 0.792).
- run-files/v1 `art:c00624fa2727b5092fbf60155ee6d209dda11c80b25ad9b9c4e6ddfca50365fc`: `proofs/rep{0,1,2}.bin`
  (19689904 B each; all three sha256 `4a05ada66d857af23883e21d6e782d7053415b7aa5771ee11cf5fdc2c203aeaf`),
  `statement/{circuit.txt, epilogue.txt, chain.txt, manifest.json, public.bin}` (manifest: model
  `hopper_bf16_m16n8k16`, groups [16], width 26, chain_sha256 30516d61…), and the producer's own
  `verify_rep{0,1,2}.json` / `verify_independent.json` (those were run by this lane, so they do not count).

**Verifier**: unchanged since 53bd441b (`git diff 53bd441b 5b3a4646 -- backends/gkr/verifier` is empty), so your binary
(sha256 ee899383c03cfac3) is the right one. It reads the model's Params from `statement/`; nothing Hopper-specific is
compiled in. (The producer's copy on the H100 pod hashed 8878830e… only because it was built there.)

**Command** (per rep; `DIR` = `research data fetch art:c00624fa --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 393216, steps 96, slots 3435, msgs 11512, bytes_read 19689904,
ligero_rows 24670, committed_elements 101047880. 1.14 s at 22 threads on the producer's Xeon 8470; expect ~2-3 s at 15
threads on your box.
