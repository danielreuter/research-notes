---
lane: vllm-rf-m32
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T01:10Z
---
# Your confirming gate (a) didn't run: collection error. Rerun with sampled_proofs on PYTHONPATH

`r20260925-224008-395b` on vyv-rf-m32-reg: prefetch 26 ok, key deleted 22:47:08Z, then **`gate_a rc=2` one second later**.
The jdiff shows `::tests.regression.test_check_lifts: absent -> error [collection failure]`, and no regression test ran.
The script is c4ir's `reg_gate_a.sh`, which exports its own PYTHONPATH without `$T/protocols/sampled_proofs`. The tree
contains PR #29, so that's the likely cause. Confirm it in the log.
- Rerun on the same pod (the fixtures are in its store; no new key is needed). Use a git clone of the same main sha
  (or current main, and name it). Append `$T/protocols/sampled_proofs` to PYTHONPATH, and print
  `python -c "import verity_sampled_proofs"` before pytest.
- Split it into two concurrent halves (`-k replay_partition` and `-k "not replay_partition"`), each with a timeout over
  4 h, so it ends before the 05:00Z vyv- deadline. The pod is 32 vCPU / 256 GB; two halves peaked at about 131 GB for
  b5gm.
- Then WAIT, end your turn, and on waking send the "CONFIRM gate (a) on main <sha>" handoff.
