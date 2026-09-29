---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: checkpoint · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-29T17:05Z

Follow-up epoch at 17:05Z. Nine rows are live (#74, #60, #67, #4, #68, #11, #39, #75, #70); #23 has no stock and #57 is gated. #70 drew two COMMUNITY hosts with driver 550.163.01, which torch cu129 cannot use: each failed fast in about 6 min ($0.27 + $0.39), was requeued (`fu.py requeue`, at most two relaunches), and #70 now runs SECURE only (`r20260929-164634-7d85`, bootstrap OK). **#101 ran clean** (Build, Match, strict word check, Commit and store all PASS; $2.07), but its record stage never ran: the 964 MB / 12,892-file records upload took 47 min and finished after the job end, and `epoch_row.sh` gives the record stage the job end as its deadline, the same end that already reserves the store time (a flaw in #346: the record stage should be bounded by the run end, not the job end). I am rebuilding #101 off-pod from its preserved build and records artifacts (nothing was omitted) and will run `rebaseline run`, the gate and the write from that; any other row cut the same way gets the same recovery.
