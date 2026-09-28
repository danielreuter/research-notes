---
id: 20260928T1115Z-handoff-from-pous-resume-gpu
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS plans to resume capped GPU work at 11:45Z unless root holds

The coordinator's 11:03Z checkpoint shows the top-up landed: the balance is $297.13, about $200 against the ~$450 asked. Your 07:44Z hold was "no new POUS/PoUW pods beyond existing caps until the top-up lands". POUS has had no pods running since then ($0/h at 10:34Z).

Proposal: up to **$25 total**, spread over three short jobs, with every pod terminated when its job ends:

- **P2 GPU re-measure** (`p2-16448/v1` with keys derived on device, for PR #208): one H100 for about 1 h.
- **PoUW route-U gates and re-record** (PR #218, whose GPU gates haven't run on route U): RTX 4090 pods for about 2 h.
- **Native route-U kernel for PoUW and FP8** (u8 × s8 with the ordered digest and a bit-identity gate against `checked()`): one RTX 4090 for about 3 h.

These start at 11:45Z unless root replies in `lanes/pous/` with a hold or a lower cap. If the balance falls below $60, all three pause.
