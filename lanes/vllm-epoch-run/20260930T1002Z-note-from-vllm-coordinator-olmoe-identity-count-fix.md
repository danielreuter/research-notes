---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T10:02Z

**OLMoE's failure is a counting bug, not #481.** The Commit's identity check counts the router-softmax tap's `moe/L<k>/router_softmax` as a seventh MoE tensor and fails. The values are exact: your run `r20260930-091912-128d` replayed 460/460, all MoE families included. The triage handoff is `lanes/vllm-coordinator/20260930T1000Z-handoff-from-vllm-moe-triage-verdict-capture-identity-count-not-481.md`.

**Fix:** [#528](https://github.com/danielreuter/verity/pull/528) @ `67793c90c667bce515ce78cff0f4bd6f1be3d64f`, granted.
- **Merge it into your run branch** and re-run OLMoE and Qwen3-30B-A3B with the router tap **on** (the default). Don't turn the tap off to pass: that commits less of the router.
- `ov.note` adds `#528` to the pre-merge prefix.
- **Relabel OLMoE's `fail`:** until the re-run passes, label the old attempt `fail` with `ov.note "identity-count bug with router tap (#528); replay 460/460"`, so the table names the cause.
- **Qwen3-30B-A3B:** if it already failed the same way, it gets the same note.
