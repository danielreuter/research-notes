---
id: 20260930T2158Z-handoff-from-infra-refuse-gpus-without-queue
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: a small follow-up from the old research coordinator's review of `--queue`: refuse `--gpus` and `--cpus` without `--queue`

The review (2:55 PM PDT, Slack thread `1790805314.862369`) found nothing blocking, and the name `--queue` stays. `--queue` (27676a80c) is in
train TQR (slot b, `r20260930-215427-4867`, expected merge `1ae8d5a1`), stacked on TIS (#592) and TCL (#586). All three should land
by about 3:45 PM PDT.

**Follow-up PR, after TQR lands:** `research run` should refuse `--gpus` and `--cpus` given without `--queue`. Today it accepts them and
then ignores them.
