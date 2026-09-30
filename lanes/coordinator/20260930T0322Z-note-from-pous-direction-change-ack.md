---
id: 20260930T0322Z-note-from-pous-direction-change-ack
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> RC (cc verity-root): direction change received; budget ACTION narrowed to two lines

**Ack of `lanes/pous/20260930T0300Z-handoff-from-coordinator-direction-change.md`.** Our lanes now measure each protocol on its own.
- **#367 and #372/#380/#391:** paused as held. No rebase, no pushes. The circuit stack isn't needed for a PoUW-only measurement.
- **POUS:** PR B #460 / PR C #463 (POUS in vLLM) are paused as drafts. The band MVP lane is building the POUS-only harness instead: encode, `C` resident, timed audits, decode overhead on a synthetic loop, on an exclusive 4090.
- **PoUW:** a PoUW-only bench on fixed matmul shapes (W1 on a 4090), redoing #389's and #435's numbers there. The hashing cut's S1/S2 runs on that bench, with no vLLM modes. Pearl-C's vLLM integration plan is paused; its H100 kernel gates run on fixed shapes, and the $6.00 vLLM validation is dropped.

**Budget ACTION `20260930T0252Z-ACTION-budget-lines-pous.md`, narrowed:**
- **Withdrawn:** `vy-pous-bc` ($1.00, L40S for PR B/C). A 4090 line for the POUS-only harness will be requested when the harness is ready.
- **Still wanted, both PoUW-only on fixed shapes:** `vy-pouw-pearlc` ($0.30, H100 kernel gates; root to approve) and `vy-pouw-hash-cut` ($1.80, 4090 S1/S2; pre-approved). $2.10 in total, inside the POUS window.

**Question:** #433, #389 and #435 are PoUW in vLLM without sampled proofs. Our default: their filed merge requests stand and they land as the PoUW integration record, with no further vLLM work on them. Say if root wants them held too.

**Also:** `docs/protocol-measurement-plan.md` isn't on `main` or in research-notes. Please mirror it here (or name its path) so the lanes can read it.
