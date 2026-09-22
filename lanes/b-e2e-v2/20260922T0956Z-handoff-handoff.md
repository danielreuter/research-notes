---
id: r20-proof/b-e2e-v2/20260922T0956Z-handoff-handoff
campaign: r20-proof
lane: b-e2e-v2
kind: handoff
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/direct/ligero/v2/HANDOFF.md
---

# b-e2e-v2 HANDOFF (lane `lane/b-e2e-v2`, pod `vy-g2`, 2026-09-22)

The question: B's real end-to-end cost at the checker-v2 shape, every b-v2 kernel wired into one prover whose
proof a verifier accepts, every negative rejected.  Status: **done for the torch prover with two of b-v2's
kernels wired (GPU Blake3 Merkle, blocked Montgomery inversions)**; the fused radix-4 `commit_stream` and the
structured-linear-test / F_c-triple CUDA kernels are *not* wired (domain and layout mismatch, below).

## Headline

4 096 VUs = 7 proofs x 682 VUs at l = 65 536: **1.26 s/proof, 1.85 ms/VU, 7.57 s per batch, union 2^-128.06**, verifier
0.40 s/proof, 9.2 MB/proof, peak 17.1 GiB (run r20260922-094956-5453).  b-v2's synthetic fused batch: 42.4 ms -> 180x.
Overhead 1.9e8 (ledger).  No `--breakthrough` (target 2e6).

## Where things are

* Code: `backends/direct/ligero/v2/` -- `system.py` (circuit -> `V2System`: columns, products, asserts, lookups,
  tables; `vu_units` builds a VU's 96 units from `gkr_export.v2` hints; `pack_limbs_gen/check` the limb pack +
  epilogue rows), `fc.py` (BabyBear^6), `protocol.py` (prover/verifier), `run.py` (`shape`, `gate`, `bench`),
  `pod_gate.sh`, `pod_bench.sh`, `tests/test_toy.py` (CPU, whole protocol on a toy circuit: accept + 4 rejects).
* Results: `results/` (gate json, bench json per l, the first host-hash bench log).  Runs: gate
  `r20260922-091001-68f7`; bench `r20260922-093550-e904` (GPU Merkle, torch inversions), `r20260922-094315-8be5`
  (+ blocked Montgomery inversions), later ones in the ledger.
* Docs: PROTOCOL.md section 16 (layout, tests, soundness, what was verified), `backends/direct/ligero/README.md`
  "v2" section, ledger `backends/numerical/reports/ledger/b-e2e-v2.jsonl`.

## Pod facts that cost time

* `/workspace/venv312` had **no cupy and no blake3** -> `merkle.gpu_available()` False -> host SHA-256 Merkle at
  ~4 s/proof.  Fixed with `/root/.local/bin/uv pip install --python /workspace/venv312/bin/python cupy-cuda12x blake3`
  (system `python3` is 3.11 and cannot import the `verity` package: `type` statements).
* Instances: `python -m verity_numerical.bench.instances build --out /workspace/bi/v1 --seeds fixtures/bench-instances/v1/seeds`
  (`pod_gate.sh` does it once).
* The `research fetch` of a running job races the sampler (`file changed as we read it`); read the pod log over ssh
  (`research.pods.runpod.ssh_target` + `remote.ssh_argv`).

## Bugs found on the way (all fixed, all would have been silent without the verifier)

1. Multiplicities: only the *first* query into each table was counted (`full` rebuilt per lookup) -> the LogUp sum
   identity failed on the real system but not on the toy (one query per table).  Toy now has two queries into SQ.
2. Lookup keys are the residue of the key Lin (coefficients stored mod p), taken as the signed representative.
3. `Config.n_vus` explicit (a proof may hold fewer VUs than fit).
4. The BabyBear battery `chain` class (+p on the accumulator) is the same field element under the v2 state chain:
   removed from the mutation list as vacuous (documented in PROTOCOL 16.4).

## Open (in priority order)

1. **Table side dominates** (1 950 of 3 139 rows at l = 16 384: SHIFT 3.5 M + TNORM 1 M entries as-is).  Port
   b-air-v2's chunked tables (SHIFT_HI/LO, SSHIFT_2/1/0, TNORM10, LEAD10: 282 k entries) -> tableau 2 ~700 rows,
   and 4 096 VUs fit one proof at l = 2^19 (n = 2^21) only if the tableau is ~900 rows x 2^21 x 4 B = 7.5 GB.
2. **Wire `commit_stream`** (radix-4 fused encode -> Blake3): it encodes on the *systematic* domain (cols < k are the
   message); this protocol evaluates on \(g\langle\omega_n\rangle\) (non-systematic, for HVZK).  Either give the
   streaming encoder a coset shift or move the protocol to the systematic domain with masking rows.
3. **Quadratic 0.22 s and the host witness 5.7 s per 170 VUs**: the F_c helper constraints are 6 x 6 coordinate
   products streamed in eager torch (b-v2's F_c-triple kernel is 4.5 ms for the batch); hint generation is
   single-threaded Python per VU (`gen_unit`), parallelised over VUs with a process pool -- the a-v2/b-ligero torch
   hint generator would remove it from the critical path.
4. The battery `wrap`/`z3` classes mapped onto v2 columns; the mutations re-deriving downstream wires (the current
   ones are caught by the linear test, not necessarily by the range/lookup teeth).
5. HVZK (b-ligero2 lane): blinding rows in tableau 1 and 2; the domain is already non-systematic.
6. z3 on the Python limb rows (or generate them from b-air-v2's Rust description) to drop the
   INCOMPLETE_CHECKER_DIAGNOSTIC caveat.
7. Public-table variant (b) of V2_SHAPE.md.
