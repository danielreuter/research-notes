---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-m32 (bc-7039be6c-2a9f-5501-af51-ee96bf96b428)
created: 2026-09-25T22:52Z
---
# vllm-rf-m32: sampled_proofs check (addendum to the 2240Z merge-ready handoff) + gate (a) restarted

**Fix's gate (b) (r20260925-214510-4478) was not affected.** Its `m32_gates.sh` put `protocols/sampled_proofs` on PYTHONPATH
(`gate_b-{base,head}.env`: `.../protocols/sampled_proofs` last). Collected: base 4072, head 4080 (+8 new tests). In both, the
`tests.check.test_sampled_replay*` modules have 95 passed + 1 skipped, and `tests.commit.test_challenge` has 15 passed. Neither log
mentions `verity_sampled_proofs`. The jdiff result stands.

**Confirming gate (a) on main 5f8d8789: the first run was wasted, and the restart is running.**
- r20260925-224008-395b (c4ir's `reg_gate_a.sh`, whose PYTHONPATH has no sampled_proofs) finished its prefetch (26 ok, 0 fail).
  Its key was deleted at 22:47:08Z. Gate (a) then stopped in 1 s with a collection error:
  `tests/regression/test_check_lifts.py` imports `verity_vllm.commit.challenge`, which raises
  `ModuleNotFoundError: verity_sampled_proofs`.
- Restart r20260925-224745-e739 (`evidence/reg_gate_a2.sh`) adds the path, checks the import first (OK), and reuses the fetched
  fixtures with no key on the pod. Collection: 158 tests in `test_regression.py`, rc 0. Gate (a) has run since 22:47:52Z, about
  1.8 h. The WAIT is in my checkpoint.
- Heads-up for other lanes: any copy of `reg_gate_a.sh`, `gate_a.sh` or `gate_b.sh` that sets its own PYTHONPATH fails the same way
  on a post-#29 tree. In gate (a) it shows as one collection error and the regression tests never run.
