---
id: core-firewall/20261007T1938Z-friction-path-require-rekeys-bundle
campaign: proof-service
lane: core-firewall
kind: friction
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
---

# A path require added to `Security/Proofs` re-keys its pinned bundle, and the re-key re-audits every Lean package

`Properties.Firewall` (branch `cursor/core-lean-firewall-2f22`) made `security_proofs` require `core_firewall` by path, so
its `lake-manifest.json` gained three path entries and nothing else. `lean_audit.deps_key` hashes the whole manifest, so
the key moved (`5177237fb2c7` to `14599830fa1b`). With no pin for the new key, `check`'s preflight refuses
`Security/Proofs` ("pins no bundle for its manifest and toolchain"), and its remedy is a cold `--export` run and `--pin`.

A bundle is `.lake/packages`, which holds only the fetched packages, so the old bundle serves the new manifest byte for byte.
The branch re-pinned it under the new key, as `tools/move/layout.py`'s `rekey_lean_deps` does after a move. Run
r20261007-193121-3504 on vy-nebius-cpu-1 restored it in 29 s ("dependencies from the store (14599830fa1b)").

Two costs remain, both from the tool, not from the change:

- Every PR that adds or moves a path require to a package with fetched dependencies must hand-edit
  `tools/verity/lean/lean-deps.json` or run a cold export.
- `lean-deps.json` is under `tools/verity/lean/`, which `lean_audit.tool_files` puts into every package's audit key. So
  the re-key also invalidates the passes of the packages the change never touched: here 4 of the 8, the Flock verifier,
  `core_protocol`, the certifier and the PoUS grader.

Recommended (not done here: the auditor is shared, and either change invalidates every pass once):

1. `deps_key`: hash the manifest's non-path entries (and the toolchain), not its bytes. That is what a bundle is a
   function of, and `rekey_lean_deps` already reasons that way.
2. `tool_files`: leave out `lean-deps.json`. The audit itself (`tools/verity/lean/check.py`) never reads it; only the
   launcher does, to choose where a bundle comes from, and the `dependencies` record already checks every `.olean` file a
   bundle supplies.
