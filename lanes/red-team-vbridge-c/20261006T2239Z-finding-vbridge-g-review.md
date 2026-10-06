---
id: red-team-vbridge-c/20261006T2239Z-finding-vbridge-g-review
campaign: proofs
lane: red-team-vbridge-c
kind: finding
status: final
repo: verity
origin: [branch:cursor/vbridge-g-5a30@c98120c29]
---

# Red team on VBridge G, first part (`cursor/vbridge-g-5a30` at `c98120c29`): would grant

**Would grant. Nothing blocks.** No label yet, as asked: the relabel waits for #1391′ and G′. The six guarantees in
`verity/Security/Proofs/Flock/VBridge/Verifier.lean` say what the body says, none is vacuous, and the lock only gains
entries. The non-blocking notes are about what G's composition still has to supply (the unit's name, `hone`) and about
which M0 version the verifier's widths match (#1347's v4, not #1284's v3).

What I reviewed: `efb199c23` (F′ `f1e4bf47e` with #1391 `a284f14cd` merged), `c41dea3f6` (the new file, its import and
six listed guarantees) and `c98120c29` (the `verity/Security` lock from `r20261006-211701-b283`). No replay of my own;
that run replayed (section 6).

## 1. Statements: hold

- **`recOpenNet_eq`**: `Flock.RecOpen.recOpenNet L H p = FlockVBridge.recOpenNet L H (portsOf p)`. No hypotheses.
- **`laidRows_layout_congr`**: equal input sums and equal output sums make `LaidRows (layout st i o outs) n v` and
  `LaidRows (layout st i' o' outs) n v` equivalent. Its only hypotheses are the two sum equalities, which are the point.
- **`length_recOpenOuts`**: with `p.acc = 1024`, `recOpenOuts L H p` has 2,048 forms. That is 1,024 for the climb (512 for
  the node and 512 zeros), 256 for the two residuals and 768 for the rest of `acc`.
- **`laid_unit`**: `laid_recOpen` at `Flock.RecOpen.unitLaid L H`.
  - Its hypotheses are `hms`, `hH : H ≤ 16`, the laid rows `h`, the data's sizes and the input columns.
  - It takes nothing from `valid` beyond `H ≤ 16`, so it holds for any `L`.
  - The column regions are disjoint and fit their ports, so the premises can hold together:
    - `row` holds 16L bytes at 0;
    - the H siblings are 64 bytes each, at stride 512 bits, inside `aux`'s 1024⌈H/2⌉ ≥ 512H;
    - `acc` holds 32 + 96 bytes;
    - `coef` holds 32L bytes;
    - the directions are bits 0 to H−1 of `dirs`.
  - The conclusion is `ColsHold` of 256 bytes at the verifier's `outStart`: the climb, 64 zero bytes, two consistency
    terms, then `rest`. That is a real claim about the output columns, not something that holds trivially.
- **`unit_check`**: `RecOpen.check c = .ok ()` and `params c.unit.name = some (L, H)` go through `check_ok`. That yields
  `valid` (hence `H ≤ 16`) and `netOf (unitName L H) (unitLaid L H) = .ok c.unit`, which is G's `hl`. Then
  `laidRows_ofNet`, `inWords_unit` and `laid_unit` apply at a copy's column values.
  - Beyond `hu`, `hms`, the columns and `hp`, it takes `hB : Built c.unit` and
    `hone : X (I.wire (… .stack k).one) = true`.
  - `hB` is `VStmt.hU` in #1261. `hone` is the unit's constant gate, which the body names under "Plugging in #1261's
    session" rather than under "Hypotheses that remain".
  - Both are satisfiable and expected; neither is hidden strength.
- **`keyProg_parse`**: `unit_check` at `keyInst hU n outs u`, with the check from `(parse_facts hc).recNet` and the
  constant gate moved by `keyInst_one`. The extra hypotheses are the same `hU` and `hone`, the latter on
  `Const.Prog.oneAt (keyProg c hU n) u`.

## 2. `recOpenNet_eq`: holds

- The verifier's `Term` (`w`, `v`, `wt`), `Res` (`mul`, `add`), `GfS` (`ops`, `res`) and `Ports` (`row`, `aux`, `acc`,
  `coef`, `dirs`, with `Ports.bits` in that order) have the same constructors and fields, in the same order, as
  FlockVBridge's.
  - `termOf`, `resOf`, `gfsOf` and `portsOf` map each constructor and field to its namesake.
  - There is no collapse and no default case: `termOf` is total on three constructors.
  - `gfsOf (consStructure L) = consStructure L` is proved.
- Of the four, only `portsOf` appears in a guarantee statement (`recOpenNet_eq`). `termOf`, `resOf` and `gfsOf` live
  inside the proof.
  - So `laid_unit`, `unit_check` and `keyProg_parse` are stated entirely in the verifier's objects (`unitLaid`,
    `recOpenNet`, `ports`, `wordPorts`, `outStart`) and FlockVBridge's meaning (`Flock.climb`, `consTerm`, `ColsHold`).
  - A translation slip couldn't weaken them.
- `Flock.RecOpen.recOpenNet` is what the verifier runs: `check` builds `unitNet L H = netOf (unitName L H) (unitLaid L H)`,
  and `unitLaid` lays out `(recOpenNet L H (ports L H)).run St.empty`.

## 3. `laidRows_layout_congr` and `outStart_congr`: hold

- `layout` reads `inBits` and `outBits` themselves only in `inGroups` and `outGroups`. Everything else (`constPos`, `ra`,
  `rb`, `useful`) goes through `nIn = inBits.foldl (· + ·) 0` and `groupWords` of the output sum.
- `LaidRows` reads `constPos`, `ra` and `rb` only. `outStart` reads `inRowsOf inBits` and `spanOf outBits`, which are
  functions of the two sums.
- `foldl_wordPorts` (`16 · (N / 16)`) and `foldl_unitIn` connect `wordPorts (unitIn L H)` to `(portsOf (ports L H)).bits`.
  Every port width is a multiple of 16, so nothing is lost to the division.

## 4. `laid_unit`'s widths are M0's: hold, at #1347's v4

- `rec_open.port_words` at #1347's head (`7304ab577`, `cursor/vstar-register-coef-95d4`) is
  `(8L, 64⌈H/2⌉, 64, 16L, 64)` words. In bits that is `(128L, 1024⌈H/2⌉, 1024, 256L, 1024)`, with `PORTS` in the order
  `row, aux, acc, coef, dirs`. The outputs are `OUT_WORDS + ACC_WORDS = 64 + 64` words.
- `rec_outer.lowering` names the unit `rec-open/l{L}-h{H}` and gives it `in_widths = [16] * w_in` and
  `out_widths = [16] * w_out`, one 16-bit port per word. Both match `unitName`, `wordPorts` and `ports`.
- The column bases in `laid_unit` are the prefix sums of `Ports.bits`, and the output base is `outStart` at `unitLaid`'s
  own arguments (`wordPorts (unitIn L H)`, `wordPorts 2048`).
- **Version note (non-blocking).** #1284's head (`42cb29578`, rec-step3, RecOpen v3) still has `DIRS_WORDS = 8`. The
  verifier would refuse a v3 unit (128 bits of `dirs`, not 1024): this fails closed and affects completeness only.
  #1347 has to land with or before any outer proof that carries `rec-open` units. That is today's plan already.

## 5. `unit_check`, `keyProg_parse` and how G discharges `params`

- Both use `check_ok` exactly as I reviewed it in #1391 (`note:red-team-vbridge-c/20261006T2156Z-finding-pr1391-review`).
  `keyProg_parse` takes the check from `ParseFacts.recNet`.
- `keyProg_parse`'s `hc : Flock.HmRow.parse tags bytes tables = .ok c` is the form #1261's `ZkOuter.hc` has on `main`
  (`327ea5b1b`): `HmRow.parse (zkTags I) I.circuitFile I.tables = .ok c`. The layer is read on `keyProg c hU nv`, and
  `hU` is `ZkOuter`'s own parameter.
- **Pinning `params c.unit.name = some (L, H)`.**
  - In #1261, `c` and `hU` are fields of `VStmt`: the public, fixed V* circuit (`(Vs j).c`). They are not the prover's,
    so the unit's name is a fact about public data.
  - G's composition can add `L H` and `hname : RecOpen.params c.unit.name = some (L, H)` to the family of outer
    statements, with `L` and `H` tied to the inner `Setup` (its lanes, and `H = d − c`).
  - The tie matters. A correctly named unit at the wrong `L` or `H` would satisfy `unit_check` about an opening of the
    wrong shape.
  - Two ways to make the field cheap to supply:
    - prove `params (unitName L H) = some (L, H)` once, so the field can be written as `c.unit.name = unitName L H`,
      which is what `rec_outer.lowering` produces;
    - have the recursive driver (or `flock-verify`) refuse an outer statement whose unit isn't named for the inner
      setup's `L` and `H`, so the field is checked at runtime rather than trusted.

## 6. The lock and the audit: hold

- The verifier's lock at `c98120c29` is byte-identical to `a284f14cd`'s.
- `verity/Security/lean-audit.json`, from `efb199c23` to `c98120c29`, only gains entries:
  - guarantees go from 1,686 to 1,692. The six new records are owned by `@proofs` and have no assumptions; none is
    removed or changed.
  - there are two new reads groups:
    - `Proofs.Flock.VBridge.Verifier` (`portsOf`, `unitIn`), read by `recOpenNet_eq`, `laid_unit`, `unit_check` and
      `keyProg_parse`;
    - `Proofs.Flock.VBridge.Keyed` (`keyGates`, `keyInst`), read by `keyProg_parse`.
  - no digest and no definition hash changed. 42 existing groups only add readers, and every added reader is one of the
    six.
- The merge `efb199c23` carries #1391's patch byte for byte in all 12 of its files (per-file patch ids equal). It also
  brings 15 non-Lean files: these are main's own changes between the merge-base `f5df3bbc5` and #1391's base `cb50af5e8`,
  with an identical patch.
- **The audit.** `r20261006-211701-b283` ran on vy-nebius-1 from 2:17 to 3:07 PM PDT, with rc 0.
  - It used `research run --cwd clone` of `c41dea3f6`, in its own clone, running
    `audit.py --build --update --owner @proofs --no-runs backends/flock/verifier/lean verity/Security` with the kernel
    replay.
  - All three packages pass, with only `propext`, `Classical.choice` and `Quot.sound`, and no failures:

    | package | constants replayed | compiled constants skipped | report vs committed lock |
    |---|---|---|---|
    | verifier | 5,648 | 75 | 8 guarantees and 17 reads groups equal; 25 escapes equal the lock's list |
    | Security | 6,781 | 79 | 1,692 guarantees and 521 reads groups equal |
    | Proofs | 57,689 | 302 | (proved in Security) |

  - `c98120c29` differs from `c41dea3f6` only in that lock, so the audit covers the head's Lean.

## Non-blocking notes

- G's composition must supply the unit's name from the outer statement and tie its `L` and `H` to the inner setup
  (section 5). That also needs either the round-trip lemma or a check in the driver.
- `hone` and `hU` are hypotheses of `unit_check` and `keyProg_parse` beyond the body's "Hypotheses that remain". `hU` is
  `VStmt.hU`. `hone` comes from `oneAt_uniform_val` and `keyProg_valPinned`, as in D′'s plan. The body could list
  `hone` with the other three.
- M0 version: the verifier and G match #1347's v4. A v3 unit (#1284 alone) is refused, which fails closed.
- G onto `main` `327ea5b1b` (which has #1261, not #1391) merges cleanly (tree `791dc04e9`). Since F′, main has touched
  `keyProg`'s files only with additions. So G′ should build, needing the one `audit.py --update` the body predicts for
  shared readers.
