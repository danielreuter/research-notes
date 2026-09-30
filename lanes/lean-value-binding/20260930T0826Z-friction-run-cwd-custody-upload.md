---
id: lean-value-binding/20260930T0826Z-friction-run-cwd-custody-upload
lane: lean-value-binding
kind: friction
status: open
---

# `research run --on` runs a relative-path command in the run dir, and custody then uploads what it wrote there

`research run --on vy-nebius-1 -- bash -c 'P=backends/…/soundness; mkdir -p $P/.lake; cp -a <warm deps> $P/.lake/packages; …'`
without `--source` (then with `--source .` but without `--cwd source`) ran in `/workspace/research/runs/<run>/`. The copy of
the warm Lean dependencies (10 GB) landed in the run dir, `audit.py` wasn't found (rc 2), and custody then put all 9.5 GiB
of run files into the machine's store and began uploading them (`r20260930-080414-bae0`; its publish.log only warns "over
4 GiB"). I deleted the copy after the fact; the upload was already reading from the store's objects. That attempt is junk
and can be dropped from the store.

Fix ideas: refuse (or warn loudly) when `--on` has no `--cwd` and the command names relative paths that exist in the shipped
tree; and have custody refuse undeclared run files above a size cap instead of warning. The skill or the lane-setup page
could show a working recorded-audit command (`--source . --cwd source`, as lean-gemm-relation's runs had).
