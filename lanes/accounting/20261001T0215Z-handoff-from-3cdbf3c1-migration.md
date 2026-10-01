---
id: 20261001T0215Z-handoff-from-3cdbf3c1-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-3cdbf3c1 (PoUW Lean store merger, driven by bc-824e54a2); under note:20261001T0157Z-order-from-compute-accounting-all-migration-handoff
---

# Migration handoff: the PoUW Lean store merger, bc-3cdbf3c1 (7:15 PM PDT, 30 Sep)

I merge reviewed Lean pins into the store's package `lean/submissions/pouw/`, one snapshot-checked write-back per merge.
Today I merged A, B, C, M1, M2a and M4. **Nothing of mine is in flight or half-done, and nothing is lost if my VM stops.**
The store package is now at `7baf34fe070368059dbc790f6a8da8dd4c5acd69d2ecd859b32ccb150400a73a` with 636 pins.
The queue is M5 (the FP4 fix, granted and the next one to run), M3 (RowSeed, waiting on its replay audit) and M2b (v2-hot,
held for fix (2)). All times are Pacific (PDT).

## 1. Branches and PRs

- None. I own no Verity branch or PR. My only notes commit is this file.

## 2. Runs and jobs in flight

- None. No research runs, no node-2 jobs, no `lean-heavy` tickets (`/tmp/lean-heavy.q` is empty), and no `tile-merge-*` tmux
  sessions. All six merges are written back and preserved in the evidence store (`research data put --kind evidence/v1 --preserve`,
  then `research data verify`). Their art ids are below.

## 3. State: what landed, what's in the store, and what's only on my VM

**The merges** (each one: snapshot, exact prediction, build, `--update`, verify, a full `check.sh`, a dry-run then a `--strict`
write-back, a full re-read of the store package, evidence):

| merge | what | pins | package hash after | written back | evidence |
|---|---|---|---|---|---|
| A | FP4 tile pins | 326 → 362 | — | 2:53–7:15 AM (A to C) | `art:cdef20ba844b17da0f2d3445944db70c065fa42d0568116352e9377da47aba49` |
| B | FP8 tile pins | 362 → 390 | — | (with A) | `art:934de0ab471f83f91c36ee63e535e87cdd84b1e68b57b47ed6159777708f73f0` |
| C | FP4 bundle 2 | 390 → 393 | `e3f8681a…` | (with A) | `art:7c2bc76116cee070c2c2751ca2f636e00199a2a643af91e800100b1f7e5a1bc0` |
| M1 | rev2, DeviceSm120Gamma, the five-file SaltDead delta, FFMA docstrings | 393 → 454 | `8787a33b…` | 9:19 AM | `art:c482fce4b54572424a7653200b0d1d1b22523366f0843072af3e47204ea743dd` |
| M2a | 182 FP8 twins (in-loop, chain-only, v2's chain cap) | 454 → 636 | `8062c64d…` | 10:09 AM | `art:0b6c342ac19806550ae303188aa6c38c794153885940ad328562d1cb9820ca8c` |
| M4 | FP4 scale decode (F2's three files) | 636 | `7baf34fe…` | 11:37 AM | `art:2d6d7cb40e8672cf7771569b6b05fce3df2104c328009f9504d32e9af670b786` |

- **M4** moved only the read `Pouw.PearlC.Fp4` (digest `85a39a43…` → `760835bc…`; the `scaleDyadic` group
  `2ded72af37b87c4a` → `1eedbdf4eae9ff06`), for exactly the four TileBound pins. The policy is otherwise byte-identical.
- **M2a's records:** M2a ran under the print-only ruling, because I read the 9:17 AM ruling (option (b), store-print records)
  late. I checked it at about 7:05 PM: all 182 store records equal `internal/pouw/price-twins-lean/proposed-pins-store-print.json`
  exactly, their type hashes and assumptions equal the GO'd ones, and bc-876ca543's `saltdead-readers.txt` equals my list of 150
  readers. **The condition is met, and nothing needs redoing.**
- Backlog line 65 ("FP8 twins waiting on the M2a merge") is stale: done in M2a.

**In the store (mine):**

- `internal/pouw-fp8/store-merge-m1-m2a-plan.md`: the procedure, the dry run, and the results of M1, M2a and M4. **Start here.**
- `internal/pouw-fp8/store-merge-m2a-changelog.md`: M2a's 182 records, one by one.
- `internal/pouw-fp8/tile-pins-merge.md`: A to C.
- `internal/pouw/cheap-binding/ttout-lean-staging/rev2-tile-device-bundle/saltdead-delta/`: M1's five-file delta (`CHANGELOG.md`,
  `lean-audit.json`, `delta.diff`, `moved-reads.*`, logs). bc-22298e90's `statement-review.md` and `five-files.sha256` are there too.
- **`internal/pouw-fp8/tile-merge-tooling/`** (new tonight, copied from my VM; 25 files plus `sha256.txt`, each re-read and
  hash-checked). It holds:
  - `snap.py`, `treediff.py`, `predict.py`, `verify_exact.py`, `verify.py` and `m4_check.py` (the M4-style "only this read
    moves" predict and verify);
  - `pipeline2.sh`, which runs the build, `--update`, verify and `check.sh` under `lean-heavy`;
  - `writeback.py` (`--dry-run`, `--strict`);
  - `extract_records.py`, `compare_delta.py` and `apply_policy.py`;
  - `inbox_post.py` (appends to `coordinator-inbox.md` with a read-back) and `put_files.py` (store copies that refuse to
    overwrite);
  - `gate.sh`, and the per-merge drivers under `runs/M1`, `runs/M2a` and `runs/M4`.
  - Its `README.md` gives the order of the steps and the paths the scripts assume.

**Only on my VM, not copied:** the work trees `/home/ubuntu/tile-merge/{A,B,C,M1,M2a,M4}/` with their `.lake` caches. They can be
rebuilt from the store and the evidence, and no successor needs them.

## 4. The next step for each kept item, and what I'd stop

Every merge starts from the store as it is then: snapshot it again, and never reuse a prediction made on an older base.

- **M5, the FP4 fix (backlog lines 48 and 63; ready).** bc-22298e90 GO'd the Lean packet (4:42 PM), the node-2 replay passed
  (`art:9f429608…`), and the assessor granted `tt-out/fp4-sm120` at C at 6:36 PM, for widths of 4,096 and up.
  - **Inputs:**
    - bc-ae19a858's round 11 in `internal/pouw-fp8/ttout-fp4-staging/` (review in `basesplit-review/`);
    - fp4-delta's 59 records (`internal/pouw/price-twins-lean/fp4-delta/`);
    - FP4 v2's 26, per bc-824e54a2's handoff.
  - **First step:** get one frozen list of files and sha256s from the coordinator's successor, and compare it with the staging
    folders at freeze time.
  - **Expected change:** bc-ae19a858's post-M4 split measured 636 → 695 pins (+59), with 16 pins' reads moving. Predict FP4 v2's
    26 on top of that exactly, from their store-print records.
  - **Run** the M1/M4 procedure. `check.sh` draws about 5.7 GB; if the VM is short, use the node-2 one-shot (`run-node2.sh` in
    `internal/pouw-fp8/coordinator-vm-tooling/`).
  - **Statement-reviewer label:** it goes on the merge snapshot only if compute-accounting orders it (bc-22298e90's handoff).
  - **After the merge,** the coordinator's successor marks the FP4 rows granted on `docs/pouw/security-proofs.md`.
- **M3, RowSeed (lines 61–62; 28 pins in `internal/pouw-fp8/rowseed-staging/`).**
  - **Done:** bc-22298e90 GO'd all 28 at 6:43 PM (`red-team/statement-review-m3-rowseed.md`), after `FragDraw` was restaged as
    the named `Prop` `Pouw.PearlC.Assumptions.FragDraw` (Daniel's ruling). bc-5382063c reports that the build and `--update`
    pass on the post-M4 store.
  - **Waiting on:** bc-5382063c's replay audit (line 62, parked for memory; node 2 can run it).
  - **The merge:**
    - **Policy:** the merge adds an `assumptions` entry, so the policy is not byte-identical, and `m4_check.py`'s verify does
      not apply. Predict the new entry with `predict.py` and verify with `verify_exact.py`.
    - **Statement reviewer:** the merge handoff names bc-22298e90.
    - **Base:** the store as it is after M5, if M5 lands first.
- **M2b, v2-hot (lines 28–34 and 66; held).** If fix (2) fails, drop it. If fix (2) passes:
  1. bc-b58c6093 restages `NoAlignedExactRegionHot.lean` (the t₀ = 0 docstring), which changes its hash again.
  2. bc-22298e90's successor reviews it.
  3. M2b needs the grant naming both prices, `publicConst 64`, t₀ and W*(w).
  4. Get a pinned list of files and hashes, then merge.
  - **The set:** bc-b58c6093's GO'd files in `internal/pouw/cheap-binding/ttout-lean-staging/v2-hot/Pouw/PearlC/` and
    bc-876ca543's v2-hot twins (`v2-hot/v2-hot-pins-store-print.json`). Not bc-7a7109a0's 12-pin set.
  - **The latest hashes I saw:**
    - `TTOutV2HotCharged` `c3d15402…`, `V2HotCharged` `27834b2f…`, `NoAlignedExactRegionHot` `5805f44e…`, `DeviceV2Hot` `39a331fd…`;
    - `AccumHot` `ef08a3ca`, `NoAlignedExactRegionHotBridge` `2d740a8b`, `TTOutV2Hot` `f7bf8ed8`, `V2HotAccounting` `3c0d08ab`,
      `V2HotChainOnly` `717eca9b`, `V2HotHeadline` `c306782e`.
  - The block tables are provisional, and their re-pin is a separate delta.
- **I'd stop:** nothing of mine is running. Don't prepare M2b before fix (2) is decided: its inputs kept changing
  today (`NoAlignedExactRegionHot` alone had four hashes).

## 5. Traps

- **The store's FUSE mount** returns EAGAIN, EIO, "Cannot stat" and empty listings under load.
  - `os.path.exists` turns an EIO into False.
  - Read through a retry loop (`read_all` in the scripts). Write to a temp file, fsync, read it back, `os.replace`, and read
    back again.
  - A write-back of a few hundred files can take minutes.
  - Re-read the whole package against the work tree afterwards, and trust only sha256s.
- **`writeback.py --strict`** compares every store file with the snapshot manifest before it writes. If anything moved since
  the snapshot, it refuses. Snapshot again and redo the merge; never force it.
- **`audit.py --update` rewrites the policy** (pins and reads), so its output proves nothing on its own.
  - Verify the result against the independent prediction (`predict.py`, or `m4_check.py predict`). It must match exactly:
    the policy, the pin set, the records, and which reads moved.
  - The `assumptions` field lists only closed `Prop`s. A named assumption applied to variables (`FragDraw`) shows only in the
    signature and under `reads`.
- **Printed signatures depend on context.** For twin sets, take the records from the staging `*-store-print.json` (option (b),
  the 9:17 AM ruling). Check their `type_hash` and assumptions against the GO'd records; the type hash is the statement.
- **`Gamma.lean`:** only `593e4e43…` is mergeable. `65bedd41…` (rev1) and `10b28d4a…` (rev2's pre-delta copy) carry the ±44
  witness (the 9:15 AM ruling). Require-equal it in every merge.
- **Staged hashes change between review and merge.** Freeze the inputs into the work tree, sha256 them, and compare with the GO'd
  hashes at freeze time, not with an earlier note.
- **`lean-heavy`** has a 5,500 MB floor. `check.sh` draws about 5.6–5.7 GB and takes 34–35 min. `tile-merge-*` labels run at
  priority 1.
  - Don't touch `/tmp/lean-heavy.hold`.
  - Never run `lake` or `check.sh` in the store; build only in a work copy.
- **The scripts assume my VM's layout:**
  - `W=/home/ubuntu/tile-merge` and the store mount path, hard-coded;
  - `audit.py` imported from `$W/A/lean/tools/lean/`. Copy the store's `lean/tools/lean/audit.py` there (sha256 `0f4d1f9b…`);
  - `/home/ubuntu/lean-heavy.sh`, whose copy is in `internal/pouw-fp8/coordinator-vm-tooling/`.
  - This VM has no `rsync` or `cpio`; the work copy uses a `cp` loop, with Mathlib hard-linked.
- **One store writer at a time.** Post an inbox line when `check.sh` starts and ends, and when a write-back lands (`inbox_post.py`
  re-reads the inbox and retries if it changed under it).
- **Evidence:** `research data put --kind evidence/v1 --preserve` from a checkout whose `research` CLI is current. Then run
  `research data verify` on the art id.

I'll answer my replacement's questions in this lane until @old-accounting stops me.
