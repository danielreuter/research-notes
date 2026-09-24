---
lane: fill-dc
kind: report
created: 2026-09-24T06:21Z
status: open
---

CHECKPOINT none (07:00Z) [open] 07:02Z chose: H100 fp8 v3x4p8 (~0.080) / +hash v1p8 (0.300); bf16 v3x4p8 (~0.14) / +hash v1p8 (0.545); A100 v3p8 (0.26) / +hash v1p8 (0.885). Live x3 + dumps running (A100 same-DC, H100 same-pod). 35 sweep results registered (evidence/registered.txt).
CHECKPOINT 1b3c7be6 (06:47Z) [open] 06:50Z sweeps r1 done: H100 fp8 v3x4p8 0.080/bf16 v3x4p8 0.129, +hash v1 0.310/0.547; A100 v3p8 0.235, +hash v1p8 1.01. v3/v3x4+hash unsupported. H100 live = same-pod (no hairpin DC); A100 verifier EUR-IS-1 RTT 0.6ms. art:0cb6c9fd
CHECKPOINT none (06:21Z) [open] 06:27Z started; read contract/brief/handoffs. Plan: H100 (bf16+fp8 hopper) + A100 pods SECURE with same-DC verifiers (H100 US-NE-1/EU-NL-1, A100 EUR-IS-1); sweep 2-3 cfg/col, then live x3 + dumps.
