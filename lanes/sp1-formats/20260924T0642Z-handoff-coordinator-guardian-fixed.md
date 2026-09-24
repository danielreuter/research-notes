---
lane: sp1-formats
kind: handoff
from: coordinator
created: 2026-09-24T06:42Z
---

# Your `research run --on vy-sp1f-4090 ... sp1.bootstrap` was killed a second time (06:40:04Z, laptop guardian): rerun it

Reason this time: swap 95% full (it cannot grow, the disk is low) while RAM was 49% free. I changed the guardian at 06:42Z:
the swap rule now also needs RAM under 25% free, and the disk rule fires at 3.5 GiB instead of 6 GiB. Your launcher was the
victim both times because it holds ~0.6 GB on the laptop for the whole bootstrap; for long pod steps prefer a detached
`nohup ... &` over `research pods ssh` so nothing long-lived sits on the laptop.
