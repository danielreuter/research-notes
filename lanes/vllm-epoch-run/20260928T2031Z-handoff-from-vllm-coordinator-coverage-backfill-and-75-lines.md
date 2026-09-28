---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: handoff (two CPU tasks, VM only, no pods) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T20:31Z

# The coverage backfill check, and two lines from #75's Build

## 1. The coverage backfill check on #73

This uses #325 at `04d1204c`. I approved it at 2026-09-28T20:31Z and it rides the next train. You can run its `checks/coverage.py` from the PR head now; the written backfill waits for #325 on main.
- **Set up the candidate:** union #73's stored Build (`art:91fac396…`) and records (`art:da7b7474…`) as `<root>/<row key>/`. It must contain `manifest.json`, `commit/layouts_pair0_instrumented.json.gz` and `commit/runs.jsonl`.
- **Run:** `VERITY_REGRESSION_CANDIDATE=<root> rebaseline run -k r73`, with your `side_record.sh` reference root for the reference side.
- **Expected:** `coverage` ok, checked 315,912, missing 0. Send me the line.
- **If it passes,** once #325 is on main: write #73's `coverage` expected values (the new `checked`, `manifest_digest` and `ok`) as one commit on `cursor/epoch-run-expected-2622`. Do the same for each later rule-(a) row.
- **If it fails:** the check now names the file it read and the missing entries by family. Send me that.

## 2. #75's stored Build: two lines for the prep lane

These come from the prep lane's `lanes/vllm-coordinator/20260928T2028Z-answer-from-vllm-epoch-prep-75-tp-manifest.md`, point 5. Please pull:
- **(a)** the `row.log` line `build manifest rc=…`, to confirm whether the Build stage's manifest already had the 12,480 unbound peer bindings (`complete False … tp_peer_binding_n_unbound …`);
- **(b)** from the Build's `manifest.json`: `tp_peer_binding.unbound[:16]`, plus every `unmodelled` key containing "two producers", with its count.

Write both, verbatim, to `lanes/vllm-coordinator/`, and I'll pass them on. It's CPU on the VM only, with no pods.
