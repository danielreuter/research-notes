---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-config-run-tp2 (bc-35ab914e) · kind: handoff (PRIORITY 1) · from: @old-circuits-and-proofs · created: 2026-09-30T21:12Z (2:12 PM PDT)

# PR A/B are priority 1. Put the Phi-3 B8 probe in now

**Why:** node 1 was 4% GPU-busy from 1 to 2 PM PDT, and the in-Commit replay is the biggest cause. Daniel's target is ≥ 60% by 3:30 PM PDT.

1. **Drop `/tmp/resubmit.sh`'s ">6 waiting" gate** for `cfgtp2-deferred-phi3b8g`. Submit it now. @circuits asked @infra to admit it at top priority.
2. **When it passes, write a `-handoff-` at once** with:
   - the roots and 460/460 vs in-process;
   - the GPU hold with and without deferral;
   - the flipped-byte negative;
   - **the replay task's measured peak memory and the bundle size**. The template asks 64 GB, and bundles can reach about 90 GB; send those two numbers to the steward too.

   I grant #599 (PR A) and #598 (PR B) in the same turn.
3. **#503 overlap** (from epoch-run): #503's uniform replay draw had to be ported into PR A's `c2_replay.py` and `replay_bundle.ARGS`. Whichever of #503 and PR A lands second needs those two lines. Say which you've done.

**The GPU-less 2-rank TP2 Build goes to a separate new lane**, so it runs in parallel with you. Stay on PR A/B.
