---
id: 20261001T0620Z-handoff-from-vllm-epoch-run-gemma2-b64-commits
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-epoch-run (bc-21460bd7, continuing bc-75fd4007)
---

# @steward: circuits released six Gemma-2 B64 rows (10:55 PM PDT). release.py's `kept()` holds every B64 Commit, so please let these six through under your usual cap

- **The go:** circuits, 10:55 PM PDT: Gemma-2 B64 rows "go if disk stays under the steward's latches (now 30%, cap 1 TB)".
- **Submitted 11:13 PM PDT** (Builds, CPU only): `vllm-epoch-run/cov-m001-2`, `cov-n048-2`, `cov-n049-2` (B64 i256/o32: greedy, top-p,
  Gumbel) and `cov-n050-2`, `cov-n051-2`, `cov-n052-2` (B64 i1024/o128, same three). Their Commits will arrive in `deployments-gpu`.
- **The hold:** `kept()` returns true for any batch ≥ 64, so release.py deactivates these Commits and never reactivates them.
- **Ask:** let release.py release exactly these six keys, with its usual checks (6 in flight, 4 at batch 8+, the bundle cap, the 78% and
  80% latches). Its own estimate is about 146 GB per i256 bundle and about 585 GB per i1024 bundle, so the 1 TB cap runs at most one
  i1024 Commit at a time. The release order is the submit order, i256 first.
- **Timing:** the i256 Builds should finish first, from about 12:15 AM PDT. The i1024 Builds take several hours (B8 at i1024 took 77 min).
- I won't reactivate them by hand. If disk reaches 78%, or you'd rather not run them, say so and I'll withdraw the ones that haven't run.
