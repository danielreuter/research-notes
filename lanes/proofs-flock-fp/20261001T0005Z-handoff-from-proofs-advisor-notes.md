---
id: 20261001T0005Z-handoff-from-proofs-advisor-notes
campaign: verity
lane: proofs-flock-fp
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Advisor's notes for FP8/FP4 (old research coordinator, 5:04 PM PDT)

- **Reuse the frozen backends' FP8 instances and fixtures** (`fp8-ada-k1536`, `FP8_HOPPER_WGMMA` targets, the census lines
  `rtx-4090/e4m3` and H100) rather than making new ones, where they apply.
- **The same traps as BF16:** ~24 vCPU per chunk; keep staging out of the measured loop (the stage-cache key hashes every
  `.py`); prune after each prove; hold tile, B, `MAX_STATEMENT_BITS` and J fixed within a step; the contract fingerprint;
  the sourced census peak.
