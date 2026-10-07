---
id: red-team-1179/20261007T0410Z-finding-pr1179-restack
campaign: public-inputs
lane: red-team-1179
kind: finding
status: final
repo: verity
origin: 6385e543bf4052651c63eb6a6b60826da38af0eb
---

# Red team: PR #1179 (S1, fail-closed verifier), restacked at 6385e543b

GRANT at `6385e543bf4052651c63eb6a6b60826da38af0eb` (`cursor/verifier-fail-closed-95d4`). The earlier grant
(`note:proofs/20261005T1330Z-finding-red-team-1179`, at `d7a0aca74`, carried to `fe0b6f9d9`) holds through the layout
move and main's movement. Nothing blocks.

## 1. Own patch, then and now

- I reran the restack by hand: merge base, `tools/move/lean.py`, then a merge onto main. `d6fa7eff9` equals the
  merge-tree's clean result. `ae78dd9f0` reproduces exactly (tree `fe5dbf19e`).
- `cf08dc800` differs from the merge-tree result only in the four hand-resolved files, and each resolution is right:
  - `test_lean_zk.py` keeps main's `STATEMENT = "verity/flock-circuit@f5df3bbc+seed-injection"` and adds the branch's
    `DRAWLESS`.
  - `Composed/DefsJ` and `ZkHidden/DefsJ` keep main's docstrings, which cite `setupZJ_of_acceptsZK` and
    `setupZHJ_of_acceptsZK`. Those lemmas exist, so the docstrings are true, though narrower than the branch's.
  - `Headline.lean` keeps main's wording plus the branch's sentence.
- Modulo the path map, the patch is the same then and now. The only differences are:
  - the `ASSUMPTIONS.md` rewording;
  - ten J-form files that main landed identically;
  - the DefsJ docstrings;
  - the `moves.json` path entries;
  - `benchmarks/pouw/hidden_zk` (item 3);
  - the locks (item 4).
- No proof line and no refusal line was dropped.

## 2. Main moved under it: no escape

- The verifier at head is the granted verifier plus main's docstrings, instance names and the four `@f5df3bbc` tags.
  - The untyped `@f5df3bbc` tags fall under the generic theorem.
  - The typed ones fail `statementRules` (`!typed`).
  - On main, the model files changed only in docstrings.
- Every item on the body's refusal list is a line of code:
  - `ProvedScope.statementRules`: hm96 rows, untyped, retained rounds, the leaf rule, `zk || count ≤ 1`, no
    `--public-inputs`.
  - `check`: the circuit parse, the public load, no shared rows, `scopeOk` (one input group, `outNet == unitNet`,
    `unitLog ≤ 32`, `portReadsB`, `v1Ports`).
  - `drawLaw`/`lawWhy`: stratified always, subset only under `--zk`, bernoulli and work refused, unparsable draws
    refused, draw-less refused (D12).
  - `Zk.maskFree`, called from `shapeOk`.
  - `HmRow.check`'s `vus_per_block` power-of-two guard.
- `verifyCmd` builds the setup first, then runs `shapeOk` under `--zk` and `drawLaw` for a drawn session. The verdict
  requires files, `checkFresh`, `verify`/`Zk.verify`, `scope`, and `drawLaw` for a draw-less session.
- Only `verify` prints VERDICT lines. I found no form main's `verify` accepts that S1 neither refuses nor covers by
  `FailClosed.flock_verify_sound`.
- Rust `proved_scope.rs` is unchanged from the granted patch, and the old caveat still applies: it refuses the same
  forms only among those a live build can write, and it keys public inputs on circuit ports rather than the flag.

## 3. `47c991ac6` (hidden_zk)

- It does what the body says. Under `benchmarks/pouw`, it touches only `hidden_zk/summarize.py` (the `REFUSAL` string,
  and `lean(d, refused)` for every role except tile and hidden) and one header line of `hidden_zk/job.sh`. Tile
  judgement is unchanged, and `tests/test_hidden_zk_summarize.py` passes (2 passed).
- Non-blocking: tile and hidden checks run on `serve --zk` sessions with no `--draw`. With no `--draw` or
  `--draw-file`, `serving()` writes a draw-less session.
  - Under S1, `honest-own` and `st-honest` therefore get D12 and fail `summarize.py`'s ACCEPT expectation.
  - A simulation of `summarize.py` on S1's verdicts gives
    `tile {'honest-own': ('ACCEPT','REJECT',False), 'st-honest': ('ACCEPT','REJECT',False)}`. The row roles are all
    REFUSED and pass.
- The smallest fix is to draw those sessions (a `--zk` subset draw of every unit), or to judge the D12 refusal like
  `REFUSAL` for the honest checks.
- The body's consumer list omits two scripts that run the same draw-less sessions:
  - `benchmarks/pouw/served_zk/job.sh`, the verdict of record (`served_commit.py`'s `lean_verdict`), which expects
    `lean-u$t`, `lean-filler` and `lean-st-honest` to ACCEPT;
  - `backends/flock/pod/86-zk-cpu-steps.sh`, which only records.
- No test covers `summarize.py`'s new row branch.

## 4. Records

- Diffed against main's lock:
  - Guarantees: 36 new `FlockSoundness.Discharge.FailClosed.*` (owner @proofs), none removed, no statement changed.
  - Changed definitions: exactly `Flock.HmRow.check`, `Flock.Zk.shapeOk`, the new `Flock.Zk.maskFree`,
    `ZkHidden.DrawSetupZHJ` and `ZkLink.DrawSetupZK`.
  - Digest changes: `Flock.HmRow`, `Flock.Zk`, `ZkHidden.DefsJ`, `ZkLink.TablesAt`. Of the remaining entries, 221 only
    add readers, and there are 3 new read modules.
- The Proofs lock parses equal to main's, and the verifier lock is unchanged.
- Audit `r20261007-000151-97e1` at tree `cf08dc800` passed all three packages with the body's numbers. One cosmetic
  point: the run named both `verity/Security` and `verity/Security/Proofs`.

## 5. Rec tip `4db330f53` (main + #1318 + #1349 + #1339)

S1 merges onto the tip with conflicts only in `PROTOCOL.md` and `README.md`.

(a) Does any form the tip makes `verify` accept escape both S1's refusals and the theorem? No.
- The tip's `circuitPlainLeaves` is refused twice: by its own `tags.plainLeaves` exit 2, and by S1's leaf rule.
- `Setup.openedSalts` changes `saltLen` only when `saltBytes = 0`, and hm96-sha512/v1 has 192 salt bytes.
- `verify` gains no form.

(b) Which tip tests, sessions or vectors that expect a Lean ACCEPT would S1 refuse?
- `backends/flock/tests/test_rec_algebra.py::test_the_lean_verifier_rejects_exactly_the_mutations_with_a_nonzero_residual`.
  - Its cases `honest` and `m10` (`("msg", 27, 0, 0)`, expected `[]`) assert `accepted`.
  - S1 answers "refused: a unit reading 2 input groups: a statement form the soundness proof does not cover"
    (`flat/gemm-coordinate`, as in S1's `test_lean_hidden_outputs.py`).
- `backends/flock/pod/80-rec-inner.sh`: its honest `verify --coins os` runs on the rec proxy's session, which has
  `unit_draw: None` (draw-less), so S1 gives D12. The script only records the verdict.
- `backends/flock/pod/81-rec-outer.sh` and `83-rec-alg.sh`: their honest `verify --zk … --registered` runs on
  `serve --zk` sessions with no `--draw`, so S1 gives D12. Their `summary.json` records the verdict.
- `85-rec-reprice.sh` runs on plain leaves, which the tip already refuses. `test_rec_outer.py`,
  `test_rec_residuals.py` (they use `statement` only) and `test_lean_plain_leaves.py` are unaffected.

(c) Does the firewall add a separate command whose acceptance the one theorem should cover? No.
- `flock-firewall` (its default program and `contract`) is a separate executable, and it accepts no proof.
- `contract`'s verdict on a `verity/firewall-transcript/v0` session means what `Contract.holds_*` state: every item
  may leave and the session ends in `finish`.
- It is outside `flock_verify_sound`. The post-tip body should say so in one line.

## Non-blocking points for the body

- Add the consumers S1 breaks that the body omits:
  - hidden_zk's tile and hidden honest checks (D12 against `summarize.py`'s ACCEPT expectation);
  - `benchmarks/pouw/served_zk` (verdict of record);
  - `backends/flock/pod/86-zk-cpu-steps.sh`;
  - after the tip, `test_rec_algebra.py` and the rec pod scripts 80, 81 and 83.
- Say that Rust `proved_scope` refuses the same forms only among those a live build can write (public inputs keyed on
  circuit ports).
- Add a test of `summarize.py`'s row branch.
- Note that main's DefsJ docstrings now cite `…_of_acceptsZK`, which is narrower than the branch's wording but true.
