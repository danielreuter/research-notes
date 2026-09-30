---
id: 20260930T1330Z-note-from-pous-471-stacked-on-433
campaign: pous
lane: verity-root
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# pous -> verity root: #471 is now stacked on #433

Update to the queued deployment-audit PRs (#471, #472, #473).

- **#471** (ncp-v2 and adapter guard) now has head `bf81f77f` and base #433's branch `cursor/pouw-audit-per-forward-fp8-4f91`, to remove the overlap with the MVP's #433. Its diff against #433 is nine files (ncp-v2 and the PoUW adapter). It adds one guard #433 lacks: a layer carrying a quantization parameter (`weight_scale`, `weight_packed`) is refused whatever its weight's type, with its own test.
- **Order:** after #433. Retarget #471 to `main` once #433 lands. The extra commits GitHub lists under #471 are `main` commits missing from #433's older base; they drop out when the base returns to `main`.
- **Recorded check:** needed at train time on a machine with the evidence store. One `verity-vllm` test (`test_tp_moe_members`, a Qwen3-30B TP manifest build) was killed for memory at 11.4 GB on the author's 15 GB VM. That comes from #433's older base; `main` recalibrated it at `a046c130`, so run the check after #433 is brought up to `main`, or on the CI pod.
- #472 and #473 are unchanged.
