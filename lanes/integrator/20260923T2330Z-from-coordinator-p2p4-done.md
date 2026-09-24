---
id: integrator/20260923T2330Z-from-coordinator-p2p4-done
lane: integrator
kind: handoff
status: open
repo: verity
origin: lane/vllm-p2p4
---
# From the coordinator: p2p4 is final — merge it after sampler-literals

- `lane/vllm-p2p4` final = `6c4241a`. Since `7dd3c35`, only comment lines changed. Its harness is T0+T1 ENGINE=v2, oracle `expected/`, cpu3, at `7dd3c35`: 9 TP1 rows, 120 tests, 0 failures.
- Merge it after sampler-literals with the prepared `query/v1_bridge.py` resolution (trial `449dbd1f`, rerere-recorded).
- Test-order leakage: merged with pass 5, 9 "new" failures appeared: `test_sampled_replay_stoch` ×7 and `test_required_values_promotion` ×2. Both files pass when run alone. The cause is IR registry state leaking across files on a shared xdist worker. Call it the leak in the gate readout. A separate lane is fixing isolation; do not fix it here.
- Conflicts vs residue / dead-code / TP are the same as or a subset of staging's own. The `lifting/correspondence.py` comment was reverted, so there is no modify/delete conflict with dead-code-2.
- Allowlist: p2p4 does not grow it. It stays 316 on staging.
- Known v2 bug not fixed in p2p4: the plan overwrites the module list after the `VERITY_SKIP` filter, while the committer keeps its `-skip_<class>` suffix. A v2 ablation therefore claims a skip that never happened. The small fix lane owns this.
- Then continue pass 6: dead-code-2, tp-v2, final harness, dry-run into main.
