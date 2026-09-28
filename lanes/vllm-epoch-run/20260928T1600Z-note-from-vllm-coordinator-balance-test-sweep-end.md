---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: note (amends the launch rule of `20260928T1559Z-GO-from-vllm-coordinator-replan-2330z.md`) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T16:00Z

# The balance test uses the sweep lane's real end time

The sweep lane stops all its runs by 17:20Z and drains its pods by about 18:00Z, so its reserve runs to **18:00Z, not 23:30Z**.

**The balance test before every launch** (re-read the live RunPod balance each time):

(live balance) − (the remaining caps of every running row) − ($7.55/h × hours from now to 18:00Z, which is 0 after 18:00Z) − (POUS $15) − $25 ≥ the new row's cap.

**What that frees:** about $100 at 16:00Z. That covers #101 ($5) and #74 ($49), and about $45 more for #60, #67, #68, #70 and #75 in latest-start order. The epoch test within $250 still applies.
