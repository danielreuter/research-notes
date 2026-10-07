---
id: rec-on-1163/20261007T0105Z-report-rec-on-1163-routes
campaign: proofs
lane: rec-on-1163
kind: report
status: closed
repo: danielreuter/verity
origin: bc-6a7b97b2 (worker for @proofs, launched by bc-7f347b4b)
---

# Rec stack routes 1 and 2: main merged into the rec heads, then into all 13 stack heads

Both routes are pushed: every head is a fast-forward merge, and each remote was confirmed at its expected sha just before
the push. Route 2's heads (main `e7b5caa89cc2`) were all pushed by 23:39Z. Every lock is unchanged, including
`verity/Security` and its `Proofs` package at #1318 and #1323 (re-recorded with kernel replay at 03:02Z, under
"Locks"), so no lock commit was needed.

Main moved after the route 2 pushes, to `e255a4efb`. That is the tip-84 train landing, and its tree is identical to tip
84's `a42083c10`. It touches no `.lean` file, lock or `tools/circuit_check` path, and all 13 new heads merge with it with
no conflicts. I did not re-merge.

## Route 1: main `327ea5b1b` into the four rec heads

| PR | branch | new head | parents (first, second) |
|---|---|---|---|
| #1081 | `cursor/rec-algebra-95d4` | `3cfdb7f4156529b812114a548b8d33d8ee34570c` | `845827f20`, `327ea5b1b` |
| #1245 | `cursor/rec-reprice-95d4` | `66e5dde011824441326d35178bb4ddd07d8d61d9` | `f8c9bec2b`, `3cfdb7f41` |
| #1246 | `cursor/rec-step2-95d4` | `d75fbf42b3ddd08d161138cac731014392ed7d60` | `4d6acbd03`, `66e5dde01` |
| #1284 | `cursor/rec-step3-95d4` | `42cb295780cc83f110f81eb14305e31f03d703e2` | `c8aa2cb5c`, `d75fbf42b` |

- **Resolutions.** Each conflict was taken byte for byte from the tip-67 train's merge of the same PR, which is exact
  because main equals tip 67 under `tools/circuit_check` and the sidecars. Each new tree equals
  `merge-tree(<train merge>, 327ea5b1b)`.
  - #1081 (`pins.json`, `targets.py`): from `8b68473e9`. The Gf pins move to `gf2k.circuit-check.json`, and the gf2k
    import and `_gf2k_roots` are added.
  - #1245 (`targets.py`): from `e04f04791`. Adds `rec_open` and `_rec_roots`, plus `verity_flock` in
    `sidecars.PACKAGES`, which #1163's test requires once `RecOpen` is registered.
  - #1246 (`pins.json`, `targets.py`): from `840a69eaf`. The `InnerRepCheck_v1` pin goes to
    `rec_residuals.circuit-check.json`.
  - #1284 (`targets.py`): from `ae1277f80`. The RecOpen_v4 docstring goes to `rec_open.circuit-check.py`.
- **Locks.** None conflicted and none was re-recorded; no rec head touches a lock.
- **Suites** at `42cb29578` (`--quick`, run locally one at a time on a 15 GB VM; route 1 was ended at route 2's start, as
  asked):
  - passed: `research`, `verity`, `verity-catalog`, `verity-circuit-check` (85 passed), `verity-experimental`,
    `verity-numerical`, `primitives/circuits`, `primitives/commitments`, `protocols/accounting/work/pouw` and
    `verity-vllm`.
  - `verity-flock`: 561 passed. Its first run failed 9 tests in `test_lean_verifier.py` because those tests spawn a bare
    `python3`, and I had launched the suites with the venv's python instead of `uv run`.
  - `verity-lean-audit` was still running when the session was ended; the rest did not start.
- **Downstream.** Before route 2, all four stacked branches had one conflict, `pins.json`, from #1347's
  `InnerRepCheck_v1` to `_v2` rename. The fix is the train's resolution of #1347 (`e5d133680`).

## Route 2: main `e7b5caa89cc2` into the 13 stack heads

| PR | branch | new head | parents (first, second) |
|---|---|---|---|
| #1081 | `cursor/rec-algebra-95d4` | `7321d7b9b64282de8ab3bf5a4ef5bb7e7e952e44` | `3cfdb7f41`, `e7b5caa89` |
| #1245 | `cursor/rec-reprice-95d4` | `7b11dda7a603128b2d707a8fdba66ae8b20dfa8f` | `66e5dde01`, `7321d7b9b` |
| #1246 | `cursor/rec-step2-95d4` | `ee9bd56556c638ebf3476b5d8d501191daf504b2` | `d75fbf42b`, `7b11dda7a` |
| #1284 | `cursor/rec-step3-95d4` | `7988c7a3afd61a7d6ad504d005bad8bd30c38195` | `42cb29578`, `ee9bd5655` |
| #1315 | `cursor/outer-shape-95d4` | `5a184befaf293c8c9e53d243208a226c27ecf90e` | `cf13123be`, `7988c7a3a` |
| #1318 | `cursor/flock-plain-leaf-tags-95d4` | `1ab5ab89c9908a3a05268edb886dcf8ab7691895` | `4fad0750e`, `7988c7a3a` |
| #1347 | `cursor/vstar-register-coef-95d4` | `c35a427d1c367c62061d630e8cd677e9e31c8881` | `7304ab577`, `7988c7a3a` |
| #1270 | `cursor/zk-gateway-95d4` | `2980f95d568655d1ab70c320d1b5ce997f13a04d` | `2f2a58de5`, `c35a427d1` |
| #1343 | `cursor/firewall-release-95d4` | `5306c63bf4ae2839146f706c0d8387e9c495239b` | `3399b71f5`, `2980f95d5` |
| #1349 | `cursor/firewall-release-2-95d4` | `86bb4d202bd6d2fa3c245953b635b3d82b4d8d02` | `83a3f5f43`, `5306c63bf` |
| #1303 | `cursor/firewall-contract-741b` | `6fb5a5db0dc08fab25c26871d1209878c153c25a` | `ceb25c35a`, `2980f95d5` |
| #1323 | `cursor/firewall-contract-95d4` | `611a85b24014bfb81522588a526a60287143e188` | `7c965ddc5`, `6fb5a5db0` |
| #1339 | `cursor/firewall-outer-95d4` | `300baafe39d975da3e76e02845cfa91408907853` | `a1adb7a17`, `611a85b24` |

### Resolutions, compared with `merge-tree(<old head>, <new base>)` (check a)

- **#1081 and #1245:** one conflict, `tools/circuit_check/src/circuit_check/targets.py`, resolved as a union. #1388 on
  main added the `lms` import and `_lms_roots`, and each PR keeps its own (`gf2k` with `_gf2k_roots`; then `_rec_roots`).
  This is the only path that differs from merge-tree.
- **#1318:** one conflict, `backends/flock/verifier/lean/Flock/Tags.lean`, resolved as a union. #1318's
  `leafSchemePlain`, `withPlainLeaves`, `plainLeaves` and `circuitPlainLeaves` go next to #1383's `coinDerivation`
  changes, and `all` lists both sides' tags. `verity/Security/lean-audit.json` also differs from merge-tree's text: the
  lean-audit merge driver (`tools/lean/merge.py`) merged it, and the only difference is that `"four_names"` moved to the
  end of its object.
- **#1347:** one conflict, `tools/circuit_check/src/circuit_check/pins.json`. Resolved as the new base's `pins.json`,
  with the `InnerRepCheck_v1{S={046a3fe0d3f7}}` to `_v2` rename applied in
  `backends/flock/python/verity_flock/rec_residuals.circuit-check.json`. That sidecar is identical to the train's
  `e5d133680`.
- **The other nine:** clean, and identical to merge-tree.
- **Nothing lost:** a pins-and-roots union check over all 13 merges loses no pin and no root function from either parent.
  The `migrate_bindings.py --verify` runs exit 0 at #1349 and #1315 (runs below).

### `Tags.lean`: does a tag #1318 adds name SHA-512?

Yes, by inheritance. #1318 adds one tag:

```lean
def circuitPlainLeaves : Tags := { circuit.withPlainLeaves with name := "verity/flock-circuit+plain-leaves" }
```

`withPlainLeaves` overwrites only `leaf_scheme` and `hashes.merkle`, so the tag keeps `circuit`'s identity. After #1383,
that identity's `hashes.coin_derivation` is `"sha512 (verity.randomness)"`, through `identityHidden`'s new default. The
merged prover agrees: `flock-circuit.rs` writes the same `coin_derivation` for every statement. #1318 writes no
`coin_derivation` field and no circuit-identity field of its own. The resolution needed no choice beyond the union.

### Check b: merging with ci's tip 84

All 13 new heads merge with tip 84 (`a42083c10ee9`, `origin/cursor/train-prep-84-on-062e72525-4292`) with no conflicts.
The same holds for the new main `e255a4efb`, which has the same tree.

### Locks

- **The nine heads whose Lean and locks equal main's** (#1081, #1245, #1246, #1284, #1315, #1347, #1270, #1343,
  #1349): unchanged. These merges change no lock and no Lean outside the tests' `backends/flock/tests/lean/*.lean`.
- **`backends/flock/verifier/lean`:** unchanged after `audit.py --build --update` with kernel replay.
  - #1303: `r20261006-234717-a06d` (PASS; 5753 declarations replayed, 68 skipped).
  - #1318: `r20261006-234656-36f6` (PASS, 5566 declarations, 7 guarantees; 5498 replayed, 68 skipped).
  - #1323: `r20261006-234706-01e3` (PASS, 6176 declarations, 14 guarantees; 6107 replayed, 69 skipped).
  - #1339: its Lean and locks equal #1323's.
- **`verity/Security` (which covers `Proofs`) at #1318 and #1323:** unchanged; nothing to commit on #1318, #1323 or
  #1339. Each ran `python3 tools/lean/audit.py --build --update --owner @proofs --no-runs verity/Security` with kernel
  replay, at `--mem-gb 192`. Both PASS: `Proofs` has 58918 declarations in 929 modules (58322 replayed, 310 skipped),
  and `verity/Security` has 6958 declarations and 1705 guarantees (6879 replayed, 79 skipped).
  - #1318, `r20261007-020414-3a47` (`art:3c71a100ce4229ad18387994a58c79aa112c21a3601445af5602304b5ca01ef1`): the
    written lock is equal to the head's as JSON, so no guarantee, read or other record changed. Its bytes differ only in
    where the top-level `"four_names"` sits: the merge driver had moved it to the end. The audit logged
    "rewritten under today's names and layout, saying what it said". `check` compares parsed records, so I did not
    commit the layout-only rewrite; the train's merge driver would reproduce that key order anyway.
  - #1323, `r20261007-020430-2af4` (`art:bdaeed234d16cc998434dca3aaeaa8119969eb631069e79eb60a536e4d7a9445`): the
    written lock is byte-identical to the head's, which is main's. #1339's `verity/Security` and Flock Lean equal
    #1323's.
  - Two earlier rounds died of memory and recorded nothing. Both named `verity/Security` and `verity/Security/Proofs`,
    which `audit.py` audits concurrently, so `Proofs` was audited twice at once.
    - At 40 GB: `r20261006-234656-36f6`, `r20261006-234706-01e3`.
    - At 128 GB: `r20261007-010113-fa89` (`art:d6449d40…`), `r20261007-010131-ad21` (`art:01d8c498…`).
  - The single-package runs peaked at about 170 GB, during `Proofs`' replay.

### Suites (check c), at the final heads, on vy-nebius-1

Each head ran `uv run tools/check/suites.py --quick --changed e7b5caa89 --jobs 6`.

| head | run | suites | passed | failed |
|---|---|---|---|---|
| #1349 `86bb4d202` | `r20261006-234411-4830` | 25 | 22 | 3 |
| #1339 `300baafe3` | `r20261006-234435-2fdb` | 26 | 23 | 3 |
| #1315 `5a184befa` | `r20261006-234458-5483` | 25 | 22 | 3 |
| #1318 `1ab5ab89c` | `r20261006-234522-8c79` | 26 | 23 | 3 |

Every run fails the same three suites, and none of the failures comes from the merges:

- **`verity-flock`:** `lake build` failures in a fresh clone, caused by six xdist workers each starting the first build
  of `backends/flock/verifier/lean`. Each head was re-run with that package built first, and all four pass with 0
  failures:
  - #1349: `r20261007-004655-520d`, 622 passed.
  - #1339: `r20261007-004706-5712`, 626 passed.
  - #1315: `r20261007-004717-d82f`, 553 passed.
  - #1318: `r20261007-004728-61e2`, 549 passed.
- **`research`:** `test_remote_cwd.py::test_two_concurrent_runs_of_one_commit_do_not_share_a_cwd` fails inside a
  research run.
- **`verity-tc-probe-fp4`:** `test_lean_vectors_poison_no_write_control_and_collect` fails inside a research run.
- The stack changes no file under `tools/research` or `tools/tc_probe_fp4`, and both tests pass locally at #1318's head.

### circuit-check on the rec targets (check c)

- **#1349, `r20261007-001009-057a`:** `migrate_bindings.py --verify` exit 0. Six targets, all ok with 0 failures:
  `GfScale_v1{L=2}`, `GfResiduals_v1{S={5649ec091c4b}}`, `RecOpen_v4{LANES=8,H=1}`, `InnerRepCheck_v2{S={046a3fe0d3f7}}`,
  `Gf128Mul_v1` and `Gf256Mul_v1`. There are warnings only (redundant-gates/ir): 2059 in `GfScale_v1{L=2}` and 16538 in
  `RecOpen_v4`.
- **#1315, `r20261007-001022-43b0`:** `migrate_bindings.py --verify` exit 0. Five targets ok: the Gf ones and
  `InnerRepCheck_v1{S={046a3fe0d3f7}}`. The sixth target, `RecOpen_v4`, was my mistake: that lineage has `RecOpen_v3`.
  Re-run as `r20261007-004903-9440`: `RecOpen_v3{LANES=8,H=1}` ok, with 0 failures and the same 16538 redundant-gates
  warning.

## Disk

On the agent VM I deleted only what I created: route 1's pytest temp dirs `pytest-881` and `pytest-882`. I also killed
my own local circuit-check run (by PID), which was using about 14 GB of the 15 GB VM; circuit-check then moved to node 1.
