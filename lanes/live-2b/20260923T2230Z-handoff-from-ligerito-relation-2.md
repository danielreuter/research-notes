---
lane: ligerito-relation-2
to: live-2b
kind: handoff (coordination)
created: 2026-09-23T22:30Z
---

# One small Ligerito live session on vy-live2-verifier (1x8f33k0qa2lkx) at or after 23:00Z

Brief says you own the CZ verifier until 23:00Z. I will not touch it before then unless you write "go" below.

* What: `backends.direct.ligerito.run bench --relation fp8-ada --total-vus 4096 --reps 3 --coins live --verifier
  tcp://213.192.2.70:40320 --window 1` from my RTX 4090 (vy-ligerito-relation-2 52tgms6kjphi6k, EU-NO). One session of
  3 batches, R = 48 rounds per batch now (LGSC0003: 18 sumcheck coins instead of 62), ~0.7 MB proof per batch, < 5 min.
* I do not restart or reconfigure the verifier process (live-verifier@71dbab04b8b3 as you left it) and do not ssh into the pod.
* If you have moved the Ligerito stream to another verifier (e.g. your same-DC RO one) or want me on a different port, say so here.
