---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T17:49Z
---

# verify-flock-pure: the uncontended c2 re-run art:b61eafa9 (T=129..256) is verified=accepted as a file re-verification, so #101's attention now has all 287 key counts labelled (c1 4fb2de9c, c2 b61eafa9, c3 4dd2069b); pod terminated 17:48Z; about $0.6

- **Run:** replay run r20260926-165159-6043 (rc 0, preserved), from lane/verify-flock-class @ 4d8217ef.
  - The cell's verifier ran 8ef6d347, which differs from my 31d275ad base only in `bench.py` and `ir_bench.py` (harness); the
    verifier is identical.
- **Class pin:** fc9dceb5 equals the sha256 of the verifier's `class.json`, and my manifest is byte-identical to it.
- **Staging:** each head's T comes from the staged set art:82c591d1, and every sub-batch is one T with its own netlist. All 128
  staged files match the verifier pod's, and they're the same files as for the earlier c2 run.
- **Sessions:** 768/768 sessions replay with `--class`, the prover's proofs are the recorded ones (1,536/1,536), and all 15
  negatives behaved as expected.
- **Not replayed:** art:ef10f5fb (its twin), as instructed. The earlier c2 copy art:87a6bcdd keeps its own accepted label.
