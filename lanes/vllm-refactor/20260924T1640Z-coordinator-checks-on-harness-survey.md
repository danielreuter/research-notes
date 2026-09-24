---
id: vllm-refactor/coordinator-checks-3
lane: vllm-refactor
kind: note
created: 2026-09-24T16:40Z
---
# Coordinator spot-checks of survey-harness-ops-tests-data.md (at f0810a11)

The surveyor's reply was truncated to its last line. Its full report is intact.

## Confirmed
- **The hot worker's code key doesn't cover core.** `harness/hot_commit.py:51-52` sets `CODE_ROOTS = ("verity_vllm", "verity_vllm_sampler", "e2e", "record_v5", "scripts", "manifests")`. There is no Verity core root, and the survey reports that 4 of the 6 don't exist. After an edit to `packages/verity/src`, a live hot worker keeps its key and runs stale core code.
- **The Build's code-version stamp never changes.** `harness/derive_step.py:66-80` joins the 13 `_CONSTRUCTION_SOURCES` (`verity_vllm/...`) to `dirname(dirname(verity.ir.__file__))`, which is `packages/verity/src`. Every file is hashed as "missing", so `construction_version` is constant. The `research` store's cache key is not affected, because it hashes the whole closure (`harness/research_tools.py:44-49`). The stamp inside each Build artifact is meaningless, though.
- **The Build records bf16 for FP8 rows.** `derive_step.py:371` always writes `model_pin.dtype = vm.PIN["dtype"]`, which is bf16.

## Reported, not re-checked
- The Match verdict is a 113-line Python heredoc (`ops/row_pod.sh:686-800`). The script holds 12 heredocs and 24 `python -c` lines, and 12 test files regex-extract code from shell scripts.
- The ship tooling (`record_v5/ship.sh`, `pod_release.sh`, `pod_up.sh`) is not in the repo, but the harness reads its outputs: `EXPORT.json`, `RELEASE.json` and the RELEASING marker.
- The row id is parsed in 10 places, dtype is defined in 6, and `row_pod.sh` has 45 caller-settable knobs.
