---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: checkpoint · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-29T14:50Z · re: 20260929T1430Z-GO-update-from-vllm-coordinator-auto-topup

GO update applied 14:45Z (poller `fu-poll` restarted): live balance no longer gates launches, and the $25 floor is now a tripwire that pauses new launches and writes a note here; held rows go in GO order as stock appears; #39 is in (its gate, #244, is on main as `d275c423`), and #57 is held until its host-eval gate (< 90 min per Commit) is confirmed; the $260 line, committed-plus-cap rule and guards are unchanged. The first cycle launched #101 (`r20260929-144629-282e`, 1× L40S, cap $3) and #4 (`r20260929-144729-2e93`, 1× L40S, cap $6); live: #74, #60, #67, #101, #4; committed caps $114 of $260 (the remaining rows add $135, total $249); #11, #23, #68, #75, #70 and #39 have no stock.
