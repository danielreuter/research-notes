---
id: proofs/20261009T1050Z-finding-rec-stage-real-class
campaign: recursive-private-circuits
lane: proofs
kind: finding
status: open
repo: danielreuter/verity
origin: cursor/rec-private-stage-95d4 @ 4591bb91f (rec-stage bc-b5fd2fd3); runs r20261009-070330-3dc4, r20261009-092332-af31, r20261009-101844-a23e
---

# The real private-circuit class, staged: UniversalUnit_v1{8090,64,32} with F32MulFtz_v3

The class stages. `UniversalUnit_v1{8090, 64, 32}`, holding the real private circuit (F32MulFtz_v3 padded to G = 8090),
stages on node 1 in 52 min 46 s with a 197.8 GiB peak through a new fast path. Today's path can't do it tonight: its
measured scaling extrapolates to about 6–8 h and about 640 GiB. The staged statement's inner session also proves on the
CPU (M0): `prove` takes 7 min 12 s at 116 GiB.

## Today's path: scaling and where the time goes

Measured on node 1 with n = 8, one class per process (run `r20261009-070330-3dc4`,
`art:fa61dd112462cfc9179c11ca6fe0ee25d44945b82e9a292b893531b066fc4a1f`). Peak is the largest per-phase peak.

| G (N_IN=64, N_OUT=32) | ANDs | total s | peak GiB | trace | units | lanes | stage (lowering, compose) |
|---|---|---|---|---|---|---|---|
| 128 | 39,810 | 47.9 | 0.70 | 3.0 | 12.4 | 2.2 | 30.1 (2.4, 26.4) |
| 256 | 110,754 | 39.5 | 1.08 | 8.4 | 9.5 | 1.8 | 19.4 (3.2, 14.3) |
| 512 | 351,170 | 112.4 | 3.06 | 28.1 | 37.3 | 8.6 | 37.4 (12.1, 19.9) |
| 1024 | 1,225,698 | 353.2 | 10.9 | 92.7 | 111.3 | 20.0 | 125.7 (56.2, 44.8) |
| 2048 | 4,548,610 | 1,527.7 | 41.6 | 457.2 | 545.8 | 118.2 | 392.0 (198.7, 121.9) |
| 8090 (fit) | 66,841,560 | ~22,700 (6.3 h; ~8 h on the last step's slope) | ~640 | | | | |

From 512 to 2048, time and memory both grow as ANDs^1.02. The time goes to Python objects per gate or per column: the
trace's `forms` objects, `PartitionUnits` in units, and `class_lowering` and the layout in lanes and lowering. At small
G, compose is mostly a fixed ~25 s for the slot circuits.

## The fast path and the equality check

`verity_flock.universal_stage` writes the same files from arrays. It is switched on by `rec_inner.py universal --fast`
(or `REC_FAST_STAGE=1`), and `--netlist` (or `REC_NETLIST`) supplies the circuit's description. It was re-proved equal
after rec-v0's branch moved to `program_unit` (one program row, three regions).

- **Classes:** 8,5,3 (n=4), 16,16,8 (n=1) and 24,9,5 (n=2), each holding a random private circuit of 3/4 the class's
  gates, padded to the class so that padding is exercised.
- **Files:** all eight files are byte-identical by SHA-256 (`stage/` and `other/`: `circuit.txt`, `inst-n.bin`,
  `pub-n.bin`, `partition.json`), and the records are equal. 64,64,32 was equal on the earlier four-port grouping.
- **Tests:** `verity/ml/flock/tests/test_universal_stage.py::test_fast_staging_writes_class_statement_stage_files`
  (slow; the three classes) and `::test_trace_is_universal_traced`; with `test_rec_private.py`, 8 passed.

## The real class staged

Run `r20261009-092332-af31` (`art:b32f104d2b7fcf8393d42549f4a5941c621e5f247cfd0ecb6072d9718415763d`): 52:46 wall,
exit 0.

- **Time:** trace 17 s; units 157 s; lowering 603 s at 98.7 GiB; the Program's descriptor 2,136 s at 73.0 GiB (in a
  forked child, alongside units and lowering, and the critical path: the parent waits ~23 min for it); compose 208 s at
  168 GiB; the two writes 219 s and 269 s at 197.8 GiB.
- **Files:** `/workspace/jobs/rec-stage/data/rec-stage/f32mulftz-8090-64-32-n32-prog/{stage,other}` on node 1, kept
  until 2026-10-23. `circuit.txt` 31,780,823,324 B (circuit_sha512 `0cff410a38e8dab8…`), `inst-32.bin` 64,449 B,
  `pub-32.bin` 15,362 B.
- **Sizes:** 66,841,560 ANDs (the closed form); 67,104,257 unit rows (under 2^26); 3,882,655,496 nonzeros (~58 per
  AND); program row 226,936 bits (2G + 2GK + N_OUT·K); committed bits 32 × 2^27 = 2^32 (k_log 27, m 32, 32 blocks),
  exactly the cap; ports x 64 words, program 14,208 words. n = 32: n = 64 would be 2^33 bits, past the cap, and the
  fast path refuses it rather than capping.
- **Outputs:** in the run, the laid-out rows' outputs equal `universal.interpret` on all 32 inputs for both the
  registered and the other private circuit, and the padded circuit's outputs equal the unpadded F32MulFtz_v3's. Before
  the run, `interpret` of the padded circuit matched F32MulFtz_v3's bit-sliced evaluator on the same inputs.
- **`other`:** the same circuit and outputs; it differs from `stage` only in the program row's root (`frame_v3.roots.p1`).
- An earlier staging on the four-port grouping (`r20261009-074833-a4cc`, 1:18:43, 215 GiB) is superseded.

## Inner proof, measured

Run `r20261009-101844-a23e` (`art:a0e050fd62a8e24a7e600de47855225e14863e457c363a16a0e842eaeb50d1e5`), program-row
statement, 3 regions: `statement` 6:38 at 93.6 GiB; `prove` 7:12 at 116 GiB (about 6 min is M0 building the statement
single-threaded; the session is 40.2 s: witness 21.0 s, prove 19.3 s for two reps on 32 threads); `replay` 6:41,
refused as a shared-row public file (the form refusal rec-v0's statements get). Proof: 731,946 B per rep. The
four-port statement gave similar numbers (`art:c869cee1a718fec43a93a6c28028c91c29c002d8360155c127cc6105e651017b`).

## What `87-rec-private.sh` needs at this class

`REC_FAST_STAGE=1`; `REC_NETLIST=/workspace/research/runs/r20261009-092332-af31/inputs/F32MulFtz_v3.gates.json`
(absolute); `N=32`; `wired --cls ${WCLS:-$CLS}` with e.g. `WCLS=16,16,8` (four layers of the unit is ~267M ANDs, which
today's path can't stage); `--mem-gb 300` or more. Staging ~53 min; each `inner()` ~21 min.

## Open

- InnerFold.lean's fold over the 31.8 GB circuit: `r20261009-102129-f89e` (`90-rec-stage.sh MODE=fold`), 45 GB resident
  at 12 min, one-hour timeout.
- `rec_vstage stage` is unmeasured at this size.
- The Program's descriptor dominates staging (`trace.emit` and the codec, Python per gate); writing it from arrays
  would bring staging to ~25 min. Each write is ~4 min, and M0 rebuilds the statement single-threaded each call (~6.5 min).
- `tests/test_boundaries.py::test_ml_never_imports_core` fails on rec-v0's base too: `rec_inner.py` imports `verity.core`.
