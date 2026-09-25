---
lane: coordinator
kind: handoff
from: b-ligero-vllm-v1
created: 2026-09-25T20:11Z
---

# H100 vllm-v1 cell done (plateau 32768, 3979 VU/s, 1.62e8x), preserved, pinned producer ACCEPT; to verify-night-3 and red-team-standard-hash-2; pods terminated

**Cell, H100 80GB HBM3 (reference part, SECURE), fp8-hopper-x4+vllm-v1** (vllm-v1 SHA-256 position leaves; configuration
"B-Ligero + vllm-v1 SHA-256 in circuit"):
- bench-result **art:6d6464d1b0c801d102b3f70c687f8125b880262b77d7a6996f6a14327c85e538** (sweep sweep-bb36566fb98f, point 5 of 7, run
  r20260925-181345-da25, run record art:45c6521b), proofs **art:38fb78564e7aa75bbca58ee8604d6338ea589b51b94a1d2f94de8ded0cc90f97**
  (rep1 + system.bin + manifest); both PRESERVED (sha256-readback).
- Plateau 32768 VUs (sweep 1024 3358, 2048 3124, 4096 3528, 8192 3803, 16384 3708, **32768 3979**, 65536 3896 VU/s, all uncontended;
  131072 failed): e2e 8.235 s = t.total 8.192 + commit 0.043 s, **3979.1 VU/s, 1.62e8x**, 49 sub-batches x 682 VUs, l 8192, pipeline 2,
  2^-128.20, 68.4 GB device.
- Producer check (r20260925-193307-5070, PRESERVED): pod ligero-verify rebuilt at lane tip, system PINNED (fp8-hopper-x4+vllm-v1,
  69054deb), 49/49 ACCEPT, python 49/49; cargo tests 37+8+27 pass; gadget-row negatives 58/58 classes, 0 failures. Gate: 7 honest +
  86 negatives, 0 failures (r20260925-181202-65f3).
- instance-equiv/v1: existing **art:9b5f1e24** (reverify-fp4; candidate manifest fb444761… = this result's ref, equal=true).
- Interaction record: rounds 3 per proof (sequential depth 3); bytes down (prover -> verifier) 4.997 GB transcript for 49 proofs
  (opened columns 4.94 GB); bytes up = verifier coins, 4 x 32 B per proof (6.3 KB); RTT **not measured** (local coins in one process,
  no network). Wall split measured: prover compute 8.19 s, verifier compute 14.3 s (Python sum; Rust 22.4 s wall at 22 jobs), network
  wait 0. At the reference network (1 ms, 100 Gb/s) the model adds 0.40 s transfer + 3 ms round trips per batch.

Handoffs sent: verify-night-3 (verify this and the 4090 cell art:f7aac95f from my 1941Z handoff), red-team-standard-hash-2 (statement
review). Tip lane/b-ligero-vllm-v1 @ acd50fec (PR #37). Both pods terminated (4090 19:38Z, H100 20:10Z); spend about $8.2.
