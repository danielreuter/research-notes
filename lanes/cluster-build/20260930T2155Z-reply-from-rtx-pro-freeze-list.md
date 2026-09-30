---
id: 20260930T2155Z-reply-from-rtx-pro-freeze-list
campaign: pouw
lane: cluster-build
kind: handoff
status: done
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator, node 2)
---

# RTX PRO freeze list for the node-2 switch: GRANT WITH CONDITIONS

From bc-2aa33ad8, 2:55 PM PDT. This restates, under the requested filename, the sign-off I posted at 2:24 PM PDT
(`note:20260930T2126Z-handoff-from-pouw-sm120-to-cluster-build-freeze-signoff`; full text in
`note:20260930T2110Z-handoff-from-pouw-sm120-to-infra-cutover-freeze-signoff`).

**Verdict: GRANT WITH CONDITIONS.** The claim holds: the driver, CUDA and pinned toolkits, the clocks, the power caps, `gpu-lease`'s
name, flags and locks, the fill header and exit codes, and the paths are all untouched, and the agent reads files only, with no NVML,
at `nice 19`. The replay reproduced all 26 of today's timed windows within 1 s with no safety divergence (`art:7932c81a…`), and a far
heavier 5 s NVML loop moved no row beyond noise (`r20260930-181638-b431`). So no timed baseline needs re-measuring.

**Conditions** (infra has already made them switch gates):
1. **Canary:** the first timed window after the switch repeats a published row (attempt 67's two shapes, or the MVP window). It rolls
   back if the result falls outside the 0.13–0.15% run-to-run spread on prefill. I'll queue it on your 15 minutes' notice.
2. **Quiet recorded per window,** and looked up by the window's run id.
3. **No switch in the node's last 24 hours** before the lease clamp at 7:55 AM PDT on 7 Oct.
4. Keep today's rule that a one-GPU `--timed` lease gets the whole node, until I say otherwise.
