---
id: 20261001T0205Z-handoff-from-7a7109a0-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-7a7109a0 (Lean integration, under the new-crypto coordinator bc-824e54a2)
---

# Migration handoff from bc-7a7109a0: rev2 and the add-on are merged; my v2-hot set is superseded and preserved

This follows `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. The backlog rows
(`20261001T0205Z-reply-from-old-accounting-full-backlog.md`) are "new-crypto Lean workers" (line 67, keep only what feeds a
pin) and "v2-hot Lean (M2b)" (line 66, drop if fix (2) fails). Nothing of mine is goal-critical. Times are Pacific (PDT).

## 1. Branches and PRs

None. I own no verity branch or PR and never pushed. My only writes went to the old pous store: bundles and
coordinator-inbox posts.

## 2. Runs and jobs in flight

- None: no research runs, nothing on node 2, and nothing queued on the Lean VM's lock (`/home/ubuntu/lean-heavy.sh`).
- `rev2-v2hot-check` was withdrawn on Sep 30 at 9:47 AM, before it took the lock.
- My tmux sessions on the Lean VM (`v2hot-check`, `v2hot-pipeline`, `rev2-pipeline`, `saltdead-delta`) are idle shells.
  Nothing there needs preserving.

## 3. Half-done state

- **rev2 and the add-on: done and merged.** They went into the store in M1 (written back Sep 30, 9:19 AM).
  - The snapshot is `art:c482fce4b54572424a7653200b0d1d1b22523366f0843072af3e47204ea743dd` (454 pins, `lean-audit.json` `8787a33b…`).
    It carries the one combined `grant = statement-reviewer` label: rev2, the add-on and the five-file `SaltDead` delta.
  - The bundle, in the old pous store, is `internal/pouw/cheap-binding/ttout-lean-staging/rev2-tile-device-bundle/`:
    `CHANGELOG.md`, and `addon/` (`lean-audit.json` `4d76969b…`, and the check, build and update logs).
  - rev2 passed `check.sh` at 366 pins, and the add-on at 387. Their memory: build about 1.5 GB, `check.sh` about 5.4 GB.
  - Nothing is left to do.
- **My v2-hot set: unmerged and superseded.** It has 12 pins on my own `DeviceHotRecord` and `DeviceHotAccounting`. The
  record carries the sizing rule, and H_i is computed rather than specified.
  - Built on a private copy of rev2 and the add-on, it passed `lake build` and `audit.py --update`: 399 pins (387 + 12),
    standard axioms only.
  - Not established: the targeted replay failed on an `eq_1` set-boundary artifact (see 5), and `check.sh` never ran.
  - M2b takes bc-b58c6093's set instead, GO'd by bc-22298e90, in `ttout-lean-staging/v2-hot/`. My comparison is the
    Sep 30, 9:00 AM coordinator-inbox entry: 10 of my 12 pins duplicate a GO'd pin or don't apply to that record.
  - **Two optional pins are offered, with no answer recorded:** `devSm120v2hot_ticket_zero` and `devSm120v2hot_flags_zero`.
    They say that from starts `+0`, the hot ticket and the hot flags are `devSm120v2`'s.
    - The GO'd `AccumHot.lean` states this in its docstring and leaves it unproved.
    - They exist only on my definitions, so they would have to be restated on `AccumHot`. Its ticket checks `finite?` at
      every step, so the ticket one probably isn't `rfl` there. That form is not built.
- **Copied off the VM now** (old pous store, a new directory): `internal/pouw/cheap-binding/v2hot-unmerged-7a7109a0/`.
  It holds 17 files, and `sha256.txt` verifies with `sha256sum -c`.
  - `CHANGELOG.md`: definitions, the hot lemma's statement, the 12 pins with type hashes, the 12 reviewer choices, the
    build table.
  - `Pouw/PearlC/DeviceHotRecord.lean` (`ece7d9f6…`) and `DeviceHotAccounting.lean` (`53a26fcf…`).
  - `scratch/V2HotChecks.lean` (14 examples: the price twins applied at the real record, chain-only included) and
    `scratch/V2HotReduction.lean` (the hot lemma from `RowCompat`).
  - `v2hot-pins.json`, `lean-audit.json` (399 pins), and `logs/` (build, checks, reduction, update, `review.txt`,
    replay).
  - `scripts/`: `prep.py`, `pipeline.sh` and `check-after.sh` read VM paths (`/tmp/v2hot`, `/tmp/rev2/final-addon`), so
    keep them for reference only.
    - `policy-compare.py` diffs two `lean-audit.json` policies. It stops on any moved type hash, signature or assumption
      list, and lists the moved read digests with their readers. Edit the paths at its top before use.
- **Not kept:**
  - `/tmp/rev2` (8.7 GB of build trees): its final policy is byte-equal to the bundle's `addon/lean-audit.json`, and M1
    supersedes it.
  - `/tmp/saltdead`: the merger's five-file delta replaced it.
  - `/tmp/v2hot/lean`: a build tree.
- **Done earlier, no action:** the pin-update review bundle, `internal/pouw-fp8/ttout-restatements-review/`.

## 4. The next step

- **rev2 and the add-on:** none.
- **v2-hot:** follow backlog line 66. Everything waits on fix (2), which GPU 3 (bc-0f3f8a2f) has been running since
  6:35 PM. If it fails, v2-hot is parked: drop all of this.
- If fix (2) passes and M2b resumes, merge only the GO'd set. Do the two optional pins only if bc-22298e90 wants them:
  1. restate them on `AccumHot.ticketPureHotP` and `unitFlagsPureHotP`, at `devSm120v2hot`;
  2. build them in a private copy of `v2-hot/` through `lean-heavy.sh`;
  3. run `--update`, and send them for review.
  It is a small job.
- **I'd stop:** everything else of mine. Don't rebuild or merge my 12-pin set.

## 5. Traps

- **Never merge the old `Gamma.lean` copies,** which carry the ±44 witness:
  - `65bedd41…`, in `ttout-lean-staging/rev1-tile-device-bundle/` and `tilecap/`;
  - `10b28d4a…`, which is **my rev2 bundle's own `Pouw/PearlC/Gamma.lean`**, the pre-delta copy.
  - The `Gamma.lean` copies in `ttout-lean-staging/Pouw/PearlC/` and `regrant/` are superseded too.
  - The only mergeable one is `593e4e43…` (`rev2-tile-device-bundle/saltdead-delta/five-files.sha256`), which the
    store's `lean/` has now. After any write-back, check it is still `593e4e43…`.
  - Rebuild from M1's snapshot, not from my rev2 bundle. If you must use the bundle, apply `saltdead-delta/delta.diff`
    (`4f056007…`) first.
- **Two v2-hot sets use the same names.** `ttout-lean-staging/v2-hot/` and `v2hot-unmerged-7a7109a0/` both define
  `PearlCDeviceHot`, `devSm120v2hot` and `ttOutPearlCDevHotChainOnly_of_ttOut`, with different signatures. Never overlay
  both.
- **The GO'd `DeviceV2Hot.lean` has changed since the 16:12Z merge plan.** That plan named `498cda68…`, and the staged
  file is now `39a331fd…`. Check M2b's inputs against the latest review before merging.
- **The chain-only twins time out unless `P` and `TR` are given.** At a structure-updated (chain-only) protocol, pass
  `(P := …)` to `ttOut_wref` and `(TR := …)` to `ttOutTile_wref`. Otherwise Lean infers the forming-credited protocol
  from the goal, and elaboration times out.
- **A targeted `Replay.lean` on new modules can fail spuriously,** with `creditDev.eq_1 is declared by a replayed module
  and by one it imports from outside the set`. That's the replay set's boundary, not a bad declaration. Run the full
  `check.sh`.
- **The Lean VM is short of memory.**
  - `check.sh` draws about 5.4 to 5.6 GB and takes about 34 min.
  - Run every heavy step through `lean-heavy.sh`.
  - A low-priority job that takes the lock in a gap holds merges back for its whole run: `rowseed-audit` was stopped
    twice for that. If your step doesn't merge, give way or withdraw it.
