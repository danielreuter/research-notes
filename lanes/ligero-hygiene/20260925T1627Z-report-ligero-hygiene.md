---
lane: ligero-hygiene
kind: report
created: 2026-09-25T16:27Z
status: open
---

CHECKPOINT cd71b615 (16:45Z) [open] pod vy-ligero-hygiene = hb8gfpinlwovt7 (cpu3c 4 vCPU; 8 vCPU stock exhausted). bootstrapping for item3 (conformance committed-operand negatives, --exclusive)
CHECKPOINT cd71b615 (16:39Z) [open] item2 fixed @7c655f86: BV-D1 (config_for sized t at k=l, calculator k=l+1); prover now sizes at k=l+1 (non-ZK small l only). item4 @cd71b615: float seed, sharing label, missing .hproof, 3 tests green. next: item3 pod
CHECKPOINT 239c0e28 (16:27Z) [open] item1 green on VM @239c0e28: pytest hashauth+reverify+steps_pin 63 passed 0 skip (LIGERO_VERIFY set); cargo test --release 69 passed 0 failed. next: item2 live_test [None] 2^-99.86
