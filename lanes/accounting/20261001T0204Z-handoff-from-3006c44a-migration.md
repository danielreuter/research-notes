---
id: 20261001T0204Z-handoff-from-3006c44a-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-3006c44a
---

# bc-3006c44a's migration handoff (the theory lane for Pearl-C on sm_120: fast-matmul bounds, v1's W1 and wall-time closure, v2-hot's Δ)

For my replacement in compute-accounting's Project, per `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`.
Store paths below are under `/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/`.

## 1. Branches and PRs
- **#451, `cursor/pouw-pearlc-census-a818`**, head `2f06c9b9`. Draft and mergeable, no `check` recorded, no comments, untouched since
  11:46 PM PDT on 29 Sep. It holds Pearl-C's falsification census and U-quality research tools (`benchmarks/pouw`), and it isn't on
  any merge train. **Left:** decide whether to record `check` and request a merge, or close it. Nothing cites it as merged.
- **`cursor/pouw-lean-ttout-a818`**, head `8f56a604`, a 29 Sep Lean staging of TT_OUT(1/400). It was on my VM only; I pushed
  it to origin tonight to preserve it. bc-b58c6093's `cheap-binding/ttout-lean-staging/` supersedes it, so it is **not for a PR**. Delete
  it once you agree.

## 2. Runs and jobs in flight
- **No research runs and no fill jobs** of mine are in flight. All 36 runs under this VM's `~/.research/runs` are done or
  failed, from 30 Sep.
- **Two CPU processes on my VM only** (tmux session `delta`, `/tmp/sm120/merge`), both `deltatc.py`: v2-hot's charged Δ on the
  audited table, at t_c = 4 and 6.
  - At 7:03 PM PDT: **t_c = 4: Δ ≥ 1.554 atoms** (a 28-atom window); **t_c = 6: Δ ≥ 2.232 atoms** (14 atoms).
  - **No custody.** They end when my VM stops. Their logs as of 7:03 PM PDT are in the store (`min-merge-search/vm-logs/dtc_4.log`,
    `dtc_6.log`).
  - **The backlog says drop them, and I agree:** the charged route is dead (compute-accounting 6:04 and 6:11 PM PDT), so a
    higher floor decides nothing.

## 3. Half-done state
- **The work's home is the store's `internal/pouw/rtx-pro/min-merge-search/`:**
  - **Scripts:** `deltacharge.py` (the original case split); `deltaexact.py` (the LP's maximum exact in T);
    `deltafast.py` (`2bc1d72f…`: the fast enumeration and the whole-composition bound); `deltadeep.py` (`8dcf2df4…`: windows to
    2,048 atoms); `deltav2.py` (`7dfb0170…` as run, start atom now a parameter); `deltatc.py` (`b1ead9e9…`); `deepbands.py`;
    `savingcap.py`, `tailcap.py` and `rowscap.py`; and `alt.py` / `alt_k.py` with the catalogue copy (`alt/`, `schemes/`, `known/`).
  - **Results:** `delta_by_n_k_p8.0_copy.json` (`5d9c2b0d…`) and `v2hot-blocks-extended-257-2047.json` (`c8866903…`). Both are
    pinned in bc-b58c6093's charged TT_OUT staging, and both are now uncited. Also `deltav2_p8.0_n8192.json` (`20d38992…`, plain v2
    from atom 10: 2.086 atoms, 1.185% packed, on the copy), `deepbands_p8.0_copy.json` and `deltadeep_p8.0_n*.json`.
  - **`vm-logs/`** (23 files, created tonight): every VM-only log, and the contraction-factor checks (`wi_allc.py`,
    `wf_allc.py`, `wi_saving.py`, `fa_*.log`).
- **Documents I own** (cursor frontmatter `bc-3006c44a-…`):
  - `docs/pouw/cheap-binding.md`: §4 items 7–8 are v1's W1 and wall-time γ; §6 is v2-hot's status, current to 6:11 PM PDT;
  - `internal/pouw/rtx-pro/theory-pearl-c-sm120.md` §14 (the fast-matmul bounds and the wall-time addenda);
  - `internal/pouw/rtx-pro/v2-hot-first-atoms-row.md` §5 and §5a;
  - `internal/pouw/rtx-pro/min-merge-search/rewrite-mix.md` (the co-issue probe's spec);
  - `internal/pouw/pouw-fp8/rowseed-fragdraw-ruling.md`.
- **Only on my VM, and not needed:** a copy of the catalogue at `/tmp/sm120/merge/{alt,schemes,known}`, identical to the store's
  (546 files, digest `79bcc8b5…`), and a research-notes clone. Nothing else is unpreserved.

## 4. The next step for each kept item
- **v1 headline (keep).** Nothing is left from me. Its code rides #449 and #548 on the merge train. Its basis is
  `post-add-bound/sm120-preadd` (B): v1's W1 closure is ≥ 1.0128 at the 8,192-column unit and ≥ 1.0919 on the measured regions,
  on the catalogue copy. bc-d9842080 was rerunning that closure on the full catalogue. **Next:** check that its result landed. If a
  margin moves, update `cheap-binding.md` §4 item 8 and theory §14.
- **v1 register-copy check (keep).** GPU 0 (bc-e6a46970) runs it as a roughly 40 s fill job (`server.md`); the spec is in
  `rewrite-mix.md`.
  - **How to read it:** v1 stays ≤ 1% at its published cast while the copy-free floor stays above about 1.055. The worst case,
    copies fully breaking, is γ ≤ 1.28% as written and ≤ 1.00% packed.
  - **Next:** put the number in `cheap-binding.md` §4 item 8 and theory §14.
- **v2-hot charge searches and their final bound (drop).** I'd stop them. A final bound would need the remaining lengths plus an
  enumeration that admits zero padding: hours, for no decision.
- **Routes back down for v2-hot's charged figure (morning proposals).** A fit-aware bound on the tall, narrow survivors. My
  proposal: an enumeration with padding ratios in its admissible pruning, using the staircase where it closes bands.
- **What I'd stop doing:** any further charged-route Δ work unless compute-accounting picks a route back. v2-hot's live question
  is fix (2), GPU 3's.

## 5. Traps
- **The store filesystem** throws EAGAIN on writes now and then. Retry with a sleep, and verify copies with `cmp`.
- **Parallel tool calls race:** a file written in the same batch as the shell that uses it may not exist yet.
- **`pkill -f` or `grep` patterns that appear in your own command line kill your shell.** Anchor them (`^python3 deltatc.py`).
- **Two catalogues.** Files named `*_copy*` are on the 479-file copy, not the audited set (manifest `dac7cee1…`, 4,180 schemes).
  `alt_k.py` defaults to c ∈ {2, 3, 4, 6, 8, 16}, but the audited model needs every c from 2 to 16. `deltaexact.py`'s `STATS=` loader
  (`catalogue-audit/catalogue-ac13ca88/catalogue_stats.json`) does that by default.
- **The exact enumeration admits no zero padding,** so under the audited model it isn't a strict upper bound. The LP and
  whole-composition bounds are, but without the enumeration they're useless (132 atoms).
- **For units wider than 8,192, Δ** rests on the 4-atom block 640 × 10,726, which no measurement has tested (the assessor's
  width caveat).
- **γ's base values:** v2-hot's own 0.36217% / 0.37071% / 0.64670% at FADD 8.376. γ = 1 − (1 − γ_now)·(1 − 1/400 − Δ)/(1 − 1/400),
  with Δ = atoms·32/k.
- **The research-notes clone goes stale.** Fetch before you read the lane.
