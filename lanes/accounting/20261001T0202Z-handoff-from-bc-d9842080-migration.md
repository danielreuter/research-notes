---
cursor:
  subagentId: "bc-d9842080-f8c7-54a2-84bb-ba0a4b680482"
id: 20261001T0202Z-handoff-from-bc-d9842080-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: FP4-tile model and fast-matmul catalogue audit (bc-d9842080)
---

# Migration handoff from bc-d9842080 (FP4-tile model, catalogue audit): nothing in flight, everything in the old store, one parked item

Written 7:02 PM PDT for my replacement in compute accounting's Project. The old store is
`/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/`, written `$OLD` below.

## 1. Branches and PRs

- **None.** I own no branch or PR in `danielreuter/verity`. My work is all in the old store.

## 2. Runs and jobs in flight

- **None on my VM or on node 2.**
- **v1's full-catalogue closure is finished.** My VM ran seven regions; bc-2aa33ad8 ran the other three on node 2
  (sharded, seeded at the copy's costs). The outputs are preserved at `$OLD/internal/pouw/rtx-pro/catalogue-audit/node2/`
  and `.../vm-runs/`. The assessor kept it at B at 5:30 PM PDT.
- **`floor-staircase-fine.sh` was never queued.** It's in `$OLD/internal/pouw/rtx-pro/cpu-fill/` and is parked on the
  backlog ("finer staircase floors").

## 3. Half-done state, and where everything is

Nothing is left only on my VM: its logs and outputs were copied to `$OLD/internal/pouw/rtx-pro/catalogue-audit/vm-runs/`
at 7:05 PM PDT.

**The catalogue audit,** `$OLD/internal/pouw/rtx-pro/catalogue-audit/` (the report is `fast-matmul-catalogue-audit.md`):
- **`catalogue-ac13ca88/`:** the file set the `Prop`s name.
  - It holds 4,180 schemes from Perminov's repository at `ac13ca88`, each verified exactly, as `schemes.tar.gz` plus
    `manifest.json`, `catalogue_stats.json` and `IDENTITY.txt`.
  - The manifest's sha256 is `dac7cee1e70c77551efdaaecb8b754cfdce1e020576d878b7e256e936be2f88b`.
- **`floors/`:**
  - `row-floors-staircase.json` holds W*(L, M), a sound lower bound, for every L from 4 to 256 and every 8 rows up to
    8,192, with zero padding and every contraction factor.
  - `whole-composition-floors.json` holds W*(L).
  - bc-b58c6093 (block table, GPU 3's list) and bc-3006c44a (Δ) read these.
- **The scripts** are at the folder's top level: `canonicalize.py`, `publish_catalogue.py`, `staircase.py`,
  `widthfloor_integral.py`, `alt_from_stats.py`, `catalogue_stats.py`, `free_family_padded.py`, `free_family_compare.py`
  and `smirnov_fp16.py`.
  - They read bc-3006c44a's `min-merge-search/` as the catalogue directory, for `alt.py`'s helpers, `known.py` and
    `merges.py`.
- **Outputs:**
  - `free-family/`: the region family on the current ranks, and the padded comparison.
  - `fp16-exactness/`: Smirnov's ⟨3,3,6;40⟩ on v1's data.
  - `node2/`: v1's last three regions.
  - `vm-runs/`: my VM's logs and outputs.

**Node 2 jobs,** `$OLD/internal/pouw/rtx-pro/cpu-fill/catalogue-audit-jobs.md`:
- `v1-closure-full-catalogue.sh` is done.
- `floor-staircase-fine.sh` is parked.

**The FP4-tile model,** `$OLD/docs/pouw/fp4-tile-model.md`, with its rows (`$OLD/internal/pouw/fp4-tile-model-rows.md`)
and notes (`nvfp4-int8-flatness-break.md`, `rtx-pro/fp8-v1-postadd-construction.md`):
- They are current to 5:20 PM PDT.
- The Lean is merged into `$OLD/lean/submissions/pouw/Pouw/TileBound/`: Theorem 1, the format closures, the
  Winograd–Strassen witness and the FFMA docstring patch.
- Bundle 3 (`$OLD/internal/pouw/fp4-tile-lean/bundle-3/`, tile index sharing) is staged, paused and unpinned, as
  §7.9 says.

## 4. The next step for each kept item, and what I'd stop

- **Finer staircase floors** (backlog: parked, Daniel decides). **Stop it.**
  - It can only raise the floors, by at most the 19% grid error in rows.
  - It can't move v1's verdict (closed at B), and v2-hot's clause (b) is decided by GPU 3's measured widths against the
    published staircase.
  - Run it only if one of GPU 3's blocks lands within 19% of a floor. It needs about 5–10 CPU-hours and 30–50 GB.
- **The floors and the file set:** keep them as they are. They are the inputs to bc-b58c6093's block table and GPU 3's
  list, and to bc-3006c44a's Δ (if clause (c) fails).
  - The only follow-up is answering their questions; no recomputation is pending.
- **The free family with zero padding:** the flag stands.
  - Every minimal shape R₀ × C₀ at tensor cost T also pays on M × N with M ≤ R₀, N ≤ C₀ and M·N > T·R₀·C₀.
  - Results 17, v2's region-lemma B and v2-hot's clause (b) need rerunning against it. Those reruns belong to
    bc-b58c6093 and GPU 3, not to me.
- **c_L in F2:** catalogue routes undercut Strassen's c_L by 2.3–4.0 points (0.776 against 0.808 at 8,192³).
  - The fix is the assessor's and the FP4 table owner's: pin the catalogue minimum, or Strassen's formula minus 0.04.
  - No rating moves.
- **Smirnov's FP16 exactness:** informational; nothing to do unless someone wants an exactness-aware floor.
- **The 99 projections beyond dimension 16:** drop. I have no files for them, and they lower nothing unless their
  forms repeat.
- **Bundle 3 (tile index sharing):** keep it parked. NVFP4's int8 cell is decided by F1′'s cap and F2, not by tile
  sharing.

## 5. Traps

- **`pkill -f PATTERN` kills your own shell** whenever the pattern also appears in that command line, as it does when
  the same command edits or runs the script. Find PIDs in one call and `kill` them in another.
- **Pushing to research-notes:**
  - The VM's default token gets a 403 (`cursor[bot]`). Verity's broker covers only `danielreuter/verity`.
  - Use `RESEARCH_NOTES_TOKEN` with the `https://notes@github.com/...` URL and its credential helper, as in
    `kb/cloud-lane-setup.md` §1. Otherwise use the store outbox.
- **The store's FUSE mount is flaky with large writes.** Copy, then `cmp`, and retry on a mismatch.
- **`alt.py` and `alt_k.py` allow only the contraction factors 2, 4 and 8.** For a 4-atom window every c with Π c ≤ 8
  fits. `alt_from_stats.py` takes `CSET`; v1's run used `CSET=2,3,4,5,6,7,8`.
- **`widthfloor.py`'s W*(L) is an LP relaxation on a T grid,** loose once K-factor-3 levels exist. Use the published
  whole-composition and row-dependent floors instead. The block widths in `v2hot-blocks-corrected.json` came from the
  old LP table on the copy.
- **`staircase.py`:**
  - keep `GRID` > 0 for rows and columns (GRID=0 runs out of memory);
  - the K factor must stay exact: rounding it let 9-atom compositions "fit" 8 atoms;
  - the published table is GRID=4.
- **Perminov's JSON gives w as n₃ × n₁.** The `.mpl` and brace files give C as n₃ × n₁, transposed to n₁ × n₃. My
  canonical files are all n₁ × n₃.
- **55 of the `.mpl` tensors use arithmetic expressions** (`-(1-0)`, `1**2*0`) that `known.parse` rejects;
  `catalogue_stats.py` evaluates them safely.
- **`catalogue_stats_perminov_all.json` records VM paths** (`/tmp/fmm-perminov/...`). Use the published
  `catalogue-ac13ca88/catalogue_stats.json`, which is equal scheme by scheme and keyed by canonical file.
- **`smirnov_fp16.py` needs v1's data generator,** `pearlc_hot_start.units`, from scheme commit `04734fb5`
  (`git archive 04734fb5 protocols/pouw`, on `PYTHONPATH`) plus `cheap-binding/`'s `pearlc_*` helpers.
- **The staircase and the floors are lower bounds.** They ignore merges, the E4M3 → FP16 conversion and FP16
  exactness. Don't cite them as costs a real rewrite achieves.
