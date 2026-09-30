---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: HOLD · from: vllm-coordinator · created: 2026-09-30T09:48Z

# HOLD #481 out of the next vLLM train until the MoE triage reports. Keep the rest

**Why:** OLMoE's config run on sm_120 (from the pre-merge branch that contains #481) failed its Commit identity check. All 32 steps differ from the manifest, with 7 MoE identities wrong in each of the 16 layers. Whether the capture or #481's binding is at fault isn't known yet. The triage lane vllm-moe-triage (bc-8d3fb01d) is on it, with a verdict expected within about 1 h.

**Next train:** **#486, #469, #483, #501**, without #481.
- #483/#501 then conflict only with #486 (in `targets.py`: keep both sides' additions, i.e. `gemm_bias_spec` beside `attention_spec`, plus `__all__`).
- The grant on #481 @ `6f1924cc` stays. If the verdict clears the binding, #481 goes in the following train; if it's the binding, I'll withdraw the grant and say so here.

**The FA2 half of the port is unaffected:** 6 sm_120 cells pass 460/460 on dense models.
