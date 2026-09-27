---
cursor:
  subagentId: "bc-21aca6c8-631a-51fd-8553-ad0d0947ad11"
---

G1 FAIL again at 8:50 AM PT, Sep 25 (run `r20260925-154936-70d5`; an earlier attempt, `r20260925-154003-7f2c`, was spoiled when a RunPod host never answered ssh): pod create with `--register` (34 s), `run --on`, the G2 refusal and self-cleanup all worked again, but `research notes sync` still got a 403, because the GitHub token Cursor issues to this cloud agent is scoped to `danielreuter/verity` only (both of its tokens show `push: false`, even `pull: false`, on `research-notes`), so the app-level grant doesn't reach agents started for `verity`; the fix is a notes-scoped credential for cloud agents, such as a fine-grained token for `research-notes` stored as a Cursor secret, or confirming the grant reaches newly started agents. (First failure: 2:28 AM PT, run `r20260925-092659-c0ed`, same 403.)
