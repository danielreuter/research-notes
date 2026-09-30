---
id: 20260930T2305Z-handoff-from-infra-storage-plan-tonight-cluster-build
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: add `--disk-gb` and `--retain CLASS` to `research run --queue`, and check disk at admission (storage plan items 2 and 5)

From `docs/storage-plan.md` (4:05 PM PDT). This comes after the node-2 switch, but tonight if possible:
- **`--disk-gb N`:** a per-kind default (20 GB for kinds with no history). Admit a job only if the node's free space, minus outstanding
  requests, minus a 10% reserve, is at least N. Warn tonight; fail closed at T4. The ledger records requested and used bytes.
- **`--retain evidence|intermediate|cache|pinned`:** with a per-kind default, recorded on each declared output. The resource-steward
  enforces it.
- **Run dirs by T4:** the executor creates each job's run dir at admission, so later it can get a project quota (plan item 3, pending
  Daniel's downtime decision).
