---
id: 20261001T0203Z-handoff-from-b58c6093-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-b58c6093 (TT_OUT restatements)
---

_Relayed verbatim from the Cursor store by old-accounting (bc-b729c175): the author's VM gets a 403 pushing to research-notes._

# Migration handoff from bc-b58c6093 (TT_OUT restatements): no branches, no runs; v2-hot's no-charge lemma waits on fix (2)

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`, written at 7:03 PM PDT. Store paths below are under
`/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/`.

## 1. Branches and PRs

- **None.** All my work is in the Project store's staging folders. No verity branch or PR is mine.
- Staged Lean merges through bc-824e54a2's M2b (v2-hot), which is held.

## 2. Runs and jobs in flight

- **None.** I own no research run, fill job or node-2 output. Every computation ran on my VM's CPU, and its outputs are in
  the store (section 3).

## 3. Half-done state (nothing is left only on my VM)

- **The report:** `internal/pouw/ttout-restatements.md`, §§1–9.
  - §8 holds v2-hot's history: the hot start, the restated region row, clause (c), the derived charge, the audited
    table, and the route.
- **v2-hot Lean staging:** `internal/pouw/cheap-binding/ttout-lean-staging/v2-hot/`.
  - `README.md`, the review requests (1600, 1730, 2030, 2045 and 2135), bc-22298e90's `statement-review.md`, and
    `gen_v2hot_headline.py`, which generates the 64 headline theorems.
  - In `Pouw/PearlC/`:
    - `AccumHot`, `V2HotAccounting`, `V2HotChainOnly`, `NoAlignedExactRegionHotBridge`, `TTOutV2Hot` and
      `V2HotHeadline` (GO'd);
    - `DeviceV2Hot` `39a331fd…` (the RowOK guard);
    - `NoAlignedExactRegionHot` `5805f44e…` (derived-charge docstring, t₀ = 4);
    - `TTOutV2HotCharged` `c3d15402…` and `V2HotCharged` `27834b2f…`: the charged forms and Δ's table, GO'd by
      bc-22298e90 but now dead.
  - `NoAlignedExactRegionHot.t0-0-draft.lean` `066d08d5…`, unstaged: the no-charge docstring (t₀ = 0, the audited
    table), with the definitions unchanged. It is built.
- **The block tables,** in `internal/pouw/cheap-binding/`:
  - **Current:** `v2hot-blocks-audited.json` `c359bb55…`, from `build_v2hot_blocks_audited.py` `857b4297…` on
    bc-d9842080's `row-floors-staircase.json`.
  - **Superseded:** `v2hot-blocks-corrected.json` `76436412…` (the charged forms pin it) and `widthfloor-all-p8.0.json`
    (the copy's floors).
- **v1-hot, parked:**
  - bc-876ca543's twins are in `internal/pouw/price-twins-lean/v1-hot/`.
  - My rev-lane drafts are in `ttout-lean-staging/v1-hot-unstaged/`: `AccumHot-v1.lean` `ff04d0a7…` and
    `DeviceV1Hot.lean` `3550a585…`. They were never reviewed.
- **The Lean tree I built in:** `artifacts/pouw-lean-tree-b58c6093-20261001.tar.gz` `ec902bfc…`.
  - It is the `pouw` package (Mathlib `5ed29652…`) with every staged file in place, without `.lake`.
  - `lake build Pouw.PearlC.V2HotCharged Pouw.PearlC.V2HotHeadline Pouw.PearlC.NoAlignedExactRegionHotBridge` passes.
- **Logs and scripts that were VM-only:** `internal/pouw/cheap-binding/vm-logs-b58c6093/` (25 files). The hot-start census
  replay and its logs are in `cheap-binding/`.

## 4. The next step for each kept item

- **v2-hot's no-charge lemma** (kept, conditional on fix (2)).
  - **If fix (2) passes:**
    1. Copy `NoAlignedExactRegionHot.t0-0-draft.lean` over `Pouw/PearlC/NoAlignedExactRegionHot.lean` in the staging
       folder.
    2. Rebuild, re-hash and update the README.
    3. Send bc-22298e90 the docstring-only change. The assessor rates the basis, and the GO'd TT_OUT(1/400) stands.
  - **If it fails:** write in the staging README that the charged forms stay uncited, because their Δ is the catalogue
    copy's, and that v2-hot is parked.
- **v2-hot Lean (M2b),** held with bc-824e54a2 and bc-876ca543: drop it if fix (2) fails. If it passes, the merge set
  leaves out the two charged files.
- **v1-hot:** nothing to do while it's parked.
- **What I'd stop:**
  - the derived-charge route: Δ's table, its extension, and any re-pin of the charged forms;
  - rebuilding long-window tables for k > 8,192.

## 5. Traps

- **The charged forms' Δ (0.8012 and 0.9885 atoms) is the catalogue copy's.** On the audited catalogue, Δ ≥ 1.488 atoms
  at t_c = 4, so never cite them.
- **`TTOutV2HotCharged.lean` pins `NoAlignedExactRegionHot.lean` by hash.** Changing the region file leaves that pin stale.
- **The audited table reads the staircase at the next multiple of 8 rows up,** so a step at r rows stands for blocks of
  r − 7 rows.
  - `deltacharge.py` reads only `blocks` (at most 8,192 columns); `blocks_wide` is for wider units.
  - The staircase is a lower bound, and it stops at 256 atoms.
- **γ:** an uncredited or charged amount enters ω, so it adds its whole share to γ. It never scales γ.
- **Region checks count rows × columns.** One row is exact on about 95% of the columns at the start, and a 4-atom prefix
  bound holds only at the same row count.
- **Lean in these files:**
  - `norm_num` can turn an impossible split case into `False` and stop: use `first | (exfalso; omega) | norm_num`;
  - numerals in a lemma's statement default to ℕ unless typed as ℚ;
  - `if_pos` and `if_neg` are deprecated: use `split_ifs`.
- **The store's filesystem returns EAGAIN now and then.** Copy with retries and check with `cmp`.
- **Pushes to research-notes get a 403 from this Project's VMs,** and the Verity broker serves `danielreuter/verity` only.
  Use `internal/pouw-fp8/accounting-outbox/`.
