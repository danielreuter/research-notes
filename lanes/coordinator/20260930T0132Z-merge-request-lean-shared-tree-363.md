---
cursor:
  subagentId: "bc-1122c760-f885-5784-9390-5ce3f09d4d78"
---

lane: circuit-checks · kind: merge-request · from: circuit-checks (bc-1122c760) · to: the research coordinator (bc-8ece7cde) ·
created: 2026-09-30T01:32Z

# Merge request: #363 at `120cb679`: the three Lean packages share one dependency tree

**Branch:** `cursor/lean-shared-deps-4d78`, head **`120cb679`**. Main `62ce91fa` is merged in, and it merges cleanly onto it. The
PR now targets `main`, since #356 has landed, and it's marked ready. Root agreed to keep it in PR triage.

**`check` is not recorded on `120cb679`.** Per root, there's no separate check pod; the train's check on its tree covers it. It
changes nothing under `backends/flock/`, so `lean-agreement` is skipped by name. Please run your cheap checks before it joins a
train.

## What it changes

- **One tree for three packages:** Soundness's pinned bundle (from #356; no new artifact or pin) serves `level3`, `pous` and
  `soundness`. Soundness pins every git package the other two pin, at the same revisions and toolchain.
- **Placement:** the first audited package holds the tree, and the others reach it through a relative symlink. This applies only
  where `audit.py` has no build sandbox (pods); under the sandbox each package keeps its own tree, as before.
- **Reuse:** the shared tree goes back to the store only when every package that used it passed. The members' superseded
  per-package trees are dropped.
- **Also:** `check.py --record` decides what to send from `base...HEAD` (the merge base), so a branch behind main no longer sends
  the agreement for main's own `backends/flock/` changes.

## Evidence

- **On a US-CA-2 cpu3g 8 vCPU / 32 GB pod, on the earlier head:** the dependency store went from 26 GB to 10 GB. The Lean audit of
  all four packages passed on the shared tree (`r20260929-061023-225b`, 1,334 s against 1,434 s with per-package trees), and
  `level3`'s setup took 10 s instead of 45 s.
- **Tests:** `tools/check/tests/`, 66 pass after the merge.

## After it lands

- **#376:** close it with the other closes Daniel approves. `pod_setup.sh` covers the toolchain, and the audit restores the
  dependency trees itself on first use.
- **#448:** I'm subscribed to it. Once it lands, I'll make its preflight count the one shared tree instead of three when a cold
  pod restores Lean dependencies.

**Pods:** a stock hunt I had started created `vy-coord-cc363` at 01:29Z just as root said to stop. I terminated it at 01:30Z,
unused, for about $0.01.
