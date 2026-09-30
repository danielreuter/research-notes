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
