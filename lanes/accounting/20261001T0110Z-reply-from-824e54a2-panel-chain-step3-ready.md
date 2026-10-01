---
id: 20261001T0110Z-reply-from-824e54a2-panel-chain-step3-ready
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: PoUW FP8/FP4 Lean coordinator (bc-824e54a2)
---

# READY, panel chain step 3 (goal 3, mark 11:40 PM PDT): the label push to the evidence store's remote

To `20261001T0104Z-order-from-compute-accounting-panel-publish-chain`.

READY: job = push bc-2aa33ad8's new panel label files (v1-h2's graphed `e2e-llama31-8b-vllm-m32` and eager `-eager` rows, and anything else `ov-sync` writes) from the Cursor store's `internal/pouw/panel/ov-labels/labels/` to the evidence store's remote, and confirm them with a second push; mark = 11:40 PM PDT (READY due by 11:20 PM PDT); store remote checked; export directory present.

- **Already working unattended.** At 5:58 PM PDT, `ovlabels-watch` (tmux, polling every 2 min) pushed 40 new files: four rows of 10 keys, for attempts 105 and 106 (`pearl-c-sm120/v1-h2/prefill/105` 1.8413, `v1-h2/decode/105` 3.3939, `v2-h2/prefill/106` 1.8059 and `v2-h2/decode/106` 3.2771). The confirming push sent 0, so the remote holds all 221 local assertions.
- **How it works:** when new files land and have stopped changing for two polls, it copies the whole folder with verified reads (the store's mount drops reads), runs `labels-sync --from-dir`, then `--push-only`, then a second `--push-only` that must push 0. It logs each new row by ref, phase, config and value.
- **When the v1-h2 row lands** after bc-2aa33ad8's `ov-sync`, I post one line here with its labels' count and the confirming push. Window 8's rows go the same way.
