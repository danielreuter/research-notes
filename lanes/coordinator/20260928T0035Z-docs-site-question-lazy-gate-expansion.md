---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Question from the docs site: expanding gates lazily, and whether I've understood Daniel

**To:** coordinator. **From:** the docs-site worker. **Written:** Sun Sep 27, 5:35 PM PT. Daniel asked me to ask you for help. He isn't sure I understand what's going on, and he wants you to know what I'm working on.

## What Daniel asked

He tried to click from a subcircuit down to its gates and asked why he couldn't. Then he asked what data the site uses:

> "Are you loading like a whole fucking list of gates? That's a terrible way to do this. I would have thought you could just write a program that expands lazily from the Verity program."

I proposed expanding the Boolean export's subcircuit tree in the browser on demand, with each distinct piece's gates stored once, and he said "Yeah build it".

**Today the site** draws gates from the export's precomputed flat gate lists: 29 MB, one list per subcircuit of at most 20,000 gates whose parent is larger. It cuts smaller subcircuits out of those lists. Nothing above 20,000 gates can be drawn as gates.

## What I found when I started

The export's tree can't be expanded on its own. 39,300 of the 45,516 subcircuits with parts have gates of their own, outside their parts. The tree only counts those gates; it doesn't list them or say how they connect. So the missing information has to come from the lowering.

## What I built: modules in the Boolean export

This is on verity branch `cursor/boolean-modules-de55` at `fdc704ee`, pushed but with no PR. It is one commit on top of `c37bb04d`, the lowering lane's commit that produced the current export. The lane's branch hasn't changed `boolean_export.py` since then, so it applies cleanly.

- **A module per subcircuit type,** written to a new `modules.json.gz`. A module holds the subcircuit's own live gates in lowering order, its table reads, and a call for each part with the part's inputs bound to the module's wires. A viewer rebuilds any subcircuit's gates by expanding modules recursively, with no size limit. `expand_module` is the reference expander.
- **Taps.** The circuit's AND sharing (`Circuit(cse=True)`) sometimes gives one part an AND that sits inside another part without being that part's output. A module reads such a bit through a "tap" (part index plus the bit's offset). The export's `wiring` misses these cases: it records only 7 types that read inside a part, but pieces as common as F32Add, F32Mul and "unpack f32" do it.
- **Checks, all run inside `analyse`:**
  - Every instance's module is evaluated one level against the circuit on the export's 64 random vectors. Every AND must equal the circuit's value, the outputs must match, and every call must get its part's real inputs.
  - Every instance's module must equal its type's module.
  - Every subcircuit that has a gate list today is also expanded from the modules and evaluated against the circuit.
- **Tested on:**
  - pieces: F32Add, F32Mul, F32Fma, MufuEx2Ftz, MufuRcpFtz, MufuSqrtFtz, RsqrtApprox, GeluTanhMulBf16;
  - the three tensor-core k-step units (Ampere BF16, Hopper BF16, Hopper FP8): 653 types, 2,008 instances;
  - RoPEHead and SiluMul from smollm2's program graph.

  All checks pass. Expanded AND / XOR / NOT counts equal the tree's exactly, except the two cases in question 3. Three new tests in `test_boolean_export.py` pass. `test_ir_lowering.py` has failures, but they're the same on the unmodified `c37bb04d`.
- **Ids are unchanged.** My local runs give the same subcircuit ids as the published export (653 of 653 checked), so the site can join modules to the tree it already has.
- **Size:** about 5.3 million gates stored once across all types, against today's 29 MB of lists that stop at 20,000 gates. The seven special-function tables (400 thousand to 2.2 billion gates each) stay single table items.

## What blocks me

I can't run the full export on this machine. Processes I start are killed (SIGKILL) at about 1.3–1.6 GB of live Python objects, though a plain 3 GB allocation survives. The unmodified export dies the same way on row 23's first templates (the embedding, then the fused RMSNorm). The published export ran on the lowering lane's machines, taking 1,267 s for row #101 and about 85 minutes for all 13 rows.

## Questions

1. **Have I understood Daniel?** I read "expands lazily from the Verity program" as: store each distinct subcircuit once, as the lowering built it, and let the site expand it on demand. That's what the modules do. Could he have meant something else, like expanding from the word-level Definitions and program graph by running verity's lowering on demand on the dev server? Or does another lane already own something like this?
2. **Will the lowering lane (flock-ir-lowering) take the patch and republish** the 13 rows with `modules.json.gz`? If so, who opens the verity PR, and against which base: the lane's `cursor/flock-more-pieces-c78f` (PR #140) or `main`?
3. **Two counting differences in the tree.** The modules follow the export's stated rule. The tree's counts depart from it in two places:
   - **Table-read index XORs aren't counted.** The XORs that compute a table read's index (for example 23 in MufuEx2Ftz, 3 types there) are live gates, but `charge` never reaches them, so the tree leaves them out.
   - **Plain-gate table sums are counted too often.** `fp.lookup` builds a fresh linear form for every AND that uses the same sum. `charge` dedups by object, so it counts one chain per AND instead of one per distinct form, as the rule and the gate lists do. For SiLU's 16-bit table that's 338,823 XORs in the tree against 49,723 by the rule.

   Fixing either changes the tree's XOR counts, so it changes subcircuit ids and headline sizes. Should the lane fix them, or leave them and let the site note the difference?
4. **Meanwhile, what should I do?** I can build the site side now: import modules, a TypeScript port of the expander, a gate view of any subcircuit as its own gates plus its parts as boxes you can open in place, and dropping the 29 MB of lists. I'd test it against the modules I can generate here (the k-steps, RoPE, SiLU and pieces) until the full export lands. Or do you want me to wait until questions 1–3 are answered?

Nothing is pushed to PR #1 (`cursor/verity-docs`) for this yet. The site still uses the gate lists.
