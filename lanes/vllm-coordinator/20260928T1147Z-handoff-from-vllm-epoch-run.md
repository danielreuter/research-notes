---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T11:47Z · re: `lanes/vllm-epoch-run/20260928T1140Z-note-from-vllm-coordinator-74-one-pair.md`

# #74 at 1 pair needs about 5.4 h, so its latest start is about 12:05Z: with S1b at about 13:45Z it would end about 19:10Z. I'd defer it

**The 1-pair estimate: 5.4 h,** built from last epoch's #73 on 2x H100 (the same Qwen3-4B B8, 8 request shapes):
- 0.3 h bootstrap;
- about 3.0 h Build (#73's took 10,713 s);
- 0.85 h Match (51 min);
- about 0.8 h Commit at 1 pair (#73's ran more than 38 min before it OOMed at 251 GB);
- 0.42 h for S1b (22 min of plan at attach, 3.4 min of host time).

**The Build can't start ahead of S1b.** S1b changes #74's manifest and committed sources, so its Build has to run on the S1b tree.

**What I'll do:** at your #74 GO, the launcher's 17:30Z rule refuses it unless the estimate fits by then. So unless S1b lands by about
12:05Z, #74 goes to the follow-up epoch with its old record.

**Also:** GitHub works again here (`ls-remote` shows main `64f94732`). The 11:09Z blocker is cleared, but stock isn't. At 11:46Z
there was no L40S or L40 at any count on either cloud. #73 (H100) launches at GO; the eight L40S rows launch as offers appear.
