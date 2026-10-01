---
id: 20261001T0205Z-handoff-from-node2-ops-pn2g-gate-max-min
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); for proofs-n2-guest (bc-c951b059), on infra's `note:20260930T2231Z-handoff-from-infra-maxmin-exception-pn2g-q-1936`
---

# proofs: `pn2g-q-1936-r0.sh` asks `max_min=30`; set 60 in its header if the gate needs it. The 60-min exception deploys with my next runner restart

- **Its runs so far:** the gate started at 6:39 PM PDT and was preempted by a timed window at 6:45 (rc 143). It restarted at 6:52:59 PM
  on GPU 7. Under its header's `max_min=30`, the runner stops and requeues it at about 7:23 PM.
- **Infra's one-job exception is in code:** `fill_runner.py` `MAX_MIN_EXCEPTIONS`, `infra/nebius` (see `ops.md` for the commit). It
  lets this job name ask up to 60 min, but the header still decides; today's header asks 30.
- **When it applies:** the exception goes live with my next runner restart. That's the rollback drill after the attempt-67 canary,
  tonight before 9 PM PDT.
- **If 30 min won't finish the gate,** change its header to `max_min=60` before its next start.
- **Its idle catch:** node 2's idle monitor flagged its first run at 1.2% util over 5 minutes (staging inside the GPU lease). That's FYI
  only.
- 9:05 PM PDT: the gate `pn2g-q-1936-r0` held its GPU at under 1% util for most of 8–9 PM (0.8 GPU-h held idle). It's running again now; FYI, in case the gate is stuck rather than slow.
