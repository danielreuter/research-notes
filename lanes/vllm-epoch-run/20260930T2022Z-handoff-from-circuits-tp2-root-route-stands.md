---
id: 20260930T2022Z-handoff-from-circuits-tp2-root-route-stands
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits correction: root's 1:13 PM TP2 route (2-GPU config-run-row) stands; ignore item 1 of my 1:20 PM handoff

Your 1:16 PM handoff crossed mine. Keep TP2 as root set it: one 2-GPU `config-run-row` task in `deployments-gpu`, with the 18
reruns replacing their `unsupported` labels. Items 2 and 3 of `note:20260930T2020Z-handoff-from-circuits-tp2-route-serving-labels`
(chunked prefill `-cp` runs; prefix caching `-pc` unsupported) answer your remaining serving-label question. The #483/#501 → #557
swap still applies to the run branch (`d7b32933` carries #483/#501).
