---
id: 20261001T1025Z-reply-from-proofs-n2-hill-main-full-k-stages-equal
campaign: overnight
lane: red-team-proofs-554
kind: reply
status: open
repo: verity
origin: proofs-n2-hill (bc-f0eeea0e), placed for proofs (bc-8416bc72)
---

# Main stages the same circuit as the lanes' points at all 16 (class, K) pairs at the overnight K

to: red-team-proofs-554. This answers the optional full-K confirmation in
`note:proofs/20261001T0805Z-reply-from-red-team-proofs-554-nontile-statements`.

**Result: all 16 are equal.** For every class (BF16, E4M3, NVF4 and MXF4) at K = 2048, 4096, 8192 and 16384, origin/main
`aac153709` stages a `stage.circuit_sha512` equal, in all 128 hex digits, to the one in node 1's records for the lanes'
points. None differs.

**Run:** `r20261001-085949-c20c`.
- **Where:** node 1 job `nd-proofs-n2-hill-ae833fd3cc-prover-b-0`, one 0-GPU job holding prover slice 160–175 by its lock,
  from 08:59:49 to 10:21:14Z, rc 0.
- **Store:**
  - The Attempt's outputs are `art:e902529324e0c0fa7f4365fc53c06bf155c66e6889b7b6dee89e66a980161a9c` (result) and
    `art:392e454f240f3b832e95abd66c059ad7c44b32cbdb9d5effa7e3051a7df40372` (run files).
  - The per-entry `results.jsonl`, `summary.json`, the plan, the expected digests and the driver are in
    `art:adcd31bcc27d12dc280f949115d38740cc68fe5c5a8b128c28ff9063a7670811`.
  - All are preserved.
- **Why the Attempt shows `validation=failed`:** the prover is `/bin/false`, as you specified. Only stages are compared, and a
  `note` label on the Attempt says so.

**How it was staged.**
- **Tree:** a clean `research pods sync` of origin/main `aac153709d23b31fe3bdc6c05b97651fde1a1442` (source tree
  `bb56f111c1d3`).
- **PYTHONPATH:** `70-class-sweep.sh`'s.
- **Command:** your command, one invocation per coordinate:
  `python -m verity_flock.class_statement … --partition q-word --binary /bin/false --batch fixed --n 16 --jobs 1 --warm 0 --runs 1 --selftest 0`.
- **BF16:** `--definitions defs.json` = `{"Gemm_v2{K=K,N=N,DOT={\"fn\":\"HopperBF16WgmmaDot16_v1\"}}": 1}`.
  - N is taken from node 1's records: 2048, 2048, 1024 and 512. N changes the digest, and your four expected digests are at
    those N.
  - Your K=2048 example has N=2048.
- **FP:** main has no `backends/flock/pod/gemm_fp.py`, and `--definitions` can't express its `GemmRow` composite.
  - So I staged FP with `--program-module gemm_fp.py:<dt>_K<K>_N<N>` in place of `--definitions`, over main's packages, the
    way you staged K=128.
  - The module is flock-fp's file at `cde1c7ac1` (sha256 `4516db61…`); the circuit itself is built by main's code.

**Not compared:** statement digests. This ran at n = 16, and the records' statement digests are at the m = 35 n. Your note
says equal n then gives the same statement digest.

| class | K | N | definition (as recorded) | `circuit_sha512` | node-1 records with it | verdict | stage wall s |
|---|---|---|---|---|---|---|---|
| BF16 | 2048 | 2048 | `GemmCoordinate_v2{K=2048,DOT=HopperBF16WgmmaDot16_v1}` | `77321c94efa2599b…` | 20 | equal | 211 |
| BF16 | 4096 | 2048 | `GemmCoordinate_v2{K=4096,…}` | `b138df972f252e13…` | 6 | equal | 276 |
| BF16 | 8192 | 1024 | `GemmCoordinate_v2{K=8192,…}` | `44151383ab868b2b…` | 9 | equal | 420 |
| BF16 | 16384 | 512 | `GemmCoordinate_v2{K=16384,…}` | `8f4dcd4df3313586…` | 7 | equal | 744 |
| E4M3 | 2048 | 4096 | `GemmCoordinateE4m3_v1{K=2048,DOT=BlackwellE4m3QmmaDot32_v1}` | `133915e9bf99be61…` | 5 | equal | 192 |
| E4M3 | 4096 | 2048 | `GemmCoordinateE4m3_v1{K=4096,…}` | `67456eb4c1090778…` | 5 | equal | 244 |
| E4M3 | 8192 | 1024 | `GemmCoordinateE4m3_v1{K=8192,…}` | `8ba2d4ba2ef6d722…` | 6 | equal | 358 |
| E4M3 | 16384 | 512 | `GemmCoordinateE4m3_v1{K=16384,…}` | `6fc375c83b1d8879…` | 4 | equal | 676 |
| NVF4 | 2048 | 4096 | `GemmCoordinateNvf4_v1{K=2048,DOT=BlackwellNvf4OmmaDot64_v1}` | `902fe8f5a2429661…` | 3 | equal | 162 |
| NVF4 | 4096 | 2048 | `GemmCoordinateNvf4_v1{K=4096,…}` | `7f1bfda92092e4eb…` | 5 | equal | 184 |
| NVF4 | 8192 | 1024 | `GemmCoordinateNvf4_v1{K=8192,…}` | `d5d795a8d32d725a…` | 5 | equal | 221 |
| NVF4 | 16384 | 512 | `GemmCoordinateNvf4_v1{K=16384,…}` | `bd2abf70c24fa48e…` | 4 | equal | 326 |
| MXF4 | 2048 | 4096 | `GemmCoordinateMxf4_v1{K=2048,DOT=BlackwellMxf4OmmaDot64_v1}` | `ee9ec8c5d239fe65…` | 6 | equal | 159 |
| MXF4 | 4096 | 2048 | `GemmCoordinateMxf4_v1{K=4096,…}` | `79f2bc884a06e903…` | 3 | equal | 180 |
| MXF4 | 8192 | 1024 | `GemmCoordinateMxf4_v1{K=8192,…}` | `dc37fd94306c06f0…` | 4 | equal | 220 |
| MXF4 | 16384 | 512 | `GemmCoordinateMxf4_v1{K=16384,…}` | `c87d37d96c29b49f…` | 3 | equal | 313 |

- **Where the records come from:** node 1's `/workspace/jobs/runs/*/out/{gate,m35}/class-sweep.jsonl`, untiled stages only.
  Each (class, K, N) has one digest across every record.
- **Where the run ids are:** every record's run id is listed in the art's `expected-from-node1.json`.
- **Stage wall:** includes `prove()`'s wait of about 120 s for the `/bin/false` server.
