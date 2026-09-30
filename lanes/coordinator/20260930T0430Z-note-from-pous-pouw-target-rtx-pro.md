---
id: 20260930T0430Z-note-from-pous-pouw-target-rtx-pro
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> RC (cc verity-root): PoUW moves to FP8/FP4 on RTX PRO 6000 (Daniel, 04:24Z); two PoUW lines withdrawn

**Daniel's decision (04:24Z):**
- PoUW now targets FP8 or FP4 on the RTX PRO 6000 Blackwell (sm_120). It no longer targets the H100 (Pearl-C) or the 4090 (NCP-INT).
- Daniel is giving the PoUW work a persistent 8× RTX PRO 6000 server, with one agent per GPU. Access details are pending from him. Once they're in, we'll register it in `machines.d` for `research run --on`.
- This refines the 03:00Z direction change for PoUW. PoUW is still measured on its own, on fixed shapes, with no served model; the hardware is sm_120 instead of the 4090.

**Withdrawn from `20260930T0252Z-ACTION-budget-lines-pous.md` and `20260930T0322Z`:**
- `vy-pouw-pearlc` ($0.30, H100)
- `vy-pouw-hash-cut` ($1.80, 4090)

**Still wanted:** `vy-pous-harness-4090` ($1.15, `20260930T0352Z`). POUS isn't affected.

**Unchanged:**
- #433 → #389 → #435 stay the PoUW integration record.
- #464/#468/#475 (the 4090 hashing cut and bench) stay drafts. They're the templates for the sm_120 port.
- The Pearl-C protocol fixes in #449 (the red team's F1/F2 and the rest) continue, because they don't depend on hardware.
