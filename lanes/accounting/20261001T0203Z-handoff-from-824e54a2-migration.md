---
id: 20261001T0203Z-handoff-from-824e54a2-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: PoUW FP8/FP4 Lean coordinator (bc-824e54a2)
---

# Migration handoff: bc-824e54a2, the PoUW FP8/FP4 Lean coordinator (Lean proofs of PoUW's γ ≤ 1%, and the Lean store merges)

To `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. All paths are in the Cursor store `bc-b729c175…` unless named otherwise.

## 1. Branches and PRs

- **None in Verity's git.** This lane works in the Cursor store's Lean package (`lean/submissions/pouw/`), and merges by checked write-back with `research data put` evidence. It owns no Verity branch or PR.
- **The store package:** **636 pins**, `lean-audit.json` `8062c64d…`/`7baf34fe…` (after M4), and `Pouw/PearlC/Gamma.lean` `593e4e43…`.
- **Merged today:**
  - the tile merges (FP4-tile, bundle 2, FP8-tile, to 393; `art:cdef20ba…`, `art:934de0ab…`, `art:7c2bc761…`);
  - **M1** (rev2, its add-on, the five-file `SaltDead` delta and the FFMA docstrings; 454 pins; `art:c482fce4…`; the combined grant label is recorded, clearing the F2 caveat);
  - **M2a** (the FP8 in-loop twins, FP8 chain-only and v2's exact chain cap; 182 records; 636; `art:0b6c342a…`);
  - **M4** (the FP4 scale decode, `scaleDyadic` reading the low 7 bits; `art:2d6d7cb4…`).

## 2. Runs and jobs in flight

- **`ovlabels-watch`** (tmux on this VM, `/home/ubuntu/ovlabels-watch.sh`; a copy is in `internal/pouw-fp8/coordinator-vm-tooling/`). This is **goal (3) step 3** (panel chain): it pushes bc-2aa33ad8's local-only panel labels from `internal/pouw/panel/ov-labels/labels/` to the evidence store's remote, confirmed by a second `--push-only` that pushes 0.
  - Window 7's rows are done (6:43 PM PDT; 30 files; `pearl-c-sm120/v1-h2/decode/109/e2e-llama31-8b-vllm-m32` is 3.4024×).
  - Window 8's rows are pending. The watcher runs until about 5:55 AM PDT.
  - **I keep it running until window 8's rows are pushed,** or until my replacement runs the same script on a VM that has the remote. Custody: labels sync to the remote, and nothing more is needed.
- **No research runs or node-2 jobs are in flight.** The FP4 D-NF replay passed on node 2 and is preserved (`art:9f429608…`), as is the a67 canary (`art:2ea3b223…`). The Lean lock queue is empty.
- **Workers** (driven by me; each writes its own handoff): bc-3cdbf3c1 (store merger), bc-ae19a858 (FP4 staging), bc-5a715b19 (F2, the scale decode), bc-7a7109a0 (rev2) and bc-5382063c (RowSeed, waiting for the skip-class re-GO).

## 3. Half-done state

- **The FP4 fix, ready to merge** (`internal/pouw-fp8/ttout-fp4-staging/`, bc-ae19a858; round 11): D-NF in `RowAdmit4`/`RowRules4`/`RowRules4At`, and `c_L` as #556's table.
  - The Lean packet is GO (bc-22298e90, 4:42 PM PDT), and the kernel replay passed (`art:9f429608…`). **The assessor granted `tt-out/fp4-sm120` at C at 6:36 PM PDT, for widths of 4,096 and up.**
  - It merges with fp4-delta's 59 records (`internal/pouw/price-twins-lean/fp4-delta/`) and FP4 v2's 26.
- **M3, RowSeed** (`internal/pouw-fp8/rowseed-staging/`, bc-5382063c; 28 pins, 27 GO): `FragDraw` is now the named `Prop` `Pouw.PearlC.Assumptions.FragDraw` (Daniel's ruling). The skip-class pin is awaiting re-GO, and the replay audit is parked for memory. `-h3` stays open until M3 is reviewed.
- **M2b, v2-hot** (`internal/pouw/cheap-binding/ttout-lean-staging/v2-hot/`, bc-b58c6093; pinned hashes: `TTOutV2HotCharged` `c3d15402…`, `NoAlignedExactRegionHot` `5805f44e…`, `V2HotCharged` `27834b2f…`, plus the GO'd rest), plus bc-876ca543's v2-hot twins. Held for fix (2) and its grant.
- **The merge plan and tooling:** `internal/pouw-fp8/store-merge-m1-m2a-plan.md`, and bc-3cdbf3c1's scripts, being copied to `internal/pouw-fp8/tile-merge-tooling/`.
- **The coordinator tooling, copied from this VM:** `internal/pouw-fp8/coordinator-vm-tooling/` (13 files, `sha256.txt`). It holds:
  - `lean-heavy.sh`: one heavy Lean step at a time, by label priority, with a hold file and a watchdog;
  - the label, canary and replay watchers;
  - `run-node2.sh` and `compare_node2.py`, the node-2 one-shot;
  - logs, including the measured memory peaks.
- **The docs:**
  - `docs/pouw/security-proofs.md` (the proofs page; mine);
  - `internal/pouw-fp8/pearl-c-lean-split.md` (the split and merge queue);
  - `docs/pouw/research-plan.md` (shared);
  - `internal/pouw/coordinator-inbox.md` (shared).
- **VM-only and not copied, because recoverable:** private Lean work copies (`/tmp/rev2`, `/tmp/v2hot`, `/home/ubuntu/pearlc-fp4/`, `/home/ubuntu/tile-merge/*/work`, `/tmp/p1work`) and their `.lake` caches. They can be rebuilt from the store and the staging folders.

## 4. The next step for each kept item

- **Window 8's labels (goal 3):** run `ovlabels-watch.sh` on a VM with the evidence-store remote. When the rows land, post the step-3 line (count, plus the confirming push of 0).
- **The FP4 merge (M5):** fix plus fp4-delta (59) plus FP4 v2 (26), through the merger's pipeline. A full `check.sh` draws about 5.7 GB, so if the VM is short, use a node-2 one-shot with inputs staged in the store. After the merge, mark the FP4 rows granted at C (widths 4,096 and up) on `security-proofs.md`.
- **M3:** bc-22298e90's re-GO of the skip-class pin, then the replay audit (node 2 if needed), then the merge.
- **M2b:** wait for fix (2) and the grant naming both prices, `publicConst 64`, `t₀` and W*(w). Drop it if fix (2) fails.
- **The scale-decode follow-up:** bump the generator's pin to #534's merge commit, and drop its override.
- **Stale backlog lines:** "D-NF replay evidence waiting on bc-824e54a2" is done (`art:9f429608…`), and "FP8 twins waiting on the M2a merge" is done (M2a, 17:09Z).
- **I'd stop:** the hourly overnight RunPod sweep (no `vy-pous*` pods all evening; pous spend $0 against the $200 cap).

## 5. Traps

- **The store's FUSE mount** fails transiently: EAGAIN, "Cannot stat", empty listings. Copy with retries, read every file twice, and check sha256 before trusting a copy or a count.
- **Lean VM memory:** the host balloon often holds 8 GiB, leaving about 6 GB, and a full check or replay draws 5.5–5.7 GB. Use `lean-heavy.sh`'s gate. Lower-priority jobs slip into the gaps between a pipeline's phases, so use a sentinel (`m1-bridge.sh`) or the hold file. Node 2 has no evidence-store remote, so stage its inputs in the store and preserve its outputs from here.
- **research-notes:**
  - The checkout is sparse; use `git show origin/main:…` to read.
  - Push with `RESEARCH_NOTES_TOKEN` via `~/.research/askpass.sh`, to the explicit URL `https://x-access-token@github.com/…`. The global `insteadOf` rewrites `https://github.com/` to a read-only token.
  - The Verity broker covers `danielreuter/verity` only.
- **`Gamma.lean`:** only `593e4e43…` is mergeable. Older copies, `65bedd41…` (rev1, tilecap) and `10b28d4a…` (rev2's pre-delta copy), carry the ±44 witness.
- **Printed signatures** differ between audit-tool versions. Use the store-print pins, and test identity by type hash plus assumptions.
- **`exit.txt`** holds `exit=N <timestamp>`. Parse `exit=N`, not digits.
- **The panel labels** exist only on bc-2aa33ad8's VM until pushed, and only VMs with the remote can push them.
