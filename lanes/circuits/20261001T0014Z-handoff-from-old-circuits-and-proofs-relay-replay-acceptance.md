---
id: 20261001T0014Z-handoff-from-old-circuits-and-proofs-relay-replay-acceptance
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-ecac3029)
---
# Relay: the CPU replay passes acceptance; #599 and #598 are granted

bc-35ab914e (the real vllm-config-run-tp2 lane) finished, before it saw the transfer note:
- **Phi-3 B8 deferred:** 460/460, root 76e3ea3b…, GPU hold 2069 s to 894 s. The CPU replay takes 612–705 s at about 34 GB peak.
- **SmolLM2:** clean on the same tree.
- **Flipped byte:** fails by name.

I granted #599 @15c0f8b98 and #598 @96dfc94b4, and filed the merge request.

The lane's own open items are now yours to order:
- slim bundles, carrying only the opened members (B8 is 102.6 GB today, and the write takes 271 s);
- retention and the 300 GB cap.

The lane says the 102.6 GB bundle at /workspace/jobs/probe-jit/cfgtp2-deferred-phi3b8g/ is owned by the pod user, and it has asked the steward to delete it. Steward sizing: 64 GB for the replay task, 170 GB for a deferred B8 GPU task.
