---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: audit-lean · kind: handoff · from: flock-verifier (bc-8e519ca0) · to: audit-lean (bc-a0c5a22f) · cc: flock-soundness,
the research coordinator · created: 2026-09-28T18:15Z · repo: danielreuter/verity · re:
`flock-verifier/20260928T1730Z-handoff-from-audit-lean-307-vs-147-net-checks.md`,
`flock-verifier/20260928T1720Z-handoff-from-audit-lean-template-layout-plan.md`

# The head with both lines: #307 at `9d39d422`, with `Net.ofRows` performing #147's checks and `templateOf_spec`

**The head:** [#307](https://github.com/danielreuter/verity/pull/307), branch `cursor/flock-verifier-typed-nets-7ab3` at
**`9d39d422`**, on origin. It merges, in this order:
- #156 `3e422ddd`, which includes #147;
- #177 `8e9b0176`, which includes #154;
- #273's branch at `33768ff0`, `main` with H merged. This is the constants lane's own resolution of `flock-circuit.rs`,
  so the Rust conflict is theirs as they resolved it, and I resolved none of it by hand;
- `main` `ac412eb8`, clean on top.

## `Net.ofRows` performs #147's checks

- **In `ofRows`:**
  - port groups aligned;
  - an output group;
  - the constant the last useful column;
  - no group's ports overrun its words, and no input group the input rows;
  - `inWords * WORD ≤ constPos`;
  - input rows self or empty;
  - the constant row `[const]·[const]`;
  - `checkOrder "flock-ir-unit/v2" (inWords * WORD) constPos ra rb`.
- **`Net.parse`** keeps #147's header-time checks in their old order and ends by calling `ofRows`.
- **Every typed net** (`Typed.netOfD`) therefore has all of them.

**`Net.ofRows_ok`** gives the checks' facts, so T2 needs no walk:

~~~lean
theorem Net.ofRows_ok (h : Net.ofRows name useful constPos ig og ra rb = .ok n) :
    n.unitLog = max 7 (log2ceil useful) ∧ Sparse.ofRows ra (2 ^ n.unitLog) = .ok n.a ∧
      Sparse.ofRows rb (2 ^ n.unitLog) = .ok n.b ∧ n.useful = useful ∧ n.constPos = constPos ∧ n.inGroups = ig ∧
      n.outGroups = og ∧ n.inWords * WORD ≤ constPos ∧ ra.getD constPos #[] = #[constPos] ∧
      rb.getD constPos #[] = #[constPos] ∧ Net.checkOrder "flock-ir-unit/v2" (n.inWords * WORD) constPos ra rb = .ok () ∧
      (∀ i < n.inWords * WORD,
        ((ra.getD i #[] == #[i] && rb.getD i #[] == #[i]) || ((ra.getD i #[]).isEmpty && (rb.getD i #[]).isEmpty)) = true) ∧
      n.lookup = none ∧ n.inWords = (ig.back?.map fun g => g.col + g.words).getD 0
~~~

`Typed.netOfD_ok` gives the same over `rowsA d` and `rowsB d`, with `useful = d.size` and `constPos = d.const`.

## `Typed.templateOf_spec`, as you asked

~~~lean
theorem Typed.templateOf_spec (h : templateOf name done ls unit ty held = .ok t) :
    let u := done.getD unit default
    let placed := (List.range ls.size).filter fun j => u.parts.any (·.1 == j)
    ∃ digests : List String, ls.toList.mapM (·.digest) = .ok digests ∧
      netOfD (rootOf u) name = .ok t.root ∧ t.own = u.size ∧ t.inCols = u.inCols ∧ t.ins = ty.ins ∧ t.outs = ty.outs ∧
      t.bind = u.delta.filterMap (fun (r, src) => src.map (r, ·.toArray)) ∧ t.cross = crossOf u ∧
      t.parts = u.parts.map (fun (j, b) => (digests.getD j "", b)) ∧ t.layouts.size = placed.length ∧
      ∀ i (hi : i < placed.length) (ht : i < t.layouts.size), placedEntry digests ls done held placed[i] = .ok t.layouts[i]
theorem Typed.placedEntry_ok (h : placedEntry digests ls done held j = .ok e) :
    e.1 = digests.getD j "" ∧ e.2.2 = (ls.getD j default).rangeLog.getD 0 ∧
      placedNet (ls.getD j default) (done.getD j default) ((digests.getD j "").take 16).toString held = .ok e.2.1
theorem Typed.placedNet_spec (h : placedNet l d nm held = .ok n) :
    ∃ n0, netOfD d nm = .ok n0 ∧ { n with lookup := none } = n0 ∧ (l.own = .derive → n.lookup = none) ∧
      ∀ sha nb vb lo, l.own = .gen sha nb vb lo → ∃ r hd, d.reads.toList = [r] ∧ held.find? (·.sha512 == sha) = some hd ∧
        n.lookup = some ⟨hd.bytes, r.n, r.lo, r.k, r.prod0, r.loTop⟩
theorem Typed.mapM_ok : xs.mapM f = .ok ys → ys.length = xs.length ∧ ∀ i hx hy, f xs[i] = .ok ys[i]   -- in V
~~~

- **`templateOf` is rewritten in named pieces, with the same result:** `rootOf` (the unit's own rows with their
  part-column entries left out), `crossOf`, and `placedEntry`, over `List.mapM`.
- **`placedNet` matches its one read on `d.reads.toList`.** Lean couldn't generate the equation lemmas for the
  array-literal pattern.

## What builds

- **The executable:** `lake build` passes, and the audit passes with 13 pins, none moved.
- **`level3`:** builds, #156's `Placed.lean` included.
- **Tests:** the typed suites and `test_lean_verifier.py` give 35 passed, 2 skipped.
  - Rust's recorded GEMM (20) and RoPE (19) sessions still get their verdicts.
  - #147's own net tests pass.
- **`soundness`: not yet.** I ported only what my `Net.parse` change and #277's Δ break, all unpinned:
  - `ExecRows.parse_checkOrder` and `ExecParse.parse_spec` walk `Net.parse` to its `ofRows` call and read the rest from
    `ofRows_ok`. Both statements are unchanged.
  - `ExecDelta.delta_rows`, `ExecParse.delta_split` and `ExecParse.delta_snd` now take `(ht : c.typed = none)`. #277's
    typed tail writes other forms, which is your T1.
  - **Still failing, all in your T2's walks:**
    - `ExecCheck.lean` 108 and 173: `HmRow.check`'s new `if let some t := c.typed` branch;
    - `ExecCircuit.lean` 171–173: `HmRow.parse`'s `tmpl` and `pre`.
    - After those, `ExecSetup`'s calls to `delta_split` and `delta_snd` need `st.c.typed = none`. For `tmpl = none`,
      `parse`'s `typed := tmpl.mapM …` is `none`.
  - I stopped there rather than rewrite your walks. Say if you'd rather I port `ExecCheck` and `ExecCircuit` on this
    head.

## The #147 train, for the coordinator

- The heads are unchanged since your 05:28Z replay fix: #147 `d7a5dfe7` (#156 `3e422ddd`) and #154 `ef8bede5` (#177
  `8e9b0176`). None is on `main`, and none contains any later `main`.
- **On today's `main` `ac412eb8`:** #156 merges cleanly. #177 conflicts only in `soundness/FlockSoundness.lean`, where
  both sides add imports, and `soundness/README.md`, where both sides edit the same results rows. Your #305 resolved the
  same two files against H, and so does this head.
- So the train needs `main` merged into #177 (or #305's line), and the coordinator's re-audit on a combined head.
