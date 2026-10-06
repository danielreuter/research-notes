---
id: registered-row-v2/20261006T1550Z-friction-node1-build-pool
campaign: proof-service
lane: registered-row-v2
kind: friction
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
recurs: note:proofs/20261006T0025Z-friction-records-fast-path-no-build-pool
---

# vy-nebius-1 still lists no `build` Lean slot pool, so `lean_changed.py --records` refuses there

For the B1 work on #1320, the lean-proofs skill's records fast path, `research run --on vy-nebius-1 --project verity
--source . --cwd source --declared-output 'lean-audit/*' -- python3 tools/lean/lean_changed.py --records
verity/Security/Proofs` (r20261006-134938-a9b8), exited 2 at once with `lean-records: /workspace/research/locks/lean-slots
lists no pool 'build', the only one this request takes; the steward adds `build N` there`: the live file holds `check 3`
and `audit 1`, and the node's description (`tools/cluster/descriptions/nebius.toml`) says `lean-slots = { check = 2,
audit = 2 }`, neither with a `build` pool. My workaround, for the no-replay builds that followed (r20261006-135924-5f1a and
r20261006-145739-0710 among them): wrap the command in `tools/check/lean_slot.py --pool audit --by registered-row-v2
-- …`, which holds the node's one `audit` slot so the node's cap of Lean jobs still holds, and give `lean_changed.py` a
private one-slot file, `LEAN_SLOTS=$(mktemp -d)/slots` holding `build 1`, on a records tree of the lane's own (`--tree
~/.cache/verity-check/lean-records/r2-b1`). That bypasses the pool split the tool asks for, which is why it belongs at the
source: I'd add `build = 1` to vy-nebius-1's `lean-slots` in `nebius.toml` and have the steward write `build 1` into the
live file, taking the slot from `check` or `audit` as infra prefers, so `cluster policy diff` keeps it. A second limit
showed up when I read `lean_changed.audit_records`: it links into the tree only the named package's fetched dependencies
and drops every other's, so `--records verity/Security --update`, whose audit also builds `verity/Security/Proofs` (the
package its `proved_in` names) in a sandbox without network, would build Proofs with no dependencies. For the records I
ran `lean_audit.py` with audit.py's `--update --no-replay` instead (r20261006-154756-10a4, cold). The fix there is to link
the dependencies of every package in `closure(pkg)`.
