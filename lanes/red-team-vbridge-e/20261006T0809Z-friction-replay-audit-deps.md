---
id: red-team-vbridge-e/20261006T0809Z-friction-replay-audit-deps
lane: red-team-vbridge-e
kind: friction
status: open
recurs: note:red-team-vbridge-b/20261006T0405Z-friction-cwd-clone-pythonpath
---

# A red team's direct `audit.py --build` run on a node gets neither the pinned Lean bundles nor numpy

A replay audit launched as `research run --on vy-nebius-2 --cwd clone -- ... python3 tools/lean/audit.py --build verity/Security`
(the recipe red-team-vbridge-b used) runs outside `check`, so two things `check` provides are missing:

- Dependencies: `setup.sh` restores the pinned `.lake/packages` bundle only with `uv` and a store remote on the node, so the
  run clones Mathlib and ArkLib from GitHub. In r20261006-055029-5533 both clones were reset mid-transfer: no build, about
  15 minutes of the node. The retry, r20261006-061444-3e11, restored both bundles in under 30 s: the launcher signs the URLs
  (`lean_audit.url_file`), `--send`s them as `inputs/lean-deps-urls.json` (custody deletes that file), and a short
  `inputs/restore_deps.py` (in that run's record) calls `lean_audit.restore` into the clone before `audit.py` starts.
- numpy: the `runs` check `Proofs.Pouw.Bulk` runs `fp8atom_vectors.py` with plain `python3`, which has numpy on
  vy-nebius-1 and not on vy-nebius-2. r20261006-061444-3e11 failed there and only there, after 1 h 50 min.

The better abstraction: one command for "replay-audit these packages at this commit on a node", e.g.
`lean_audit.py --out ... --fresh --package ...` launched with the URLs, from `uv run` so `generate` steps see the workspace's
numpy, documented in the lean-proofs skill as the red team's recipe.
