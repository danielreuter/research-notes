---
lane: vllm-rf-b5patc
kind: report
created: 2026-09-25T16:26Z
status: final
---

CHECKPOINT 80b19e59 (16:47Z) [final] merge-ready lane/vllm-rf-b5patb @ 4537961b (no new commits); gate(a) 158=158 0 changes (cc3f, custody art:f1229b6c); gate(b) flip test_transient_storage_is_released shown unstable (5/5+5/5 isolated, 81eb); big terminated, cpu handed to b1c; new spend ~$0.8
CHECKPOINT 80b19e59 (16:45Z) [final] merge-ready lane/vllm-rf-b5patb @ 4537961b (no new commits); gate(a) 158=158 0 changes (cc3f, custody art:f1229b6c); gate(b) flip test_transient_storage_is_released shown unstable (5/5+5/5 isolated, 81eb); big terminated, cpu handed to b1c; new spend ~$0.8
CHECKPOINT 80b19e59 (16:43Z) [final] merge-ready lane/vllm-rf-b5patb @ 4537961b (no new commits); gate(a) 158=158 0 changes (cc3f, custody art:f1229b6c); gate(b) flip test_transient_storage_is_released shown unstable (5/5+5/5 isolated, 81eb); big terminated, cpu handed to b1c; new spend ~$0.8
CHECKPOINT 80b19e59 (16:42Z) [final] merge-ready lane/vllm-rf-b5patb @ 4537961b (no new commits); gate(a) 158=158 0 changes (cc3f, custody art:f1229b6c); gate(b) flip test_transient_storage_is_released shown unstable (5/5+5/5 isolated, 81eb); big terminated, cpu handed to b1c; new spend ~$0.8
CHECKPOINT 80b19e59 (16:40Z) [final] merge-ready lane/vllm-rf-b5patb @ 4537961b (no new commits); gate(a) 158=158 0 changes (cc3f, custody art:f1229b6c); gate(b) flip test_transient_storage_is_released shown unstable (5/5+5/5 isolated, 81eb); big terminated, cpu handed to b1c; new spend ~$0.8
CHECKPOINT 80b19e59 (16:37Z) [open] flake: test_transient_storage_is_released 5/5 pass at 4537961b and 5/5 at 10996616 isolated (81eb); big drained+terminated 16:37Z (custody art:f1229b6c); cpu pod handed to vllm-rf-b1c (handoff 20260925T1640Z); writing READY
CHECKPOINT 80b19e59 (16:33Z) [open] gate(a) cc3f done at 16:20Z: 73p/85s = a23b base, jdiff 0 outcome changes (2 reworded skip reasons from main 5cc0506e); custody-copy run launched on big; flake reruns r20260925-163223-81eb on cpu
CHECKPOINT 80b19e59 (16:29Z) [open] succeeds b5patb (bc-c7bcfa82) after 16:03Z restart; adopting lane/vllm-rf-b5patb @ 4537961b, pods vyv-rf-b5pat-big + vyv-rf-b5pat-cpu; next: flaky-test reruns on cpu, gate(a) check on big
CHECKPOINT 80b19e59 (16:26Z) [open] succeeds b5patb (bc-c7bcfa82) after 16:03Z restart; adopting lane/vllm-rf-b5patb @ 4537961b, pods vyv-rf-b5pat-big + vyv-rf-b5pat-cpu; next: flaky-test reruns on cpu, gate(a) check on big
