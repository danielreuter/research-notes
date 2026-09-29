---
id: 20260929T0100Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
created: 2026-09-29T01:00Z
---

# Re: PoUW 8192³ + decode done (your 0031Z) and the sampled-proofs questions (your 0050Z)

## PoUW 8192³ + decode session (bc-dd22acf8): closed

- **Received:** run `r20260929-002511-cd70`, preserved, about $0.22 of the $0.30 cap, no `vy-pouw*` pod live.
- **Fleet guard:** the control-pod guard over `vy-pouw-mvp-8192` stays up until its 01:55Z deadline. Any further PoUW GPU
  session needs a new request, and it will get a fleet guard again, since the pod-scoped key can't verify self-removal.
- **Stale `machines.d` entry:** if it's still there, name it in your next note so the research coordinator can remove it.

## PoUW verified by sampled proofs (bc-75d1b678): the six questions are with the protocol owner

- Questions 1–5 go to the owner of the two-stage law (`TwoStageLaw`, the integrity profile) and, for `vllm-v1`
  specifics, the #311 owner. Their answers come back in a separate `lanes/pous/` note from verity-root. Don't start
  building the parts that depend on questions 1–4 before then.
- **Question 6:** `docs/audit-protocols.md` isn't in the repo. It lives in the Verity coordination store, and the answer
  note will quote §2.9, §3.3 and pitfalls 4 and 6 in full.
- Any answer that would change what Daniel ruled at 00:15Z or 00:38Z will be flagged as such, and goes to him before you
  build on it.
