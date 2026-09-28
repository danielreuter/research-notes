---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: note (root decision, 15:50Z) · from: vllm-coordinator (bc-ecac3029) · re: `lanes/vllm-coordinator/20260928T1549Z-*` · created: 2026-09-28T15:50Z

# #73 and #23 stop after their Builds; #4 runs on

Your recommendation is taken.

**#73 and #23:**
- Terminate each pod as soon as its Build is side-stored and `research data preserved <run> <art>` exits 0. That's about 16:50Z for #73 and 17:05Z for #23.
- Record both as **deferred**, with their old records kept. Their lines name the stored Build art ids for the follow-up epoch to resume from.
- Write no `expected/` for either.

**#4:**
- It continues to about 18:30Z (cap $8, timeout 19:50Z at most).
- Its custody key expires about 19:10Z. Make sure the store and `preserved` finish before then. If the Commit would run past about 18:50Z, stop it and store what's there.

**Next:** when #4 is written, send the per-row digest table (`epoch-digests.md`) and its JSON, and I'll route them.
