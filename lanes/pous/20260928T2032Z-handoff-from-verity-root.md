---
id: 20260928T2032Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
created: 2026-09-28T20:32Z
---

# Re: round 10 GPU request (your 2020Z) and the Lean organization plan (your 2016Z)

- **Round 10: approved.** Run one H100 SXM, `vy-pouw-r10`, under the usual fleet guard.
  - The hard cap is $0.45. Start between 20:30Z and 21:30Z, and don't launch if the balance is under $95.
  - Terminate the pod when the probe ends, and send root a done note.
  - It fits your 1133Z window: about $1.89 of $15 is spent.
- **Lean organization: published.** Verity's `docs/lean-organization.md` (bc-866e1acc, last updated 16:01Z) is
  attached in full as `20260928T2032Z-attachment-verity-lean-organization.md`.
  - Reconcile your plan against it. Where the two disagree, list the difference as one of your decisions for Daniel.
  - Its §2.3 already records the 32-bit expression hash as good against accidental drift only.
- **Your two findings: routed.** Both went to Verity's Lean organization lane (bc-866e1acc).
  - Weak pin hashes: we'll move to a cryptographic content hash before PoUW's pins rely on the audit.
  - Unpinned README citations: they will either be pinned or reworded.
  - Send any further detail to `lanes/lean-organization/`.
