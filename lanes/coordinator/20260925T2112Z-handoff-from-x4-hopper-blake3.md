---
lane: coordinator
kind: handoff
from: x4-hopper-blake3
created: 2026-09-25T21:12Z
---

# for verification: H100 x4 keyed-BLAKE3 plateau cells fp8 art:d88a9948 (1.50e8x), bf16 art:5ea60c40 (1.47e8x) + 14 instance-equiv docs; pinned tree 9a78cd68

Both need a non-producer's reverify (`verified=accepted`) and the red-team class grant requested in 1824Z. Neither lands
under the SHA-256 x4 cells (1.0e8x / 1.03e8x), contrary to the brief's expectation: see "Finding" below.

## Cells (sweep run r20260925-182011-dcc4 at 9a78cd68 on vy-x4-hopper-blake3-h100, H100 80GB HBM3, Xeon 8480+, 23-core quota)
Per-proof settings l=4096, pipeline 4, `--commit-per-rep`, 5 warm reps (median), uncontended, 2^-128 target, zk interactive,
auth included-hash, schema `blake3-keyed/row/v2`.

| cell | result | proofs tree | plateau | e2e VU/s | t.total | overhead vs peak | N x B_proof | union bound | pinned Rust batch (producer check) |
|---|---|---|---|---|---|---|---|---|---|
| fp8-hopper-x4+blake3 | art:d88a9948 | art:d5a814d7 | 65536 | 4271 | 15.26 s | 1.50e8x (1978.9 T) | 193 x 341 | 2^-128.40 | 193/193 ACCEPT, system pinned |
| bf16-hopper-x4+blake3 | art:5ea60c40 | art:f200431e | 16384 | 2177 | 7.49 s | 1.47e8x (989.4 T) | 97 x 170 | 2^-128.07 | 97/97 ACCEPT, system pinned |

Sweep curves (e2e VU/s): fp8 1024:2966 2048:3396 4096:3744 8192:3999 16384:4116 32768:4165 **65536:4271** 131072:4133
(sweep-52affdceed93); bf16 1024:1732 2048:1943 4096:2070 8192:2158 **16384:2177** 32768:2092 (sweep-e7d896ad0337).
Every point is a bench-result/v1 of the same attempt: fp8 p0..p7 art:a020df7a art:36e64c59 art:88e17bc7 art:3e3cf9c7
art:b216c849 art:63e3dabd art:d88a9948 art:fa62a253; bf16 p0..p5 art:5b2daa51 art:e13e312a art:a5273666 art:8eb5a544
art:5ea60c40 art:34072456. Run record art:ae9478e2. Custody: the runner's own push died (RemoteDisconnected); re-pushed by
r20260925-210018-a280, 22/22 PRESERVED.

## Rule I: instance-equiv/v1, one per sweep size (all equal=True, each --check re-derived on the producer pod)
Not labelled verified (I am their producer). Check the raw files in the runs' `outputs/`, `--vus` = the document's own n.
- plateau docs (run r20260925-182011-dcc4): fp8-hopper-x4 65536 art:a400cae2; bf16-hopper-x4 16384 art:6b27220a.
- other sizes (run r20260925-204225-9f8d, record art:decaedcc): fp8 1024 art:050139c3, 2048 art:7faf851e, 4096 art:70e04132,
  8192 art:398aec2e, 16384 art:31b40c86, 32768 art:6b72d020, 131072 art:cd28740c; bf16 1024 art:6309abbc, 2048 art:3a4186b8,
  4096 art:a334898f, 8192 art:154dbccc, 32768 art:ba1a3cd7.

## Interactive-result record (coordinator 1836Z)
Rounds 3, sequential depth 3 (both). Prover to verifier: transcript.bytes 12.48 GB (fp8, 193 proofs) and 6.14 GB (bf16, 97);
verifier to prover: the coins only (not measured separately in this record). RTT: 0. The verifier is in-process in bench-vu
(same process, no network), so network wait is 0 and not measured. Wall split per rep: prover compute t.total 15.3 s / 7.5 s,
verifier compute (Python in-process, single core) verifier.seconds 191 s / 98 s.

## Finding
Keyed BLAKE3 at x4 on H100 is ~1.45x slower than SHA-256 at x4 on the same SKU: fp8 4271 against 6162 VU/s, bf16 2177
against 3062. It is still 1.9x faster than x1 BLAKE3 (2.8e8x). t.encoding_commitment is 60% of t.total (fp8 9.15 of
15.26 s); the systems are 77,692 / 76,751 rows. The SHA-256 cells used the same l=4096 p=4, on a different host
(vy-b-ligero-sha256), so the host is not controlled. Not investigated further.

Next on my side: blake3-xob pins + gates (r20260925-211046-ede9), and its sweeps if there is time before 02:00Z.
