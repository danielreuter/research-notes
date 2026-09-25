---
lane: vllm-rf-gc
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T22:55Z
---
# gc3 follow-up: G4c after the b5vc merge (one token), plus the other stale-ROOT uses

Your gc2 merge request went out at 22:55Z. b5vc (in main) builds G4c's list with
`glob(os.path.join(ROOT, "verity_vllm/program/frontend/rules/vllm_bindings/*.py"))` and `relpath(p, ROOT)`, using the
stale `ROOT`. After your merge that glob is empty, so G4c silently skips the 13 bindings files.
- Once gc2 is in main, branch `lane/vllm-rf-gc3` from `origin/main`. Make that glob and relpath use `INTEGRATION`, and fix
  the G4b/G1-G4b/G5 stale-ROOT uses you listed (`EVIDENCE`, `DERIVE_STEP`, the G5 PYTHONPATH).
- If a corrected guard fails, report it as a real finding; don't weaken it.
- Gate: run `test_harden_guards.py` and the lints at head and base on a small cpu pod, in a git clone with
  `sampled_proofs` on PYTHONPATH (`gate_b2.sh`). The full gate (b) isn't needed for a one-file test change unless
  something else moves.
- Budget $2. Merge-ready handoff as usual.
