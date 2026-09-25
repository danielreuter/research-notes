---
lane: coordinator
kind: handoff
from: x4-sha256-fill
created: 2026-09-25T19:37Z
---

# verification-ready: 4090 fp8-ada-x4+sha256 plateau art:ac1f532c (3402 VU/s, 3.16e7x) and A100 bf16-ampere-x4+sha256 4096 art:675a03a3 (1830 VU/s, 5.55e7x)

A non-producer (not x4-sha256-fill, not b-ligero-sha256) should reverify and label; the two instance-equiv docs need a
fresh-pod `python -m verity_numerical.bench.instance_equiv --check <raw file> --vus <n>` by someone else (raw files in each
run's `outputs/`; artifact meta adds `lane` and `provenance`).

| cell | result | proofs | equiv | run (tree) |
|---|---|---|---|---|
| RTX 4090 · E4M3 · SHA-256, fp8-ada-x4+sha256, plateau 16384 | art:ac1f532c | art:b205e19d | art:dc455fc8 (equal, producer --check reproduces) | r20260925-181916-75dd (cd963fd4) |
| A100 SXM4 80GB · BF16 · SHA-256, bf16-ampere-x4+sha256, 4096 (set cap) | art:675a03a3 | art:aaa3c3a6 | art:40b23d0b (equal; --check refuses: ref shared by 6 relations; instances = the frozen ref itself) | r20260925-192613-398d (8edb8000) |

- 4090: l2048 p3 (screen at 4096: l2048p2 2512, **l2048p3 3142**, l1024p4 2266 VU/s; l4096p2 CUDA OOM). Sweep 1024 2655, 2048 2985,
  4096 3262, 8192 3382, **16384 3402**, 32768 killed (rc -9, host memory). e2e 4.816 s = t.total 4.662 + commit 0.154; 97
  sub-batches of 170, 2^-128.31, 16.6 GB device. Pod Rust (cd963fd4 build) 97/97 ACCEPT, system pinned. Uncontended, 5 reps.
- A100: l4096 p4, 4096 VUs, e2e 2.239 s = 2.194 + 0.045; 25 x 170, 2^-128.05, 36.4 GB; pod Rust (8edb8000) 25/25 ACCEPT pinned.
- Interactive fields (1836Z standard): rounds.protocol 3, sequential depth 3; bytes prover->verifier = transcript 7.44 GB (4090)
  / 1.83 GB (A100); verifier->prover = coins only (not separately recorded). RTT **not measured**: file-dumped runs, no live
  verifier. Modelled at the reference network (1 ms, 100 Gb/s): network 0.595 s + 3 ms (4090), 0.146 s + 3 ms (A100) against
  prover compute 4.82 s / 2.24 s; verifier compute (sum over sub-batches) 20.2 s / 5.25 s.
- Custody: both result artifacts verify PRESERVED; the proofs trees' readback verify timed out from the VM (large); the runner
  pushed them under custody-r2 — please confirm with `research data preserved <run>`.
