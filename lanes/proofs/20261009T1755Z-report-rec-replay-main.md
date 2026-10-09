---
id: proofs/20261009T1755Z-report-rec-replay-main
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-ab22ea8f-7188-52ea-b8be-e580764a0419
---


# The wired-circuit folds again, on main 6cea9a973 plus the harness (lane rec-v0)

For the proofs coordinator (bc-8416bc72). Times are Pacific (PDT); machine stamps stay UTC. Written at 10:55 AM PDT
(17:55Z). The run before it, `r20261009-170419-af54`, is in `internal/private-circuit/rec-private.md`, in the section
"The wired cheater through `InnerFold.lean --program` on main".

## Answer

**Yes. On main `6cea9a973` (with #1626 and #1635) plus #1651's harness, all 12 of af54's verdicts are the same, and each
of the four wired cheaters is still refused at `setup: links`, at the same cut wire.** No verdict changed, so nothing was
re-run.

af54 replayed no outer part (`PARTS=-`). Its 12 rows are V*'s three folds of the wired circuit for each of the four
runs: the wired cheater with the program, and the honest wired statement with and without it. This run has the same
12 rows.

## Run and tree

- **Run** `r20261009-174714-8134` on vy-nebius-1: SUCCESS (rc 0), 17:47:40Z to 17:51:33Z (234 s), and PRESERVED. Its
  run record, holding its `out/`, is `art:10bcb692b070421a8d332738eae19c317a0ce1478d85b3292b3dfe9313b3c8fa`.
- **The same command as af54:** `92-rec-private-reverify.sh`, with the same `RUNS` and `RESTORED`, and `PARTS=-
  FOLDS_ONLY=1 JOBS=4 CPUS=16`.
- **Resources:** CPU only, with `--declared-output 'out/*'`. It was pinned to cores 0-15, af54's slice. Node 1's check
  slots are `a` (32-63) and `b` (64-95), both held by checks at launch, so the run took no check slot.
- **Tree** `251814c669e5` on `cursor/rec-replay-main-95d4`, which stacks three commits:
  - main `6cea9a973`, which contains #1626 (`0b533f684`) and #1635 (`1d9cfaff1`);
  - `c0454cacc`, a merge of #1651's head `51b3b426d` (`cursor/innerfold-program-95d4`), so the tree holds the PR's own
    commit;
  - `251814c66`, which adds the pod driver: `92-rec-private-reverify.sh`, `rec_private_coins.py` and
    `rec_private_summary.py`. These are `cursor/rec-replay-run-95d4`'s pod files with `FOLDS_ONLY`, byte-identical to
    af54's tree `493b7d150`.
- **The diff against main** (`git diff --stat 6cea9a973 251814c66`) is the harness and `pod/` only:
  - `verity/ml/flock/tests/lean/InnerFold.lean`: +11/−3, byte-identical to af54's;
  - `verity/ml/flock/pod/`: the three files, +474.
- **Rebuilt from main:** the flock package changed with #1626 (`Flock/Firewall/Contract.lean`, `lean-audit.json`), so
  Lean's tools were rebuilt. `inner-fold`'s sha256 is `9557417cc3daf72a…`, against af54's `fab638a47f417bf4…`, and
  `flock-verify`'s is `e667ce741cc7d362…`.
- **What it read:** the same as af54.
  - The recorded verdicts came from the restored copies under `/workspace/jobs/rec-v0/data/restore/`. Their digests are
    byte-identical to af54's (and 53f3's).
  - The folds' statements, programs and points came from each run's data dir, which its L0 `sizes.txt` names.

## Verdicts against af54

| run | V*'s fold of the wired circuit | af54 | now (main 6cea9a973 + harness) | |
|---|---|---|---|---|
| 2922 (8090) | wired cheater (made-up), with the program | refused at `setup: links` | refused at `setup: links` | same |
| 2922 (8090) | honest wired, with the program | accepted | accepted | same |
| 2922 (8090) | honest wired, without the program | refused at `setup: META links` | refused at `setup: META links` | same |
| 6720 (16,16,8) | wired cheater (made-up), with the program | refused at `setup: links` | refused at `setup: links` | same |
| 6720 (16,16,8) | honest wired, with the program | accepted | accepted | same |
| 6720 (16,16,8) | honest wired, without the program | refused at `setup: META links` | refused at `setup: META links` | same |
| 80e4 (1024,1024,512) | wired cheater (made-up), with the program | refused at `setup: links` | refused at `setup: links` | same |
| 80e4 (1024,1024,512) | honest wired, with the program | accepted | accepted | same |
| 80e4 (1024,1024,512) | honest wired, without the program | refused at `setup: META links` | refused at `setup: META links` | same |
| 2f10 (real-class path) | wired cheater (made-up), with the program | refused at `setup: links` | refused at `setup: links` | same |
| 2f10 (real-class path) | honest wired, with the program | accepted | accepted | same |
| 2f10 (real-class path) | honest wired, without the program | refused at `setup: META links` | refused at `setup: META links` | same |

"Same" means the `now` text in `out/reverify.json` is identical to af54's, character for character, and so is the
recorded verdict it is compared against. The refusal without the program reads `setup: META links: Linking needs the
verifier's own program and partition (--program, --partition)` in every run.

## The `setup: links` refusal of each wired cheater

- 2922 (8090): `setup: links: cut wire [240, 248) from unit 0 to unit 8: the reader's row p1 is not the writer's committed output row (their b ‖ c differ)`
- 6720 (16,16,8): `setup: links: cut wire [240, 248) from unit 0 to unit 8: the reader's row p1 is not the writer's committed output row (their b ‖ c differ)`
- 80e4 (1024,1024,512): `setup: links: cut wire [30720, 31232) from unit 0 to unit 2: the reader's row p1 is not the writer's committed output row (their b ‖ c differ)`
- 2f10 (real-class path): `setup: links: cut wire [240, 248) from unit 0 to unit 8: the reader's row p1 is not the writer's committed output row (their b ‖ c differ)`

Each is the text the run itself recorded, and the text af54 gave.

## What it is evidence for

The evidence is the same as af54's, now on the verifier of record:
- `InnerFold.lean` runs main's own setup (`Stmt.setupTables`, with the Linking check that `verify --program` runs).
- When handed the verifier's program, that setup refuses the cheater's wiring and accepts the honest statement's.
- The cheater's program, partition and circuit are byte-identical to the honest statement's; only its public file
  differs.

No theorem covers `InnerFold.lean` or this Linking check. Main's `flock-verify` still refuses the plain-leaves form before
setup (`FlockVerify.lean:333`), so for the verifier itself the cheater's verdict stays "refused: uncovered form".
