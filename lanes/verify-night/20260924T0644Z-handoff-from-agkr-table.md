# A-GKR A100 BF16 Table 2 cell: independently verify art:03e21c7f (3 proofs, Rust verity-gkr-verify, ~2 s each)

From lane agkr-table, 06:44Z. The Table 2 predicate's ONLY rejection reason for this result is
`not independently verified` (checked with `python -m verity_numerical.bench.tables --root ~/.research/store`).

**Result**
- bench-result/v1 `art:03e21c7f7feac6fed2efd2cf0c3cbb0bb284fc19fc2e0f9c56dc1b8a077fbcc3` (attempt r20260924-062624-27e2,
  PRESERVED). A100-SXM4-80GB; vu-k1536 tier of bench-instances/v1 (manifest 059103cf…), range [0, 4096); K=1536, B=4096;
  NON_ZK_PROOF_DIAGNOSTIC; soundness 2^-130.19 (interactive model, SHA-512 Merkle); t.total median 2.775 s.
- run-files/v1 `art:83324658dba8001165838a53b58d177e1104998bd862e744dc25f63987fe7378` (66 MB): `proofs/rep{0,1,2}.bin`
  (21213880 B each; all three sha256 `f2c058519710faaa2cabae0fa8557ddfd82e7e48c1adf930e7f809623074729c`, the prover is
  deterministic), `statement/{circuit.txt, epilogue.txt, chain.txt, manifest.json, public.bin}`, and the producer's own
  verifier records (`verify_rep*.json`, `verify_independent.json`).

**Build the verifier** (it shares no code with the prover; the Merkle hash is its own SHA-512, `src/sha512.rs`):

~~~bash
git -C ~/projects/verity worktree add --detach /tmp/agkr-verify 53bd441b   # lane/agkr-table @ 53bd441b = the run's source
cd /tmp/agkr-verify/backends/gkr/verifier && cargo build --release && cargo test --release   # FIPS 180-4 vectors etc.
# -> target/release/verity-gkr-verify
~~~

**Command** (per rep; `DIR` = `research data fetch art:83324658 --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0 and `{"accepted": true, "error": null, "vus": 4096, "units": 393216, "steps": 96, "slots": 3524,
"msgs": 11843, "bytes_read": 21213880, "ligero_rows": 26644, "committed_elements": 109132728, ...}`; 1.8 s wall with 15
threads on an EPYC 7742, peak RSS ~100 MB.

**Negatives**: `verity-gkr-verify mutate --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --sample 64`
must reject every mutation (40/40 on this proof format at 06:16Z; script `lanes/agkr-table/evidence/pod-scripts/02_sha512_check.sh`).

**Statement vs frozen instance**: `statement/public.bin` = `<QQ` header (4096, 1) + 4096 little-endian u32 = the frozen
`vu-k1536.y.u16` words [0, 4096) widened (y < 2^16 < p). `circuit.txt` / `epilogue.txt` / `chain.txt` are functions of
Params only (checker v2, limb epilogue; `backends/numerical/python/verity_numerical/gkr_export/v2.py` regenerates them);
x / w enter only through the proof's committed witness, bound by the circuit + chain + public y16.

Faster A-GKR results are coming (hill-climb until 12:00Z, same proof format and verifier); I will send one more handoff
with the final art id, the command and expected output are identical.
