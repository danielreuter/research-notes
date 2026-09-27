---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness · created: 2026-09-27T15:35Z · re: `δ_link` under expected-time collision resistance (Daniel, 14:34Z)

# The link theorem you'll discharge `LinkSound` with: its shape, and what changes from `analysisB`

Daniel adopted expected-time collision resistance of SHA-512 for the audit's value layer. It is A2, `Assumptions.SHA512ExpectedTimeCR`, in [#127](https://github.com/danielreuter/verity/pull/127). The plan is `note:20260927T1510Z-draft-expected-time-link-plan`, and §3 of that note is your interface.

- **A new analysis replaces `analysisB` for the link.** The extractor stops after `k` *accepted* reruns, rather than `Kr` reruns. `ks` and `link` are scaled by `c/(c−1)`, and `cover` comes from the relative bound. I'll call it `analysisBE`. Your composition with `extraction_audit_count` stays the same.
- **What you'll get:**
  - `flock_batched_knowledgeSoundE`: `ε_ks` is `c/(c−1)·E_ω[ε_c⁻ + √(k·adv₀)]`.
  - `flock_batched_countE`: the count curve, with `δ_link` still named.
  - Later, `flock_batched_linkSoundE`, with `δ_link` the record term `t·N_s(8N₀/e)/2^256.5` up to lower-order terms. It takes A2 for the explicit finder it builds, plus `ValueBinding`.
- **`ValueBinding` is new and named**, like `LoweringSoundB`. A satisfying witness opens each io wire's registered commit string, and two openings of one string with different values give a SHA-512 collision. M0's `hm96-sha512` leaf layout discharges it, by you or me, whoever gets there first.
- **Landed:** S1–S2, in draft [#163](https://github.com/danielreuter/verity/pull/163): `session_knowledge_sound_acc`, `Extract.expectAcc`. S3, `analysisBE`, is next.
