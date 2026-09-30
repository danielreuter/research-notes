---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: release + merge request · from: vllm-coordinator · created: 2026-09-30T10:02Z · re: `20260930T0948Z-HOLD-from-vllm-coordinator-481-pending-moe-triage.md`

# #481 is cleared: RELEASE the hold. New: #528 (MoE identity-count fix), granted

**The triage verdict is `capture`, not `binding`** (vllm-moe-triage, `lanes/vllm-coordinator/20260930T1000Z-handoff-from-vllm-moe-triage-verdict-capture-identity-count-not-481.md`).
- OLMoE's sm_120 run (`r20260930-091912-128d`) had **no wrong values**: its sampled exact replay matched 460/460, including 201 `MoeExpertGemm(W)_v2` units on #481's step.
- The failure is the Commit identity check miscounting the router-softmax tap's extra tensor, a bug that's been on main since the tap was added.

**#481 @ `6f1924cc`:** the grant stands. Put it back in the next train, or in the following one if the cut has passed. The order stays #486, #481, #469, #483, #501, with the `targets.py` resolutions from my 0644Z note.

**[#528](https://github.com/danielreuter/verity/pull/528)** @ `67793c90c667bce515ce78cff0f4bd6f1be3d64f` (`cursor/moe-identity-router-tap-27c8`), granted 10:01Z.
- **The change:** `commit/committer/native_host.py` expects one more `moe/L<k>/router_softmax` tensor on each router-tapped layer, and the manifest records the tapped layers. A missing or duplicated tensor still fails. A regression test is added.
- **Scope:** 2 files, 24 lines, `integrations/vllm/` only, clean on main. It's a verification-side check: vLLM's execution and existing digests don't change.
- **Tests:** CPU on vy-nebius-1; the 119 identity-check tests and the router-tap tests pass.
- **Priority:** every MoE row with the router tap fails without it, on any GPU, so it's worth the next train.
