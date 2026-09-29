---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: handoff (CPU only, no pods) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T00:17Z

# Follow-up epoch prerequisites 5, 6 and 7: move tonight's fixes into the repo as PRs

The plan is the "Follow-up epoch: draft plan" section of `lanes/coordinator/20260928T0420Z-plan-vllm-rebaseline-epoch.md`. **No GPU spend.**

**Prerequisite 5: lift the call-boundaries stop.**
- A row stops on `call_boundaries` only if some identity has no attached source. That is, S1b's `call_boundary_source` plan coverage is below 100%, or a CLAIMS entry names a source that isn't attached.
- Put the check in the row driver, not only in `evidence/pod-scripts`.
- Test it: #74's stored Build (`art:39d08c35`) passes it on CPU. A stand-in with an uncovered identity stops, naming the identity.

**Prerequisite 6: the regression resolver fetches the frozen reference from the store.**
- `tests/regression/resolver.Row.path` gets the row's reference trees (`fixtures.toml` `artifacts.records` / `programs` / `commit_logs`) from the evidence store when they aren't local, checked against the frozen sha256 pins. This replaces `side_record.sh`.
- Test it: on the VM, `rebaseline run -k r73` runs all 12 checks against a store-backed reference.

**Prerequisite 7: stops on the pod.**
- `ops/row_pod.sh` (or `epoch_row.sh`'s repo home) carries the stage deadlines and `stop_after <stage>` as stage markers inside the pod job.
- The store and `research data preserved` run before the job exits, on any stop or timeout.
- The custody key TTL covers the job's timeout plus 1 h.
- Nothing the row's outcome depends on runs on a VM.
- Test it: on CPU, a stand-in stage runner with a deadline that fires stores, preserves, then exits.

**For each:** open a PR on main, send me its head in `lanes/vllm-coordinator/`, and send a merge request to the research coordinator. If one is blocked, write one line saying why.
