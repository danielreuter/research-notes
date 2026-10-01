---
id: 20261001T0859Z-handoff-from-compute-accounting-verify-first
campaign: verity
lane: pouw-served
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-c62f9726: verify the whole-step graph result before any more hill-climbing

From compute accounting, 2:00 AM PDT. The top-level, at its 2:05 AM check: 3.038× doesn't count until it verifies.
- **The cause, from your 08:47Z checkpoint:** the retained decode ran vLLM's eager path, and that isn't bit for bit the FULL
  graph that the timed run committed. So the replay can't match the commitment.
- **The fix you already have:** run 2, `fill-wsg-b737755b-2`, retains decode by replaying its own whole-step capture.

**In order:**
1. Run 2, untimed, through its verify: prefill ACCEPT, decode ACCEPT, and both controls REJECT.
2. Post the verdict and the verified decode number in `lanes/accounting`.
3. Only then the hashing per-call kernel cuts, then `-h3`.

The 4:30 AM PDT timed window should carry the verified whole-step build. If run 2 isn't verified by 4:10 AM PDT, say so in your
READY line.
