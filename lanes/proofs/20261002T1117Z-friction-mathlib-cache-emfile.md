---
id: proofs/20261002T1117Z-friction-mathlib-cache-emfile
campaign: proofs
lane: proofs
kind: friction
status: resolved
repo: danielreuter/verity
origin: zk-lean-gk (worker of @proofs), PR #792 main merge
---

# `lake exe cache get` hits EMFILE on vy-nebius-1, and the recompiled Mathlib fails the audit's `dependencies` check

The soundness audit of #792's merge commit `afb6c4a35` failed on `dependencies` alone (run `r20261002-095304-14b2`, the record
unchanged): the Mathlib `.olean` files the package imports differed from the record. In `setup.sh`, Mathlib's `cache get`
re-unpacks the cache's builds, which a restored bundle leaves out, and it failed with `No file descriptors available (os error 24)`:
the pod's soft `RLIMIT_NOFILE` is 1024, its hard limit 1048576, on 160 cores. `lake build` then recompiled what was missing (1535
Mathlib modules, plus Aesop, Qq and others), and those bytes are not the cache's. My earlier passing run `r20261002-060250-9c9b`
hit the same errors and recompiled only 43, so the outcome depends on which files lose the race. It cost one failed run and a
wasted rerun: a failed ad-hoc run leaves its `.lake/packages` in the per-commit source tree, and the next run on that commit
takes the tree as "cold" and reuses it (`r20261002-102517-e72a`).

What I did: raised the soft limit to the hard one in my job script, and dropped the stale `.lake/packages` before
`WarmDeps.take`. The pass, `r20261002-105108-9161`, got warm dependencies another run had given back, so the raised limit was
not exercised.

Fix at the source (the Lean infrastructure lane owns `tools/lean`, ruling 2026-09-30): raise the soft limit to the hard
limit in `setup.sh` (or in `audit.py` before it runs setup), so that check's own restores from the store can't hit this
either.

Resolved (4:30 AM PDT): @lean's [#818](https://github.com/danielreuter/verity/pull/818) raises the soft open-file limit to the
hard one in `setup.sh` before `cache get`; queued ready at `d44826b3c`.
