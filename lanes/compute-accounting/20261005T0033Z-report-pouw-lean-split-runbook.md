---
id: 20261005T0033Z-report-pouw-lean-split-runbook
campaign: pouw
lane: compute-accounting
kind: report
status: final
repo: danielreuter/verity
origin: bc-52ff1136
---

# Runbook: split PoUW's Lean into spec + `security_proofs/pouw`

Lane `pouw-split`, written 2026-10-05T00:29Z (after `date -u`). Dry-run against slice 6's tip (#1132,
`cursor/pouw-lean-l3-slice6-b890` at f27afa5ef) merged with main; ready to fire when #1132 lands.

## TL;DR

- Use lean's split.py from #1167 (`cursor/layout-move-lean-741b`, f102935e7), not the older dry-run branch's
  (bd202e480). #1167's renames the proof modules to `PouwProofs.*` (declarations keep their `Pouw.*` namespaces),
  writes `proved_in` into the spec's lock and rewrites imports, which is #1144's module-root rule. The older tool keeps
  module names (`Pouw.*` in both packages): that builds with `lake build`, but `lake env lean` (the audit's Facts and
  Replay) resolves a root from the first search-path entry holding a `Pouw/` directory, so the audit cannot run on it.
- One command, `--keep Pouw.SecurityProofs.Dimension.Lifting`; no refusals in any variant; no Lean edits, not even
  import trims.
- One Python follow-up commit (the generators and three tests now read and write `security_proofs/pouw`).
- Pod audit of the split (run `r20261004-235418-eb72` on vy-nebius-1): **PASS**, 16255 declarations in 303 modules,
  only `propext`, `Classical.choice` and `Quot.sound`; 800 guarantees; guarantees (800), reads (128) and dependencies
  (9) of the regenerated lock are byte-identical to the spec's.

## Must land first

1. #1144's stack and #1167 (lean's layout move): core's proofs become `VerityProofs.*`, which PoUW's proofs import
   (`HiddenGamma`, `HiddenTileGame` and `TileCircuit` import core's `SecurityProofs`). This also brings in the
   `proved_in` audit (`audit.py SPEC` audits the spec and the proofs packages named in its lock), the new merge.py and
   #1167's split.py. Without #1167 the split can't be audited the way `check` audits it.
2. #1132 (slice 6). As of 2026-10-05T00:24Z neither #1132 nor #1167 is on main (main b529216bb). The dry-run base
   still merges cleanly with that main (`git merge-tree`); main's only lean change since the base is a new
   `tools/lean/lean_audit.py`.

Order between #1132 and #1167 doesn't matter: the scratch v2 branch merges #1167 into #1132+main with no conflict.
One catch: git runs the merge driver from the worktree's own `tools/lean/merge.py` at merge time, so an older branch
runs an old driver. If `lean-audit.json` conflicts, run main's driver by hand:
`git -c merge.lean-audit.driver="python3 $PWD/tools/lean/merge.py %O %A %B %P" merge ...`, or run
`python3 tools/lean/merge.py BASE OURS THEIRS protocols/pouw/lean/lean-audit.json` on the three stages.

## Fire (on landed #1132 + #1167)

~~~bash
git fetch origin main
git worktree add -b cursor/pouw-lean-split-<suffix> /tmp/wt-pouw-split-fire origin/main
cd /tmp/wt-pouw-split-fire

# 1. plan (prints, writes nothing). Expect: spec 150 modules (149 the lock trusts + 1 tool), proofs 154 under
#    PouwProofs, "guarantees 800 and reads 128 stay byte for byte", no "refused".
#    The package path is relative to the cwd: run it from the checkout you mean, never from a split tree.
python3 tools/lean/split.py protocols/pouw/lean --area pouw --keep Pouw.SecurityProofs.Dimension.Lifting

# 2. apply
python3 tools/lean/split.py protocols/pouw/lean --area pouw --keep Pouw.SecurityProofs.Dimension.Lifting --apply
git add -A protocols/pouw security_proofs/pouw tools/lean/lean-deps.json
git status --short | grep '^??'   # prints nothing: everything the split wrote is staged
git commit -m "Split PoUW's Lean: spec in protocols/pouw/lean, proofs in security_proofs/pouw (PouwProofs.*)"

# 3. the Python follow-up (generators + 3 tests + suite inputs). It cherry-picks cleanly onto the split.
git fetch origin cursor/pouw-lean-split-on-1167-7167
git cherry-pick cbdf7a8a6
~~~

The Python follow-up does this:

- `protocols/pouw/lean/scripts/{fp8atom_vectors,row_prims_vectors,h1t_vectors}.py` gain `--proofs-out` (default
  `--out` if given, else `security_proofs/pouw`) and write the checks under `PouwProofs/SecurityProofs/...` with
  `import PouwProofs...`. The spec halves (`Pouw/Protocol/...` vectors) stay under `--out`.
- `tests/test_row_prims_lean.py` and `tests/test_lean_package.py` generate into `tmp/spec` + `tmp/proofs` and compare
  each half with its package. `tests/test_cap_lean.py` reads `security_proofs/pouw/PouwProofs/SecurityProofs/PearlC/Cap`.
- `protocols/pouw/pyproject.toml`: `[tool.verity.tests] inputs` gains `security_proofs/pouw`.

If slice 6 changes a generator or a generated file before landing, regenerate after step 3:
`python3 protocols/pouw/lean/scripts/<gen>.py` (defaults now write both packages) and commit any diff.

### If #1156 (`cursor/pouw-lock-reduction-e3fa`, 800 → 151 guarantees) lands first

- #1156 conflicts with #1132 in `protocols/pouw/lean/lean-audit.json` only. merge.py refuses: #1156 stops reading
  definitions (for example `Pouw.PearlC.CodeSeedNoise`, `Pouw.PearlC.pearlCTiles`) in modules whose reads #1132
  changed, and `Pouw.PearlC.rowDrawn_satisfiable` reads `Pouw.Protocol.Fp8Atom.E4M3` while the merged record doesn't
  list it. The fix is #1156's own: regenerate the record on the merged tree (`audit.py --update`, a Lean build, on a
  pod). The split then fires on that.
- #1156's lock as pushed (dddd02aad) still lists the old reads. Regenerated at 151 pins it reads 82 modules. Dry run on
  that regenerated lock: no refusals, spec 149 / proofs 151 without `--keep`.
- **Drop `--keep`**: #1156 unpins Lifting's 4 theorems, so Lifting becomes a pure proof module
  (`PouwProofs.SecurityProofs.Dimension.Lifting`). Its `layers` entry goes with it, since split.py moves a non-spec
  layer to the proofs lock.
- Spec shrink under the 151-pin lock: the spec's module count doesn't change (split.py takes everything under
  `Protocol/Assumptions/Guarantees` by prefix, plus the read modules). Only reads shrink: 66 of the spec's modules go
  unread at 151 pins, against 21 at 800. A minimal spec (the closure of the read modules plus `Guarantees.*`) would be
  about 95 modules. Moving the other ~53 out means renaming spec-named modules, which is a later step and not this split.

### If #1154 (`cursor/pouw-guarantees-lift-e3fa`) lands first

- It merges with #1132+main cleanly, lock included, under main's merge driver. It adds `Pouw/Guarantees/PearlC.lean`
  (spec) and a `SecurityProofs/PearlC` proof module.
- Dry run with #1167's tool on #1132+main+#1154: no refusals. With `--keep Lifting`: spec 151 (150 trusted + 1 tool),
  proofs 155; guarantees 800 and reads 129 kept byte for byte. Fire with the same commands.

### #1156 together with #1154

They conflict with each other in `lean-audit.json` (merge.py refuses on `TTOut`, `Fp8Atom.Atom`, `Fp8Atom.Fp32`,
`Device*` and `SkipP` reads) and in `price_twins.py`. That's a merge for their authors; I didn't dry-run it. Once
merged, the rules above apply: no `--keep` if #1156 is in.

## `--keep` and why

`Pouw.SecurityProofs.Dimension.Lifting`, while the lock pins its theorems (the 800-pin lock; also #1132 and #1154):

- `card_le_pow_of_sub_mem`, `grid_card`, `slice_card_le_of_subspace` and `solutions_card_le` are guarantees, and their
  statements read its own definitions (`grid`, ...).
- It is already one of the spec lock's `roots`, with its own `layers` entry: imports Mathlib only ("the lifting
  worker's grid-density and slice lemmas (L2, L3) stand alone on Mathlib").
- top's plan keeps it with the spec.

Kept under its proof-style name (split.py keeps `--keep` names). Without `--keep` the plan doesn't refuse, but it moves
pinned guarantees into the proofs package, which contradicts the lock's roots and layers. After #1156 none of the four
is pinned, so it goes.

## Post-checks

1. Pure move. The spec lock's `guarantees` and `reads` must be text-identical to main's; only `roots` and `proved_in`
   change:
   ~~~bash
   python3 - <<'EOF'
   import json, subprocess
   a = json.loads(subprocess.check_output(["git", "show", "origin/main:protocols/pouw/lean/lean-audit.json"]))
   b = json.load(open("protocols/pouw/lean/lean-audit.json"))
   for k in ("guarantees", "reads", "assumptions", "meaning"):
       print(k, json.dumps(a.get(k), sort_keys=True) == json.dumps(b.get(k), sort_keys=True))
   print("changed:", sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k)))   # expect roots, proved_in (+ layers if no --keep)
   EOF
   S=$(git log --format=%H -1 --grep="Split PoUW's Lean")   # the split commit
   git diff -M --summary $S^ $S | grep -c rename   # 152 on the base: 154 moved, but the 2 aggregators show as D+A
   d() { git diff -M $S^ $S -- '*.lean' | grep "^$1[^-+]" | grep -v "^$1import " | cut -c2- | sort; }
   diff <(d -) <(d +) && echo "only imports changed"
   ~~~
   Every moved `.lean` file differs only in `import` lines: `Pouw.` → `PouwProofs.` for moved modules, and
   `Verity.SecurityProofs.` → `VerityProofs.SecurityProofs.` for core's proofs. Git doesn't detect the two
   aggregators as renames: `Pouw/SecurityProofs.lean` (145 imports rewritten) and
   `Pouw/SecurityProofs/Fp8Atom/Checks.lean` show as deleted plus added. So the check compares the removed and added
   non-import lines as multisets; on the v2 branch they're equal.
2. Suites, serially: `uv run tools/check/suites.py verity-pouw`, then `verity-lean-audit`, then `repository`. On the
   scratch tree these gave 648 passed / 2 skipped, 92 passed and 82 passed. The 2 skips are pre-existing:
   `verity_pouw.circuit.cap` is absent. To run a test file by hand from a worktree, set
   `PYTHONPATH=$PWD/protocols/pouw:$PWD/packages/verity/src`, because the package has no `src/`. Otherwise
   `/workspace/.venv` imports `/workspace`'s `verity_pouw`, from whatever branch is checked out there, and the cap pin
   test fails on unrelated numbers.
3. The Lean audit, on a pod, never locally:
   `uv run python tools/check/check.py --record --on vy-nebius-1` (the merge gate). With `proved_in` it runs
   `audit.py protocols/pouw/lean`, which builds and audits the spec and `security_proofs/pouw` together. The Lean
   build alone is about 16 min on vy-nebius-1 (build 964 s, replay 179 s, total 1376 s).
4. Cosmetic, optional: `security_proofs/pouw/lake-manifest.json` gives verity's dir as
   `../../protocols/pouw/lean/../../../packages/verity/lean` (un-normalized, but it resolves).

## The audit run

- Run `r20261004-235418-eb72` on vy-nebius-1, `rc 0`, class SUCCESS. Job: `audit-job.sh` in this folder, launched by
  `research run --on vy-nebius-1 --cwd source --declared-output 'out/*'`.
- Commit audited: `27ef21c97` on `cursor/pouw-lean-split-dryrun-e3fa`, which is the names-kept split (7e47f9c2b) plus
  `reroot.py` moving the proofs under `PouwProofs.*`. Its Lean files are identical to #1167's split (v2 branch,
  0d727a8d2) except the three imports of core's proofs: `Verity.SecurityProofs.*` there, `VerityProofs.*` on #1167.
- The base has no `proved_in`, so the job audited the proofs package against a check lock: the spec's lock with
  `roots = PouwProofs + spec roots`, minus `exempt` and `runs`. Steps and results:
  - Step 1: the spec's `lake build`. rc 0.
  - Step 2: build the check lock.
  - Step 3: `audit.py --build security_proofs/pouw`. **PASS**: 16255 declarations in 303 modules; axioms `propext`,
    `Classical.choice`, `Quot.sound`; 800 guarantees. Built without a sandbox: `unshare` isn't available on the pod.
  - Step 4: `audit.py --update --no-replay`, then compare with the spec's lock: guarantees 800/800, reads 128/128 and
    dependencies 9/9, all text-identical.
- Verdict: the split is a pure move, and the proofs prove every pinned guarantee from the spec unchanged. This uses
  the one pre-approved audit run; `audit.py SPEC` on #1167's tree itself (proved_in) is left to `check --record`.

## Branches and files

- `cursor/pouw-lean-split-dryrun-e3fa`, head abf56e29d:
  - base cebac7cf4 (main 5049de02f merged into #1132 f27afa5ef);
  - 0a23b9fd9 (split.py from bd202e480, scratch);
  - 7e47f9c2b (names-kept split);
  - 27ef21c97 (reroot to `PouwProofs`, audited);
  - abf56e29d (Python follow-up).
- `cursor/pouw-lean-split-on-1167-7167`, head cbdf7a8a6. This is the shape to fire:
  - 617ea6a8c (#1167 merged into the base);
  - 0d727a8d2 (#1167's `split.py --apply`);
  - cbdf7a8a6 (the Python follow-up, cherry-picked; the 3 tests pass: 7 passed, 1 skipped).
- In this folder:
  - `audit-job.sh`: the pod job.
  - `reroot.py`: the scratch reroot, superseded by #1167's split.py.
  - `pr.md`: the PR text.

## Out of scope

Moving the silicon models (`Sm120`, `DevicePricesLoop`, `devSm120v1` from `Device.lean`, and `Fp8Atom.{Atom,E4M3,Fp32}`)
to `catalog/silicon/` Lean. They stay in the spec as they are; the split doesn't touch them.
