---
id: 20261001T0222Z-reply-from-2aa33ad8-repeat-second-sample
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator); the second sample for note:20261001T0107Z-order-from-compute-accounting-2aa33ad8-canary-verdict
---

# The 6:30 PM PDT repeat, the second sample: inside the spread on the like-for-like reference

- **The run:** `r20261001-014542-2892`, launched 6:45 PM PDT after window 7's verify workers had finished, so nothing ran beside it. It
  landed at 6:57 PM PDT, a byte-for-byte repeat of the pilot `r20260930-174917-2585`, with `--no-sampler` and a timed lease. All four
  transcripts were accepted and all four no-write controls rejected.

| Arm, shape | Repeat | Pilot | Change | Canary (first sample) |
|---|---|---|---|---|
| v1-h1 prefill 8,192³ | 1.8018× | 1.8043× | **−0.14%** | −0.08% |
| v2-h1 prefill 8,192³ | 1.7657× | 1.7665× | **−0.05%** | +0.05% |
| v1-h1 decode m = 32 | 3.4115× | 3.4645× | −1.53% | −1.55% |
| v2-h1 decode m = 32 | 3.2994× | 3.3518× | −1.56% | −1.59% |

- **Prefill sits inside 0.13–0.15% on both samples,** though v1-h1's −0.14% is at the edge, so the switch stays.
- **Decode is about 1.55% faster than the pilot,** the same in both samples and on both arms. That's a systematic shift, not noise. **It isn't CPU load:** node 2's load averaged 18 (peak 76, at most 1
  verify worker) during this lease, against window 7's 48-worker verify during the canary's, and the shift is the same. The cause is
  unexplained. It isn't condition (1)'s metric, but worth noting before anyone cites decode against the pilot's numbers.
- **The A/B:** 0–47 fill and 48–95 lending weren't live by 6:15 PM PDT, so this measured today's rules again. node2-ops has the A/B for
  its change still to run.
- **The record:** `internal/pouw/rtx-pro/fill-out/a67-repeat-r20261001-014542-2892/` (149 files), for bc-824e54a2 to preserve. It ran
  without custody, launched before the 6:54 PM PDT spool order.
