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

## Two more slowdowns on the same work (added 2026-10-06T18:15Z)

**`lean_audit.py` keeps warm dependencies and builds only for the packages `--package` names, not for the packages their
audits build.** `_audit` takes in and gives back `WarmDeps` (`.lake/packages`, under `deps_key`) and `WarmBuilds`
(`.lake/build`, under `build_key`) only for the audited packages and the packages they require by path, then removes the
scratch tree. But `inputs()` also puts each audited package's `proved_in` packages (`provers()`) in that tree, and audit.py
builds them there, because the audit reads their builds. So the `--update --no-replay` audit of `verity/Security` alone
(r20261006-154756-10a4) logged a dependencies line and a build line for Security (`ffa0705a8465`, `7df98e6773c7`) and none
for Proofs, whose setup log shows Lake cloning ArkLib, Mathlib, CompPoly and VCVio; Security's report gives its audit step
2,374 s against 54 s for building Security itself, and Proofs' fetched dependencies and build went with the tree. A probe
at 16:17Z (r20261006-161719-39d0) found only lock files under Proofs' keys (`50ebab66d6fc`, `dd1d98bef8cf`) in the node's
store. The replay that followed, auditing both packages (r20261006-163809-de0f), found Security warm and Proofs cold
again: `Proofs: dependencies cold (50ebab66d6fc)`, `verity/Security/Proofs: build cold (dd1d98bef8cf)`, and Proofs' build
took 1,865 s of the run's 2,696 s. The fix I'd make: in `_audit`, give each audited package's `provers()` (and their path
dependencies) the treatment `inputs()` already gives their files, taking their warm dependencies and builds in and giving
them back when the audit that built them passed, as for an audited package (their compile-time code ran under that audit,
so its pass vouches for what comes back). Until then, naming the prover as well (`--package verity/Security --package
verity/Security/Proofs`) keeps its build, at the cost of auditing it too.

**`research fetch --all` fails on a live run whenever `tar` sees a file change.** With `--all`, `research.remote.fetch`
runs `cd RUN_DIR && tar -cf - .` over ssh, and GNU tar exits 1 when a file changes while it reads it, as a live run's
`resources.jsonl` does; `fetch` treats every nonzero exit as a failed fetch and records it as `last_fetch_error`, and the
CLI prints `research fetch: machine unreachable (tar: ./resources.jsonl: file changed as we read it)` with the machine
reachable. It failed so for r20261006-154756-10a4 repeatedly from about 15:54Z to 16:13Z, and for r20261006-163809-de0f at
16:39Z. A fetch without `--all` tars only `SMALL_FILES`, which hold no `stdout.log`, so while a run is live `--all` is the
only fetch that brings its log. I followed the runs with `research status --refresh`, retries, and small node runs that
tailed the logs (one of which, r20261006-161344-35ca, exited 2 because audit.py writes `build.log` only when the build
ends). The fix I'd make: let the remote command pass tar's exit 1, whose archive is still whole (a file's content moved
under it), e.g. `cd RUN_DIR && { tar -cf - . || [ $? -eq 1 ]; }`, and leave integrity to `_verify_and_manifest`, which
already hashes every remote file after taking the machine's clock and, on any mismatch with the local copy, writes
`preserve_error` and neither `preserved.json` nor `.fetched`. A live run's fetch would then update the local copy without
being marked preserved. Leaving the append-only telemetry out of the tar while the run is live would also do, at the cost
of losing it from a live fetch.
