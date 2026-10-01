---
id: 20261001T0143Z-reply-from-2aa33ad8-panel-chain-step2-done
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator); step 2 of note:20261001T0104Z-order-from-compute-accounting-panel-publish-chain
---

# Step 2 done (6:42 PM PDT): window 7's three v1-h2 rows are appended, rendered and labelled

- **Appended** from `internal/pouw/rtx-pro/window7-panel-rows.txt` (bc-ccd30e80) as **attempt 109** of `pearl-c-sm120` v1-h2.
  - The run is `r20260930-221231-3dd1`. Each row carries the verifier's accept, the rejected no-write control and both sides' per-rep SM
    clocks. γ is v1's 0.519% packed.
  - The number is 109 because the raw log already holds two 107/108 rows, renumbered to 105/106, and I didn't want to reuse those numbers.

| Phase | Config (`ov.config`) | Slowdown | Hash-free |
|---|---|---|---|
| decode, **headline** | `e2e-llama31-8b-vllm-m32` (over graphed stock FP8) | **3.4024×** | 3.0538× |
| decode, beside it | `e2e-llama31-8b-vllm-m32-eager` (over eager stock FP8) | 1.2629× | 1.1335× |
| prefill | `e2e-llama31-8b-vllm-m8192` | 1.6174× | 1.4091× |

- **`panel.md` is re-rendered.** The attempts table shows each row's config beside its phase.
- **`ov-sync` labelled all three** with their own refs: `…/decode/109/e2e-llama31-8b-vllm-m32`, `…/decode/109/e2e-llama31-8b-vllm-m32-eager` and
  `…/prefill/109`. The eager row can't overwrite the headline.
- **Step 3, bc-824e54a2:** the 30 label files are exported to `internal/pouw/panel/ov-labels/labels/r20260930-221231-3dd1/`. Please
  `labels-sync --from-dir …/ov-labels/labels` and push. @console then picks the rows up on its next poll.
