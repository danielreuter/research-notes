---
id: 20260928T2201Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
created: 2026-09-28T22:01Z
---

# Re: new window for the PoUW 8192³ timing run (your 2136Z)

- **Approved, with a wider window so publication delay can't make it miss again.** Same terms as 2103Z:
  `vy-pouw-mvp-8192`, one RTX 4090, fleet guard, cap $0.30, pod terminated as soon as the run is fetched, running
  `benchmarks/pouw/gemm_bench.py` at 8192³ from `cursor/pouw-headline-8192-4f91` (`e10528d4`).
- **Window:** launch any time until 22:45Z.
- **Launch floor:** $90, the POUS pause floor. For a $0.30 run you can use that instead of your $95. Don't launch if the
  balance is under $90.
