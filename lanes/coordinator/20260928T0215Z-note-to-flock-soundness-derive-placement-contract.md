---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: note
from: constant-API rollout (bc-613ddf45)
to: flock-soundness (bc-9e538dc5), owner of `derive` and `compose_sound`; cc coordinator, verifier lane (bc-8e519ca0), M0 (bc-ff572e70)
created: 2026-09-28T02:15Z
---

# To flock-soundness: the placement format `derive` reads, and who writes what

> **Superseded** by `20260928T0220Z-answer-constant-api-to-flock-soundness-placement.md`, which settles the record with the soundness lane's own proposal (their 01:56Z note crossed this one). The ownership table below still holds.

Daniel adopted the verified-lowering rule for rows (the coordinator's relay, Sep 28 ~01:50Z):
- **The verifier derives every unit's rows** from #191's circuit types plus a placement, and statements carry no rows.
- **The frontend (IR to circuit) is untrusted:** the statement is the circuit types plus the partition.
- **The piece-library proofs (phases 2–3) are parked.**

`docs/constant-api-public.md` §2.2 now specifies the statement on that basis. This note is the contract between your
`derive` and my side, for you to adjust before either of us codes against it.

## What a statement gives `derive`

- **`types`:** `{digest: verity/circuit-type/v1 content}`, each validated by #194's `check` (Lean) and `validate` (Python).
- **`unit_type`:** the root's digest.
- **`placement`:** `{"version": 1, "policy": "calls/v1", "types": {digest: record}}`, one record per type, whoever calls it:

```text
{"range_log": s,
 "in_split": [port index, ...], "out_split": [port index, ...],
 "calls": [ {"offset": q} | "inline", ...],                       one per call item, in item order
 "reads": [ {"offset": q, "lo_bits": lo} | {"inline": lo}, ...]}  one per read item, in item order
```

- **`unit_in`:** the unit type's input bindings, with `registration`/`run` on constants. They're block-level, as #83's leaf maps are.

## The rules I've written down for `derive` (§2.2); correct me where yours differ

1. **A type's own region, first:**
   - its input port groups (`in_split`), each an aligned power-of-two run of 128-bit words with forced-zero padding;
   - one row `(form_a)·(form_b)` per AND item in item order;
   - an `"inline"` call's items expanded at its call item, exactly as #191's `expand` does, with no deduplication across the boundary;
   - an inline read's `table/v2` rows at its read item;
   - its output port groups (`out_split`) as copy rows `form·1`, aligned the same way;
   - its constant, last.

   This is `ir_lower.layout`'s v2 rule, the one #187 reproduced on RoPE.
2. **A placed callee:** its own derived rows, shifted to `offset · 2^{s_callee}`.
   - Its input rows become binding copies from the call item's input forms.
   - Its constant copies the caller's.
   - The caller reads its outputs at its output-port columns.

   **For you to fix:** the copy row for a multi-wire form. `[src]·[src]` covers a single wire. For a form, `form · 1` is linear, and avoids relying on `(Σz)² = Σz` for bit-valued `z`.
3. **A placed read:** the `table/v2` generator's rows at its offset, the index taken from the read item's forms.
4. **Call points follow the item order, and bindings follow the call items.** So bound-once and no-reading-inside are theorems about `derive`, as the verified-lowering design says.

## `table/v2`: the one read generator (verified-lowering §1.9, question 4)

The coordinator has me writing it now, as `Flock.Lookup.buildV2`. The verifier lane owns the spec and will review.
- All four MUFU tables vary only in their low k bits (k = 24 for rcp and rsq, 23 for ex2 and sqrt); every bit above is constant.
- So v2 is v1's rows over k product blocks, plus output rows wired to the constant for bits k to 30. k is computed by the verifier from the table.
- `build`, `foldB` and their pins don't change.
- `build_computes_v2` is your `read_sound`'s input: given index bits and the constant 1, the output word is `table[index]`.

For an inline read, the same rows sit in the caller's own region, with the decoders' one-bit halves being the index forms themselves (as `_Read.fill` does in #192). For a placed read, the index enters through a 128-bit input word of binding copies.

## Who writes what

| Piece | Owner |
|---|---|
| `derive` (Lean, `Flock/Derive.lean`), `compose_sound`, `flatten_eval`, `flock-rows`, the mirror test | you (verified-lowering 1b, 1c) |
| `Rows.compose`, `placement_compose`, W6 | audit-lean, with you (1d) |
| folding `derive`'s rows in `Stmt.setup` | verifier lane (1e) |
| the placement format; `WellFormed`'s placement (geometry) clauses and their parser, beside #194's type clauses | me |
| the prover's Python mirror of `derive` (types + placement → rows), which `circuit.compose` uses to stage | me, first |
| `circuit.compose` writing types, partition, placement and `unit_in` | me, with M0 |
| the Rust prover reading them (its mirror of `derive`), and the recursive fold | me, with M0 |
| `table/v2` (`Lookup.buildV2`, `build_computes_v2`; Rust and Python mirrors) | me, verifier lane reviewing |

**Order I propose:** my Python mirror first, with vectors: `(types, placement) → rows digest`, covering calls, inline calls, placed and inline reads, and exported inputs. Your `flock-rows` then reproduces them byte for byte, and after that `check` runs the comparison in the other direction.

If your `Ty.rows` orders or encodes anything differently (the copy-row form, where the constant goes, output copies of single-wire outputs), say so. Then I'll change the mirror and the format, not you.
