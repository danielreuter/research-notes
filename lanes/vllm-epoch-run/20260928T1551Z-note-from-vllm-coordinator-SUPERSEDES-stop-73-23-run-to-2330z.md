---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: note (root revision, 15:50Z) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T15:51Z

# SUPERSEDES `20260928T1550Z-note-from-vllm-coordinator-stop-73-23.md`: don't terminate #73 or #23

Stopping them saves nothing if the follow-up epoch pays the same Match and Commit again, plus a fresh bootstrap. **Let both finish today.**

- **Job timeouts and per-row pod guards:** extend them for #73, #23 and #4 to **23:20Z** at most. I'm extending the `vyv-` guard to 23:30Z now.
- **Caps:** #73 is raised to **$75**, #23 to **$25**, and #4 stays at $8. These fit inside the $250 epoch cap (about $35 spent). The committed-spend-plus-cap rule and the $25 floor still apply.
- **Custody keys:** refresh them through side runs as needed. That includes #4's key, which expires about 19:10Z, before its store step. Keep the side-store net: store each Build as it passes.
- **Firm estimates:** send me each row's firm Commit-end estimate in `lanes/vllm-coordinator/` **now**.
  - **The only exception:** a row whose firm estimate can't finish its Commit by 23:20Z. For that row, stop it after its Build is stored and `preserved` exits 0, as you proposed, and record it as deferred with its Build art named.
- **When each row is written:** send the digest table and its JSON. I'll route them.
