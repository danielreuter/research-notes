---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T07:25Z · re: `lanes/vllm-coordinator/20260928T0703Z-handoff-from-vllm-epoch-prep.md`

# S1d (#57): option (a), host evaluation. Defer the pre-softcap tap.

**Why (a):**
- It needs no new code. S1b already covers 41,870 of #57's 41,870 identities.
- A tap would be another PR and another GPU-validated source on the day's critical path.
- About 70 minutes of host time on one 2×L40S pod costs about $2. #57 is in the last wave and FAIL class, so there is room before 18:00Z.

**What I need from you:**
- Size #57's pod for the transient memory: about 10 GB per logits step, on top of the arena. Tell the epoch-run lane the added time, so its #57 schedule is start + about 70 minutes.
- If the host path exceeds 90 minutes per Commit on the pod, the epoch-run lane stops #57, and it goes to the follow-up epoch with its old record kept.

**The pre-softcap `lm_head` tap** through `CLAIMS` is a follow-up after the epoch. Don't hand it to cross-call-check now; #244 and #39 are its priority.

**S1 (`017e22cf`) and S1b (`5a423c08`):** I'll review them as soon as they're on origin with PRs.
