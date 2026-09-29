---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note (decision needed) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-29T13:18Z · re: the follow-up epoch GO (13:04Z)

# #74's $52 cap ends its job during the Match: raise it to about $75, or accept a Build-and-Match row?

- **#74 launched at 13:15Z:** run `r20260929-131456-4007` on `vyv-rf-epoch-74`, a secure 2× H100 at $6.98/h with 503 GB. The cap buys
  7.45 h, so the run's timeout is 6.78 h and its job's last stage must end by **19:22Z**, which leaves the 40-minute store reserve inside.
- **The estimate from last epoch's #74 on the same shape:**
  - Bootstrap about 0.3 h and Build about 4.9 h, to about 18:35Z;
  - then the call-boundaries gate (#351), 0.5 h, to about 19:05Z;
  - then the Match, about 1 h, and the 3-pair Commit, about 2.8 h.

  So the deadline stops the Match. The Build and records are stored, the row is deferred, and there's no Commit.
- **To reach the Commit:** a cap of about **$75** gives 10.7 h, ending about 23:55Z. That's inside the line's 12 h per pod, and $23 more of the
  $260. Today's committed caps are $130 (the five GO rows), $183 with the held ones.
- **What I need from you:** raise #74's cap (I'd extend its run with `tele set-timeout` and its lease with `research pods extend`), or leave it.
  Without an answer, #74 stops at its deadline as designed.
