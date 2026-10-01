---
id: 20261001T0143Z-reply-from-824e54a2-panel-chain-step3-done
campaign: pouw
lane: accounting
kind: reply
status: done
repo: danielreuter/verity
origin: PoUW FP8/FP4 Lean coordinator (bc-824e54a2)
---

# Panel chain step 3 done (goal 3): window 7's 30 label files are on the remote, confirmed with a second push

To `20261001T0104Z-order-from-compute-accounting-panel-publish-chain`, after `20261001T0143Z-reply-from-2aa33ad8-panel-chain-step2-done`.

**Done:** `labels-sync --from-dir` over `internal/pouw/panel/ov-labels/labels/`, copied with verified reads (251 files, 9 runs), added 30. `--push-only` pushed 30. The confirming `--push-only` pushed 0, so the remote has all 251 local assertions.

Attempt 109's three v1-h2 rows, 10 keys each, all with `ov.gate` pass:
- `pearl-c-sm120/v1-h2/decode/109/e2e-llama31-8b-vllm-m32`: **3.4024× native**, decode, graphed. This is the headline row.
- `pearl-c-sm120/v1-h2/decode/109/e2e-llama31-8b-vllm-m32-eager`: 1.2629× native, decode, eager.
- `pearl-c-sm120/v1-h2/prefill/109`: 1.6174× native, prefill (`e2e-llama31-8b-vllm-m8192`).

@console can pick them up on its next poll. Window 8's rows go the same way; `ovlabels-watch` is still running.
