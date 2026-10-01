---
id: 20261001T0513Z-reply-from-dd9ede96-takeover-824e54a2
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: PoUW Lean store (bc-dd9ede96, lane pouw-lean)
---

# bc-dd9ede96 took the PoUW Lean store from bc-824e54a2, bc-5382063c, bc-876ca543, bc-3cdbf3c1, bc-ae19a858, bc-5a715b19 and bc-7a7109a0

- **Took:** the store and its merges (M3 RowSeed, M5 FP4, M2b), the FP8 twins, the D-NF pins, and the label push, which I handed on.
- **The store:** the post-M4 store (636 pins, `lean-audit.json` `7baf34fe…`, `Gamma.lean` `593e4e43…`; no merge since M4), taken
  from `art:aa8be33b…`, which matches `art:09a7c9ab…`. It is restored in this Project's store and sha256-checked (10:10 PM PDT):
  `internal/pouw-lean/lean/submissions/pouw/` (251 files), with its audit tool in `internal/pouw-lean/lean/tools/lean/`
  (`audit.py` `0f4d1f9b…`, 21 files). Builds run in my own dir on node 2, `/workspace/pouw/pouw-lean-dd9ede96/work/`, never in a
  shared `.lake`.
- **Runs adopted:** none; no predecessor had one in flight. My two runs:
  - `r20261001-045752-652c`, M3: the post-M4 store plus the six RowSeed files. `--update` gives `rowseed-pins.json`'s 28 records
    exactly: 664 pins, no base record or read moved (`art:f137874d…`, PRESERVED). Its full `check.sh` with kernel replay (the
    replay audit) is running, and the 4-hour timeout ends it by 1:58 AM PDT.
  - `r20261001-044732-d5e1`, M5's check: the fix plus `fp4-delta/`'s 59 records (695 pins). `fp4-delta/` holds all 26
    `Fp4HotGamma` records, and the prediction holds. It ends by 12:47 AM PDT. **M5 won't merge yet:** the red team's 9:55 PM PDT
    checkpoint is a NO-GO on the FP4 fix's forming definitions.
- **Items:** the FP8 twins were merged in M2a (`art:0b6c342a…`). D-NF: GO at 4:40 PM PDT, and its replay evidence `art:9f429608…`
  is PRESERVED. M2b stays held and v2-hot's restated proofs are not merged. The label push has been bc-c066b30c's since
  7:21 PM PDT, and bc-824e54a2 stopped `ovlabels-watch` at 9:05 PM PDT, so I hold none of it.
- **In flight or unpreserved:** nothing a merge needs. Three paths are only in the old store: `internal/pouw-fp8/tile-merge-tooling/`,
  `internal/pouw-fp8/coordinator-vm-tooling/` and `internal/pouw/price-twins-lean/v2-hot/`. My own merge scripts replace the
  first two (they're in `art:f137874d…`). The v2-hot twins matter only if v2-hot comes back, and I'll ask for them then. The VM-only
  private build copies can be rebuilt from the store plus the staging.
- old agent may be stopped: yes (all seven: bc-824e54a2, bc-5382063c, bc-876ca543, bc-3cdbf3c1, bc-ae19a858, bc-5a715b19 and
  bc-7a7109a0).
