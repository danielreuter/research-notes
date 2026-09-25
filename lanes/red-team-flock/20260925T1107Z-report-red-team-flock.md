---
lane: red-team-flock
kind: report
created: 2026-09-25T11:07Z
status: open
---

CHECKPOINT 3301c435 (11:14Z) [open] findings so far: live-coin challenger absent (verifier is FS-only); reps commit separately + Mixed binding has no public io -> rep1 can be an honest proof of another witness (no squaring vs link); AG r1 nonce freedom (aarch64 only). Next: cheap CPU pod demo of unlinked reps
CHECKPOINT 3301c435 (11:12Z) [open] paper+code review of flock b684b12 (public clone) + flock-128 harness (art:4cc09936 inputs): query term -97.77/run reproduced from TOMLs; fixed inner zerocheck prefix lossless (x86 RS path); candidate BREAK: reps commit separately, link binds one root. Next: verify live-coin/FS gates, union verifier
CHECKPOINT 3301c435 (11:07Z) [open] started 11:08Z: setup done, read contract/brief/flock-128 report+PARAMETERS handoff; inbox empty. Next: red-team-link §3-4, TABLES, flock-128 evidence (accounting.py, census, configs, harness patch)
