---
lane: coordinator (verity-main-wt; lane/qol)
to: research-qol (verity-wt/rqol; lane/research-qol)
kind: handoff
created: 2026-09-23T20:30Z
decided_by: user, 20:25Z
---

# Research tooling: who owns what (two QoL lanes were editing the same package)

`lane/research-qol` and `lane/qol` both edit `tools/research` (six files overlap: README.md, cli.py, pods/part.py, store/cli.py,
store/local.py, tests/test_store.py).  A dry merge (`git merge-tree --write-tree lane/research-qol lane/qol`) conflicts only in `cli.py`,
trivially (both add adjacent docstring lines and adjacent new functions).  The user chose a split by area:

**research-qol owns** `research run` and remote execution, and store transport:
- the undeclared-tool derivation fix (argv into undeclared derivations; no reuse key without a declared Tool), confirmed on main
  `cli.py` `_prepare_store` (`ident = {"name": Path(command[0]).name, ...}`, `key = {}`);
- small-file packs, R2 throughput, source shipping / `READY.json`, a `research` version check for remote runs;
- `fold_record_pins`.

**lane/qol (coordinator) owns** interactive pod tooling, store CLI ergonomics, notes tooling, the Ligero pod recipe:
- `research pods ssh` / `research pods sync` (pods/connect.py; done) and `research pods stage TARGET ART...` (next: the pod pulls
  from R2 with a `research data mint-credential` credential, driven by art ids / fixtures.toml; replaces the STAGED.json scripts);
- short `art:` ids on `research data` (done), key params never redacted (done: `unredact_key_params` in cli.py), remote-unusable
  error text (done), dump-completeness check at registration, label vocabulary enforcement (`label` refuses unknown keys);
- `research notes checkpoint` / `research notes status`;
- `backends/direct/ligero/pod_bootstrap.sh` and `reverify.py`.

**Merge order:** hand off `lane/research-qol` by branch name when it is ready; the coordinator merges it into main first, then rebases
`lane/qol` onto the result and resolves `cli.py`.  Please do not re-implement `pods ssh/sync/stage` or the label vocabulary; tell me
here if something in lane/qol's area blocks you.

**Relationship between the two tree-shipping mechanisms** (keep both, they serve different uses): your `ship_source` puts an
immutable, verified source identity on a machine for `research run --source`; `pods sync` refreshes a mutable worktree that a lane
ssh-es into (`/workspace/src`, git-visible files only, prunes what it shipped, stamps `.research-source.json` from
`env.source_conditions`).  If you want one stamp format, say which fields you need and I'll match yours.
