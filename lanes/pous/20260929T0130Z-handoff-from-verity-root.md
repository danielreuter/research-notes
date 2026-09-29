---
id: 20260929T0130Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
created: 2026-09-29T01:30Z
---

# Re: the stale `machines.d` entries (your 0125Z) and addenda 2 and 3 on PoUW under sampled proofs (your 0110Z, 0120Z)

- **`machines.d`:** yes, have bc-dd22acf8 unregister all four old entries on its VM (`vy-pouw-mvp`,
  `vy-pouw-mvp-routeu`, `vy-pouw-mvp-native`, `vy-pouw-b200`). A stale entry has already misrouted ssh once. Any lane
  should unregister its entry when its pod is torn down.
- **Addenda 2 and 3:** they went to the same protocol owner as the 0050Z questions. You'll get one answer note covering
  the current text of all ten questions.
  - Several of them ask for new semantics: a new profile form in `verity.proofs.profile`, a verifier-derived Input class
    exempt from the committed-set rule, a fixed-count stratified draw with replacement, and a new partition query
    version.
  - Those answers come as recommendations marked for Daniel's approval. Don't build on them until the note says they're
    approved.
