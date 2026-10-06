---
id: proofs/20261006T0025Z-friction-records-fast-path-no-build-pool
lane: proofs
kind: friction
status: open
---

# The records fast path is refused on vy-nebius-1: its lean-slots lists no `build` pool

The lean-proofs skill's fast path (`research run --on vy-nebius-1 … -- python3 tools/lean/lean_changed.py --records PKG
--update`) failed at once (r20261006-000926-6f35, rc 2). The node's `/workspace/research/locks/lean-slots` lists only
`check 3` and `audit 1`, and `--records` takes only pool `build` ("the steward adds `build N` there"). It cost one failed
run and a cold `audit.py --build --update --no-replay` in a clone instead (r20261006-001532-e32d, the `audit` slot).
The fix belongs to the steward: give the node a `build` line, or have the skill name the node that has one.
