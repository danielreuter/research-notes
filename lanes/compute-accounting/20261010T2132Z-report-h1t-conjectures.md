---
id: 20261010T2132Z-report-h1t-conjectures
campaign: pouw
lane: compute-accounting
kind: report
status: final
repo: danielreuter/verity
origin: compute-accounting worker bc-555cb717-d533-52e3-9144-3e84c602a32d
---

#1736 at 72169f483a40e92ece949caf484b997cd440b29a: `DistinctLiveH1T` is an open conjecture in the Security lock, with a salt-sampled falsification test (`verity/core/protocols/pouw/tests/test_h1t_conjectures.py::test_distinct_live_h1t`), and h1tGamma is listed again, frozen, resting on it. `HalfApartH1T`'s test runs, but no theorem reads it, so it isn't in the lock. No counterexample was found. Lean check `--update` run r20261010-204158-0f88.
