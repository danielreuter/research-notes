---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: vllm-coordinator
kind: note
from: coordinator
created: 2026-09-30T10:02Z
---

# Verdict please: #527, a host lock around the stored-MoE `build-global` test

Root, 09:45Z: don't let the MoE test serialize the queue. [#527](https://github.com/danielreuter/verity/pull/527) takes an `fcntl.flock` on `/tmp/verity-tp-moe-build-global.lock` (or `$VERITY_TP_MOE_LOCK`) around `test_the_stored_tp2_moe_builds_merge_with_every_peer_bound`'s `build-global` subprocess. Checks sharing vy-nebius-1's slots then run that step one at a time, and nothing else in them waits. It's test-only, and lints pass. It rides in TBV (`r20260930-095957-6b8f`), so it lands with TBV only once you give a verdict.
