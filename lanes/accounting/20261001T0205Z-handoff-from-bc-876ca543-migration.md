---
cursor:
  subagentId: "bc-876ca543-9636-59e7-ad99-0052e8cf3702"
id: 20261001T0205Z-handoff-from-bc-876ca543-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: price twins (bc-876ca543)
---

# Migration handoff from bc-876ca543 (price twins): four staged Lean sets, nothing in flight, nothing VM-only left

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. Written 7:05 PM PDT, and updated 7:10 PM PDT from
bc-824e54a2's handoff: M2a is merged; the FP4 grant is in; the FP4 count corrected.

**The lane.** Lean price twins for PoUW γ. Every published γ cites a Lean instance at both FP32 prices (issue-bound FADD 8.00
and in-loop `1047/125` = 8.376), and the larger is published. All of it is staged in the **old** store,
`/cursor/stores/bc-b729c175-…/internal/pouw/price-twins-lean/`. Start with its `README.md`.

## 1. Branches and PRs

- **None.** I own no verity branch or PR. All my work is store staging, and it reaches the Lean store only through bc-3cdbf3c1's
  merges.

## 2. Runs and jobs in flight

- **None.** No research run, no fill job and nothing on node 2. Every build ran on my VM's CPU and has finished.
- **My only standing thing** is a 30-min wake timer that reads this lane for orders. It stops with my turn.

## 3. Half-done state, and where it is now

All of it is in the old store and synced (sha256-checked). Nothing of mine is VM-only any more.

| Item | Path under `internal/pouw/price-twins-lean/` | State |
| --- | --- | --- |
| FP8 in-loop twins, FP8 chain-only, v2's exact chain cap | `README.md`, `Pouw/PearlC/` (14 files), `proposed-pins.json` (`0e330c31…`, 182 pins) | **merged in M2a** (636 pins in the store, `art:0b6c342a…`; bc-824e54a2) |
| M2a verify aids | `saltdead-readers.txt` (150 of 182), `proposed-pins-store-print.json` | used or superseded by the merge |
| v2-hot twins (M2b) | `v2-hot/` (132 pins, `v2-hot-pins.json` `c11eafaa…`), plus `v2-hot-pins-store-print.json` | GO; held on fix (2) and the grant |
| FP4 delta (Pearl-C4 v1 and v2 on `lut256`) | `fp4-delta/` (59 pins, **FP4 v2's 26 included**), with `rebase_on_fix.sh` and `fix-rehearsal.diff` (NVFP4 only) | GO; `tt-out/fp4-sm120` granted at C (widths ≥ 4,096, 6:36 PM PDT); merges with the fix (M5) |
| v1-hot | `v1-hot/` (100 pins) | GO; parked on Daniel |
| The private build's policy and recipe | `private-build/`: `lean-audit.json` (853 pins), the aggregator, a sha256 manifest of all 234 `.lean` files, the toolchain, `compose-check-v2hot.lean` and `sync.sh` | preserved 7:03 PM PDT |
| The uncited-figures list | `uncited.md` | last updated 30 Sep 7:06 AM PDT (14:06Z); owners noted |

The reviews are bc-22298e90's, beside these files: `statement-review*.md`, `statement-review-1350.md` and
`statement-review-v1-hot.md`.

## 4. The next step for each kept item

Against `20261001T0205Z-reply-from-old-accounting-full-backlog.md`:
- **"FP8 twins to the store" (M2a): done.** M2a merged them (636 pins, `art:0b6c342a…`). Nothing is left.
- **"v2-hot Lean (M2b)", drop if fix (2) fails.**
  - If fix (2) passes, M2b merges bc-b58c6093's GO'd 11 pins with my 132 unchanged. They are stated for the no-charge route,
    TT_OUT at γ₀ = 1/400.
  - None of the 132 reads `SaltDead`.
  - If it fails, nothing to do; v2-hot is parked.
- **"FP4 γ Lean set", keep.** It goes in the FP4 merge (M5): bc-ae19a858's fix (round 11, Lean GO 4:42 PM PDT) plus the 59.
  - **The 59 already include FP4 v2's 26** (`Fp4HotGamma`: two general theorems, eight twins and sixteen values). So M5 is
    the fix plus 59 records, not 59 plus 26.
  - Next: run `bash fp4-delta/rebase_on_fix.sh <private copy> <fixed ttout-fp4-staging>/Pouw <out>` on round 11. It builds,
    audits, replays and checks that all 59 records are unchanged. The audit prints the definitions the fix changed. The 16
    debit-reading pins need those to have bc-22298e90's review, which the 4:42 PM PDT GO may already cover.
  - I'm not starting it, per the migration order. It's a successor's or bc-3cdbf3c1's first job for this set.
  - The grant (C, widths ≥ 4,096) covers the twins' 8,192³ and 16,384³.
  - The published figures don't move: v1 0.71732% / 1.93807%, v2 0.71689% / 1.93528%.
- **"v1-hot", keep parked.** If Daniel adopts it, it merges with the rev lane's `devSm120v1hot` and its grant.
- **"v2-hot restaging" (the derived-charge route), moot.** Stop it.
- **What I'd stop:**
  - aligning `fix-rehearsal.diff` to the 15:18Z conditions, since it only tests that the records survive and the real
    definitions are bc-ae19a858's;
  - any work on the charged v2-hot form.

## 5. Traps

- **Two audit tools.**
  - The workspace's `tools/lean/audit.py` (newer, with `Facts.lean`) prints raw notation, `Eq d.G 0` and `(…).cast`.
  - The store's vendored `lean/tools/lean` (`VENDORED-FROM 6746f408`) prints `d.G = 0` and `↑(…)`.
  - Type hashes and assumptions agree, so a byte-equal record check fails across tools. Use the store's tool, or compare by
    type hash.
- **Reads are recorded per module.** A new definition in a module that pins read flags every one of those pins as changed. So
  new definitions go in new modules, as `DeviceChainCapKernel` and `DeviceHotRev1` do. Don't add the optional `G = 0` guard to
  `hotFoldDev`: it would need a re-review.
- **`lake build <module>` doesn't rebuild the aggregator.** Run the full `lake build` before `audit.py`, or the audit reports
  "matches no audited module".
- **The store's FUSE mount** returns EAGAIN or "Resource temporarily unavailable" under load. Copy with retries and a sha256 check
  (`private-build/sync.sh`).
- **Generated files:** `DeviceSm120KernelGamma.lean`, `v2-hot/…/HotGamma.lean` and `v1-hot/…/HotRev1Gamma.lean` come from
  `gen_kernel_gamma.py`, `gen_hot_gamma.py` and `gen_v1hot_gamma.py`. Regenerate them, never hand-edit.
- **Rounded against exact.** `Prices.sm120Loop` rounds `qa` (1.047 → 2), so its twins are upper bounds. The exact in-loop
  values are the kernel-form pins (`…LoopCast8…`, `ChainCapKernelGamma`). `labels` in `proposed-pins.json` links each rounded
  twin to its exact pin.
- **Which price is larger varies by row.**
  - Chain-only it is FADD 8.00 for v1 and v1-hot, but 8.376 for v2 and v2-hot.
  - Forming credited it is 8.376 for v1-hot, except at the as-written cast 32.06, where it's 8.00.
  - Check each row's larger price; don't assume.
- **v2-hot compared with v2, or v1-hot with v1:** say "equal within 0.001 points". The gaps are normalization effects
  (bc-22298e90).
- **The FP4 statements are generic over `sem`.** The fix changes what 16 of them mean without changing their records, so they
  need a statement review of the changed definitions, not just a byte check.
- **`research-notes` pushes** get a 403 with the VM's default GitHub credential. Use `https://notes@github.com/…` with the
  `RESEARCH_NOTES_TOKEN` helper (`kb/cloud-lane-setup.md`).
