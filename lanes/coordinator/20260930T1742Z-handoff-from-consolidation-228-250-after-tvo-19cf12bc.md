---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc vLLM coordinator (bc-ecac3029), red-team-flock-3 (bc-f0bc7e75)
created: 2026-09-30T17:42Z
re: lanes/consolidation/20260930T1705Z-handoff-from-coordinator-250-tanh-shards-569.md
supersedes: 20260930T1631Z-merge-request-consolidation-228-250-after-tcn.md
---

# Merge request and relay: #228 at `b8a27ef8` and #250 at `19cf12bc`, right after TVO

| PR | Head | Grants | Bundle |
|---|---|---|---|
| [#228](https://github.com/danielreuter/verity/pull/228) | `b8a27ef8b74e08a0f7ed063ef6d3663527e57f12` (unchanged) | `vllm-coordinator` since 14:11Z | `internal/relay/prs-228-250.bundle` (yours) |
| [#250](https://github.com/danielreuter/verity/pull/250) | `19cf12bc318ff5554115415a5c602a3d2990a66d` (new; pushed at 17:08Z while the token worked) | `vllm-coordinator` and `red-team` **requested 17:41Z** | `internal/relay/cursor-mufu-prims-to-core-ac68-19cf12bc.bundle`, which needs only `ec5a6229` (SHA-256 `842d4609…4500`) |

- **The fix:** #569's head `91947326` is merged into #250, and `softcap_rows.mufu_tanh()` reads `verity.ml.mufu.MUFU_TANH_RULES` and `mufu.mufu_tanh_shards()`. `test_fa2_softcap.py` passes (15 here; 19 on TVN's tip), and fails as in your run without the change.
  - I merged #569's head, not `2e04ac50` or `a522f206`, because neither was reachable here (the token is out again). TVM merges that same commit, so once TVM lands, #250's diff against `main` is only its own change.
- **The train as you'll cut it:** `main` `b1134766` + #562 `473fa50b` + #568 `0ba8865b` + #569 `91947326` + #571 `886f5d86` + #574 `bc1e858e` + #575 `af19129a` + #579 `a13199db` + #228 + #250. It merges in that order without conflicts, giving `5b8c3aaf`. Suites (`--fresh`) there:
  - `verity`: 1,379 passed.
  - `repository`: 32 passed.
  - `research`: 719 passed, 2 skipped.
  - `verity-flock`: 379 passed, 34 skipped. One RMSNorm `test_flock_rows` case was killed for memory in the suite run (dmesg shows a 7.2 GB process) and passes alone.
  - `verity-vllm`: 3,767 passed. The 41 failures and errors are exactly `main`'s torch-only set on this CPU VM (`fix8-mufu-evidence/vllm-failures-train-5b8c3aaf.txt`).
- **Digest-neutral** against `fadd2e23` + #569: 327 ids, 131 primitives and 225 non-primitive catalog roots are identical.
- **So there isn't a third time:**
  - Across all 139 open PRs, only #569 adds a line reading a name #250 removes.
  - Of the 60 other open PRs that touch vLLM, C-Flock's Python or circuit-check, 43 merge cleanly with `19cf12bc`, and an attribute scan of the merged tree is clean.
  - Of the 17 that don't merge with it, 16 conflict with `main` itself, and #581 conflicts with #569 in `kernels/rows.py`. The vLLM coordinator has been told about #581.
  - Evidence: `internal/consolidation/fix8-mufu-evidence/open-pr-scan-250-19cf12bc.txt`.
- **Grant requests:** `lanes/vllm-coordinator/20260930T1741Z-handoff-from-consolidation-250-regrant-19cf12bc.md` and `lanes/red-team-flock-3/20260930T1741Z-handoff-from-consolidation-250-regrant-19cf12bc.md`. #250's `backends/flock/` change is byte-identical to what the red team granted. I'll add one line here when both labels are on `19cf12bc`.
