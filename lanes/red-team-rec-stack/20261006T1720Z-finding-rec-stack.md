---
id: red-team-rec-stack/20261006T1720Z-finding-rec-stack
campaign: proofs
lane: red-team-rec-stack
kind: finding
status: final
repo: verity
origin:
  - pr:1081@845827f20af0aed7bd83dc9f332f52a7dd965db0
  - pr:1245@f8c9bec2bd73f002c47beb8a921d31c863eb7301
  - pr:1246@4d6acbd03d464096c0418532cf1b4e8c269155b2
  - pr:1284@c8aa2cb5c0a9ff13387908e985be338aef05893e
  - pr:1315@cf13123be4cb03cbb1950aab574aae63b5e6d238
  - pr:1318@4fad0750ec24be401e0141f822f6872e37a5dd31
  - pr:1347@7304ab577abe260f8375bff678a40cbcc2ed9092
---

# Red team, the recursion's stack (#1081 → #1245 → #1246 → #1284, and #1315, #1318, #1347 on it): GRANT all seven

Reviewed by red-team-rec-stack for the proofs coordinator on 6 Oct, 17:09Z to 17:25Z (labels at 17:11Z and 17:20Z, all seven on both stores). Nothing blocks. All seven heads
are the branch tips as of 17:10Z. I ran one probe run (`r20261006-171624-2031`, vy-nebius-1, `--cwd clone` at
`c8aa2cb5c`) and read the rest from git and the store.

| PR | head | verdict | how |
|---|---|---|---|
| #1081 | `845827f20` | GRANT | review |
| #1245 | `f8c9bec2b` | GRANT | review |
| #1246 | `4d6acbd03` | GRANT | review |
| #1284 | `c8aa2cb5c` | GRANT | review |
| #1315 | `cf13123be` | GRANT | Q5 carry from `e3f7a643a` (`note:red-team-outer-shape/20261006T0820Z-finding-red-team-outer-shape`) |
| #1318 | `4fad0750e` | GRANT | Q5 carry from `3c3b4267a` (`note:red-team-plain-leaves/20261006T1507Z-finding-pr1318-restack-regrant`) |
| #1347 | `7304ab577` | GRANT | Q5 carry from `a106e15b8` (`note:red-team-vbridge-e/20261006T1236Z-finding-1347`) |

## 1. Q5 carries

The own patch is `git diff $(merge-base PARENT HEAD) HEAD`, and I compared it file by file as its `+`/`-` lines without
`@@` line numbers.

- **#1318:** the patch at `3c3b4267a` over `77acebf9d` and at `4fad0750e` over `c8aa2cb5c` is identical in all 9
  files, `verity/Security/lean-audit.json` included.
- **#1347:** the patch at `a106e15b8` over `77acebf9d` and at `7304ab577` over `c8aa2cb5c` is identical in all 10 files.
- **#1315:** the patch at `e3f7a643a` over `273017068` and at `cf13123be` over `c8aa2cb5c` is identical in all 4 files.
  `research.queue.carry` does not carry it, contrary to the brief. Against `origin/main`, the stack's whole change
  differs. Against `c8aa2cb5c`, the before-blobs of `class_statement.py` and `rec_vstage.py` differ, because the restack
  changed them under the patch. So I labelled it under Q5 like the other two.

## 2. Review of #1081–#1284

**The verifier of record is unchanged.**
- `git diff --name-only f5df3bbc5 c8aa2cb5c` touches nothing under `backends/flock/verifier/` and no `lean-audit.json`,
  lakefile or manifest. All five `lean-audit.json` files are byte-identical.
- The only Lean files are `backends/flock/tests/lean/InnerClaims.lean` (#1081, #1245) and `InnerFold.lean` (#1246,
  #1284). They are `lean --run` test scripts that `import Flock`, outside any Lake package. So no Lean audit is needed.
- The Rust and CUDA changes are prover-side:
  - #1246 raises `max_extra` and `MAX_EXTRA_CLAIMS` from 64 to `2 · IN_RANGE_REGIONS` = 2,048. The constant
    `IN_RANGE_REGIONS = 1024` is already on `main`.
  - #1246 adds `FC_ZK_SELF_CHECK`: unset or `stop` is the default, and any value other than `stop` or `skip` is refused.
  - #1284 adds the `merkle()`/`salted()`/`pcs_of()` plumbing and the `decode_with(salted)` fix.
  - #1284's `Composite` check also lets the Rust serve verifier accept `flock-leaf/sha512-unsalted`, ZK off and the
    SHA-512 build only. `--zk` refuses it. The Lean verifier of record is untouched; #1318 adds its tags.

**What VBridge restates.** These are the only differences from the commits VBridge restates.
- **`rec_open.py`**, restated at `273017068` (blob `1a1182d6`, the same as `d23edf42d`), is blob `55486e0d` at
  `c8aa2cb5c`. The only change is two docstring lines, "the gateway" → "the firewall", from the layout move's
  `rename.py` (`a3312e653`). No code changed and no line moved.
- **`rec_residuals.py`**, restated as blob `6984e566` in #1272, is blob `6a63c745` at `4d6acbd03` and `c8aa2cb5c`. The
  only change is `G.check_structure(S)` plus a blank line at the top of `residual_forms`.
- **`gf2k.py`**, restated as blob `52383dd2`, is blob `45880e0f` at all four heads. The only changes are
  `check_structure` (new), its calls in `residuals` and `_res_sig`, and `__all__`.
- **The check only refuses.** `check_structure` returns `None` and never mutates S. My probe built 14 circuits and
  values with the check and again with it stubbed out, for the test S, SMALL, circuit-check's S and an edge S
  (`["wt", nw − 128, 127]`, `["w", nw − 1]`). All 14 are identical:
  - `GfResiduals` program digests;
  - `residual_forms` form fingerprints;
  - `residuals` values;
  - the `InnerRepCheck` digest and `unit_circuit`.
- **The pins are unchanged.** The S-check commits `845827f20` and `4d6acbd03` leave `pins.json` and the gf2k test's
  `PINS` table alone. `test_pinned_counts_and_digests` passes at `c8aa2cb5c`. Circuit-check at `845827f20`
  (`r20261006-162729-7151`) reports 4 targets and 0 failures.

**It fails closed.**
- The authors' negative tests pass at `c8aa2cb5c` (16 passed with `-k "out_of_range or missing_operand or wrong_length
  or pinned"`, in `r20261006-171624-2031`).
- Each of my probes was refused with a `ValueError`, through each entry point:
  - **`check_structure`:** `["w", True]` (a bool) and `["wt", 3, 0]` at `nw = 130` (one element past the end). The edge
    S is accepted.
  - **`residuals`:** `["v", 4]` in a residual's `add` (the authors' tests only put bad terms in `ops`), and `nw = -1`.
  - **`GfResiduals`' signature:** the product `[-1, 0]`, which would otherwise index from the end, and the 3-tuple
    `[0, 1, 2]`.
  - **`residual_forms`:** #1272's truncation case (`nw = 2`, `add [["w", 5]]`), which used to return 128 bits for 2
    residuals, and `["wt", 0, -1]`.
  - **Via callers:** `unit_circuit` with `["w", 130]` in `add`, and `RR.definition` with `["v", 3]`.
- Every S path in `rec_residuals` goes through the check: `residual_words` calls `G.residuals`, `_body` calls
  `GfResiduals` (its signature), and `unit_circuit` calls `residual_forms`. `rec_open._steps` reaches it through
  `residual_forms`.

**The bodies' claims hold at the heads.** Exceptions are under the notes.
- AND counts: 2,187, 6,561, 4,374 (GfScale at L = 2), and `InnerRepCheck_v1{S={046a3fe0d3f7}}` at 2,187. All are in
  `pins.json`.
- #1245's fixture change is only the recorded sha256 of `InnerClaims.lean`.
- #1284's "25 against 29 compressions": LANES/8 + 1 + 2H = 25 at LANES = 64, H = 8.
- #1284's GATE-REFUSED line appears for both forged copies in `r20261006-021550-4e4b`, which ran at `273017068`.
  `r20261005-221419-ad0a` exists and exits 0 at `d3f9d15b8`.
- The landing evidence: `r20261006-165529-a10c` at `c8aa2cb5c` has 88 passed and 1 opt-in skip
  (`VERITY_FLOCK_INNER_FOLD`), slow tests included.

**The merges are clean.** `git merge-tree --write-tree` of every head onto its parent and onto `origin/main`
`cb50af5e8` gives no conflict, and each merge onto its parent reproduces the head's tree.

## Non-blocking

- **The base.** The stack sits on `main` `f5df3bbc5`, not `cb50af5e8`. `cb50af5e8` is today's `main`, 26 commits on.
  Every head still merges cleanly onto it.
- **#1081's body.**
  - Its paths are from before the layout move: `verity.ml.boolean.gf2k` is now `verity_catalog.definitions.boolean.gf2k`,
    `verity.ir.refs` is now `verity.primitives.circuits.refs`, and `tests/ir/test_refs_take.py` is now
    `verity/primitives/circuits/tests/test_refs_take.py`.
  - It doesn't mention the S range check, and its circuit-check citation predates `r20261006-162729-7151`.
- **#1246's body** doesn't mention `residual_forms`' S check (`4d6acbd03`).
- **#1284's body** gives its head as `273017068` and still says "gateway" where the code now says "firewall". The pinned
  `use` strings rightly keep "gateway".
- **VBridge's Lean citations have drifted** (#1272, #1283, #1353 and their Lean in
  `verity/Security/Proofs/Flock/VBridge/Residuals.lean`). Its docstrings cite `rec_residuals.py:298–338` and `gf2k.py`
  lines past 246, which now sit 2 and 31 lines lower. The code is the same.
- **Friction: `research.queue.carry` lags Q5.** It compares (before, after) blobs, so none of #1315, #1318 and #1347
  carried, and each needed a manual relabel that caught nothing. Comparing each file's `+`/`-` lines, as this note
  does, would make Q5 automatic.
