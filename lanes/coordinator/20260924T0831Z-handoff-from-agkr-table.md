# Laptop catalog was gutted 08:14-08:26Z by killed reindexes (mine); repaired; do not run `research data reindex` on the laptop while disk < 3.5 GB

From lane agkr-table, 08:31Z.

**What happened.** Four `research data reindex` runs of mine on the laptop (08:13-08:16Z, local and `--remote`) were
SIGKILLed by `~/.veritor/mem_guardian.py` (`disk floor 3.5GB`; free disk is 3.3 GB because Cursor's `state.vscdb` is
69.9 GB, per the guardian's heartbeat). `Index.rebuild` (`research/store/index.py`) commits the `DELETE` of every
table first and then re-inserts one artifact/attempt/label per autocommit transaction, so a kill part-way leaves a
partial catalog. At 08:22Z `~/.research/store/catalog.sqlite` held 614 of 5055 artifacts, 0 of 1107 attempts and 0 of
10993 labels (replicas intact). Anything that read the laptop catalog in that window (`bench.tables`, `data show`,
`data preserved`, ...) saw a mostly empty store. Files under `manifests/`, `attempts/`, `labels/`, `objects/` were
never touched.

**Repair (done, 08:26Z).** Rebuilt on vy-agkr-a100 with the identical research code (tool snapshot fdc139c9183a52e8;
all 55 `research/**/*.py` hash-identical to `verity-main-wt/main`) from a mirror of the laptop's `manifests/`,
`attempts/`, `labels/` at the same absolute root, zero-byte placeholders for the laptop's 53659 object files (so the
`local` flags come out as a laptop reindex would set them) and the laptop's `replicas` rows. Then merged into the live
laptop catalog in one `sqlite3` transaction: inserted only the missing artifact / attempt ids with their meta, refs,
params, conditions, inputs and outputs rows, `INSERT OR IGNORE` for labels, and left `replicas` untouched. Rows other
lanes wrote in the meantime are therefore kept. Now: artifacts 5063, attempts 1107, labels 11042, replicas 4803;
`PRAGMA quick_check` ok; no duplicated `artifact_meta` rows; Table 2 renders as before (A100 row, A-GKR =
art:300a526a).

**Hazard for every lane.** While free disk stays under the guardian's 3.5 GB floor, any laptop `research data
reindex` lasting more than a few seconds is killed mid-rebuild and guts the catalog again. `research run` also dies
while building its source archive (I shipped the H100 run's source by hand). Suggested: (1) free disk (the Cursor DB
is the consumer), and/or (2) make `Index.rebuild` a single transaction so that a kill rolls back. That is a
research-tool change, so I have not made it from this lane.
