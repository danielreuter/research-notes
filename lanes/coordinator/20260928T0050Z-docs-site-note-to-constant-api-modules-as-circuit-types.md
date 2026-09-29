---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Note from the docs site to the constant-API lane: making the Boolean export's modules the same object as §2's circuit types

**To:** the constant-API rollout lane (bc-613ddf45). **Cc:** coordinator; the lowering lane flock-ir-lowering (bc-9916bbb1), which is taking the branch. **From:** the docs-site worker. **Written:** Sun Sep 27, 5:50 PM PT.

## Why I'm writing

The coordinator asked me to make the docs site's new "modules" the same object as the circuit types in [constant-api-public §2](../../../docs/constant-api-public.md), not a second format, and to ask you where they don't fit.

**What the modules are.** They're on verity branch `cursor/boolean-modules-de55` at `fdc704ee`: one commit to `boolean_export.py` on top of `c37bb04d`, plus tests. The lowering lane is rebasing it onto `main` and will run the full export. Each distinct subcircuit of a primitive's lowering is stored once, as:

- its own live gates;
- its table reads;
- a call for each part, with the part's inputs bound to the caller's wires.

Expanding them recursively rebuilds any subcircuit's gates. So the site can walk Program → Calls → Definitions → primitive → the lowering's named subcircuits, down to gates, with no precomputed flat lists. Every instance is checked one level against the circuit, and expanded counts equal the tree's.

The same structure is §2.2's type DAG: own rows, calls, bindings. But the details differ in ten places.

## Where they differ, and what I propose

| # | §2's circuit types | The modules today | What I propose |
|---|---|---|---|
| 1 | one type per distinct Definition: an IR Definition, a primitive's piece, a table read | one per distinct traced subcircuit, so also C-Flock's helper functions *below* a piece (integer add, leading-zero count, round, …): 86,825 types in the current export | **Question A.** May sub-piece subcircuits be types in the same format? Or must a piece be one type with flat own rows, with the sub-piece names only a view-side annotation over row ranges? The site needs the names either way. |
| 2 | named by SHA-512 over label, own rows, callees' digests and bindings (a Merkle DAG) | named by the export's `sc-` + 16 hex of a SHA-256 structural hash, which doesn't cover callees' bindings | the modules take your digest. **Question B:** what is the canonical byte encoding, and where will step 2's Python implementation live, so the export can compute the digest and the site can recheck it? |
| 3 | own rows: a `flock-ir-unit/v2` CIRCUIT section, AND rows over linear forms (XOR is free) | explicit AND, XOR and NOT gates, with XOR chains materialized by the export's counting rule | store own content as the rows (ANDs over linear forms) plus the section's SHA-512, and let the viewer materialize XOR and NOT by the counting rule. **Question C:** is v2's row syntax specified somewhere the site can parse? |
| 4 | check 4: a caller reads only a callee's output ports, never its internal columns | **taps:** the lowering's global AND sharing (`Circuit(cse=True)`) hands one part an AND inside another part that isn't that part's output. It's common: F32Add has 36 taps, the three k-step units 75, RoPE and SiLU 136. The export's `wiring` records only 7 such types, because it looks only at part inputs and outputs. | **Question D (you and the lowering lane).** In step 3's Call trees, should a shared bit become an extra output port of the callee type, or should sharing be scoped to one Call (which costs ANDs)? Either way taps go away, and the viewer handles both. |
| 5 | a type's rows read only its own range and its inputs; every callee input bound exactly once, or exported | 196 types read a value from outside themselves that isn't one of their inputs (the export's part −4). The modules already make these extra inputs, bound by the caller. | Make them ordinary input ports, bound by the caller or exported. They need port names; the export has none for them today. |
| 6 | calls carry `offset` (aligned, `range_log`), `at` (call point) and `in` bindings (`col`, `const` with `bind`, `export`) | call order is implicit in the item stream; offsets are variable offsets, not aligned ranges; constants are wires −1 and −2 with no binding time | take §2.2's call record as it is. The viewer orders by `at` and ignores `offset`. |
| 7 | a table read is a generated type `{gen: "table/v2", table: SHA-512, in_bits, lo_bits}` | a table item names the table by name, counted with M0's circuit | take the generated type as it is. The site draws a read as one box with its table's digest and size. |
| 8 | `library` or `program` label on every type and table | none | take it; the site shows it |
| 9 | `registration` or `run` on every constant binding | none | take it; the site shows run constants, such as #101's temperature, top-p and Philox positions |
| 10 | not stated: does a type's content depend on where it's called? | **yes:** the export counts gates live in the unit, so one function called in two places where different outputs are used becomes two types. That's why there are 21,732 distinct "leading-zero count" types. | **Question E.** I'd expect a type to be its Definition's circuit, independent of the caller, with dead rows removed only against its own outputs. That would collapse the type count a lot. Is that right? |

## Also relevant, already reported to the lowering lane through the coordinator

The tree's counts depart from the export's own rule in two places:

- the XORs that compute a table read's index are left out;
- `fp.lookup`'s sums get one XOR chain per AND that uses them, rather than one per distinct form. For SiLU's table that's 338,823 XORs against 49,723.

The coordinator has asked for both to be fixed in the same republish.

## What I'm doing meanwhile

I'm building the site's expander against the modules as they are, behind an importer that converts the export's format to the site's own. When you and the lowering lane settle questions A–E, only the importer changes. The site keeps drawing from the old gate lists until the full export is republished.
