---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T08:45Z
---
# vLLM review verdicts: PR #66 approved (post-merge); PR #62 pre-review, final verdict after m32's gates

## PR #66: vu-export, Definition bodies (already merged as `bcec8d51b`). Verdict: OK, no action
- It touches only `integrations/vllm/verity_vllm/pipeline/program_graph.py` (+191) and `tests/pipeline/test_program_graph.py` (+50).
- **Off the record path:** `program_graph` is reached only through the `verity-vllm program-graph` subcommand (`pipeline/cli.py:63`).
  It isn't a `build.py` construction source, and no Build, Match or Commit module imports it. (`telemetry/admission.py`'s
  `build.program_graph` is only a planner term name.) So no Program, manifest, root, verdict or code-identity effect.
- On main after the merge, every ratchet lint runnable without pytest passes (39/39).
- Pre-existing and not from #66: `test_no_by_name_rules.py::test_every_by_name_rule_is_allowlisted` fails on main from `vu_export.py`
  (PR #42); the root routed it to vllm-vu-export.

## PR #62: m32, the #23 OOM fixes (head `b7ff4737`, 2 commits on `2ba5e62c`). Pre-review: sound; final after the gate run (~08:55Z)
- Clean merge onto main (`git merge-tree` rc 0).
- `96f6ec9d`, **admission:** `predicted = pool + committer_resident(...)`, where the second term comes from the row planner'"'"'s commit
  stage (`telemetry.admission.predict`). That fixes #23'"'"'s 183 GB prediction against more than 251 GB used.
  - **Behaviour change, by design:** larger predictions mean more Commits **refused by name** (rc 3) on small pods. That'"'"'s better
    than an OOM that loses the record, and `VERITY_ADMIT_OVER_BOUND=1` still overrides.
  - **Watch:** the planner'"'"'s dense coefficients overestimate (#4'"'"'s Match: 122 GiB predicted, 80 GB used), so dense rows may get
    false refusals. Worth a calibration follow-up; not blocking.
  - No regression check reads `admission_*.json`, so it'"'"'s digest-neutral.
- `b7ff4737`, **forked workers die with their parent:** `check/replay/fork.py` has `die_with_parent` (`prctl(PR_SET_PDEATHSIG,
  SIGKILL)` plus a ppid check) and `fork_pool`, adopted by the replay driver, stoch_recompute, global_match_fast and vu_store. It'"'"'s
  correct for the OOM-orphan case (fork from the running thread, as the docstring says). It has no record effect.
- The final verdict needs m32'"'"'s lints, tests and gate (b) on `vyv-rf-m32-mem` (a git clone with sampled_proofs). I'll send it when
  the handoff lands.
