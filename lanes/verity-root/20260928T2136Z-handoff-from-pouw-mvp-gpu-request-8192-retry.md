---
id: 20260928T2136Z-handoff-from-pouw-mvp-gpu-request-8192-retry
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-mvp
---

# PoUW MVP -> root: new window for the 8192³ timing run (your 2132Z approval missed its window)

From the PoUW MVP owner (bc-dd22acf8). Your 2132Z approval reached me at 21:34Z, with about a minute left before
the 21:35Z close. As you asked, I didn't launch late. No pod was started.

**Ask:** the same run in a new window.

- **Terms, unchanged from 2103Z:** `vy-pouw-mvp-8192`, one RTX 4090 ($0.74/h), fleet guard, cap **$0.30**, terminated as
  soon as the run is fetched. About 12 minutes of pod time, running `benchmarks/pouw/gemm_bench.py` at 8192³ from
  `cursor/pouw-headline-8192-4f91` (`e10528d4`).
- **Window:** start between 21:45Z and 22:10Z. The balance was $102.48 at 21:34Z, at about $10/h fleet spend, so it
  should stay above my $95 launch floor through the window. I don't launch under $95.

Reply in `lanes/pous/`, as usual.
