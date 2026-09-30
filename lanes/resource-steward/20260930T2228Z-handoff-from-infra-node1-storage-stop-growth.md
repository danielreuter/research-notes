---
id: 20260930T2228Z-handoff-from-infra-node1-storage-stop-growth
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# resource-steward: stop node 1's storage growth, which is at 76% and about 190 GB/h. Diagnosis is done; prune `research/src` now within policy, own the owner asks, write the storage plan by 5 PM PDT

Daniel wants growth stopped, not watched.

**Diagnosis** (infra, 3:23 PM PDT): `/workspace` is at 3,790 of 5,016 GB.
- `jobs/runs`: 221 GB, up 72 GB, all proofs' backend-sweep. `r20260930-210718-2f89` is a 59 GB failed run; `-220453-b99a` and `-9cce` and
  `-220551-3af1` hold 63 GB of `circuit.txt` outputs.
- `jobs/flock-sweep2/stage-cache`: 156 GB, up 64 GB. **Duplicate full copies** of the same `circuit.txt` files as `runs/*/out/classes/`
  (different inodes, equal sizes). Proofs.
- `jobs/cov`: 131 GB, up 55 GB. Replay bundles: `cov-g142` TinyLlama B8 is 45 GB; Phi-3 B8 `.partial` bundles are 11–60 GB. Circuits.
- `research/src`: 160 GB of shipped source trees. Regenerable.
- `jobs/probe-jit`: 76 GB, flat.

**Projection:** 80% (4,013 GB) at about 4:35 PM PDT, and 85% (4,264 GB) at about 5:55 PM PDT.

**Owner asks are on Slack** (3:25 PM PDT): @proofs (dedupe the stage-cache, the failed run, output digests) and @circuits (delete
bundles after replay, clean up `.partial` bundles, cap unreplayed bytes). Follow up on both threads, and act on each yes.

**Do now, within your policy:** prune `/workspace/research/src/<sha>` trees older than 24 h that no running process references (check
`/proc/*/cwd` and `cmdline` for the sha). Log it. That is likely 100 GB or more back.

**The storage plan by 5 PM PDT:** see my resume message, or the brief in `note:20260930T2228Z` (this note), items: needs, constraints,
budgets per lane with `--disk-gb` at submit, retention classes, offload (faster R2 custody or node 2 overflow), what you enforce
automatically, and Daniel's yes/no items. Write it to `lanes/resource-steward/20260930T2359Z-draft-storage-plan.md` if you can't reach
the Project store, and infra copies it to `docs/storage-plan.md`.

## Update, 3:34 PM PDT (infra)

- **Node 1:** 78% (3,875 GB). The new top writer is `jobs/probe-jit/cfgtp2-deferred-phi3b8g` (102 GB since 3:17 PM PDT), circuits' #599/#598
  acceptance probe.
- **At 4:00 PM PDT, delete** `jobs/probe-jit/cfgtp2-deferred-phi3b8m` (61 GB) and `-phi3b8f` (12 GB) unless circuits or the TP2 lane
  (bc-35ab914e) says keep in thread `1790807092.688879`. Circuits' rule is to keep the newest complete Phi-3 B8 and delete the rest. Check
  first that they have no open files.
- **Delete `cov-g142`'s TinyLlama B8 bundle** (45 GB) once it has no open files; circuits said yes. A replay (pid 2234181) was reading it at
  3:28 PM PDT.
- **The stage-cache prune freed 0:** every entry was touched within 30 min, and the old research coordinator's hardlink dedupe is running
  (`/workspace/jobs/sweep2-feed/dedupe.log`).
- **At 80%, pause packing** (`PACK_COMMITS=0`) and ask kueue-fold and circuits to hold new B8 Commits. circuits has already held them.

## Rules from the owners, 3:30–3:37 PM PDT (they supersede the above where they differ)

- **Stage-cache (proofs and the old research coordinator):** do NOT prune by age alone. Prune an entry only when its `circuit.txt` has
  **link count 1** (no run still references it) **and** it is older than 30 min. Keep `r20260930-210718-2f89`. The dedupe loop (tmux
  `sweep2-dedupe-loop`, every 5 min) had freed 112 GiB by 3:37 PM PDT, with its first pass ending about 4:00 PM PDT.
- **Replay bundles (circuits):** deletion after a recorded replay is already in the template: `config-run.yaml` line 351 deletes
  `replay_bundle_p*` when the replay's rc is 0 and `config_record.json` is non-empty.
  - **Confirm** `cov-g142`'s 48 GB bundle disappears when its replay ends.
  - **Add** `rm -rf $SWEEP_DIR/$ROW/commit/replay_bundle_p*` to the GPU task on any non-zero rc, via kueue-fold on `infra/nebius`,
    commit first. A failed replay keeps its bundle for up to 6 h for triage, then the host sweep deletes it (today it waits 48 h).
  - The only bundles now are `cov-g142` (48 GB), `cov-n086` (8 GB) and `cov-n093` (5 GB).
- **The 300 GB rule:** apply circuits' hold (no new B8+ Commit while more than 300 GB waits for replay on the node) to MPS packing
  too. Tell mps-pack (bc-1c69147a) in `lanes/kueue-fold/`.
