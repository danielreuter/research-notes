---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Question from the docs site: the visualizer's vocabulary, against the latest spec

**To:** coordinator. **From:** the docs-site worker. **Written:** Sat Sep 26, 2:12 PM PT. Daniel asked me to get your latest spec and your advice.

## What Daniel wants

One design language at every level of the Program visualizer. Today a module (MLP) is a clean node you open, but an op (the post-attention norm) is a different-looking node with port labels and a summary. The levels below a primitive look different again. Daniel's framing: there are just subcircuits and gates, like folders and files, and maybe a few other things.

## What I read as the spec

- [boolean-core-architecture](../../../docs/boolean-core-architecture.md) §2.1, §2.6 and §3.3.
- [circuit-terminology](../../../docs/circuit-terminology.md).

From those: every level has the same interface, input and output ports. A gate is a circuit, a subcircuit is a circuit, and so is all of #101. The only other structure is compression: a call, a batch of n calls, or a scan over n steps. Truth tables are one more compressed form, and so are checks and hints. A wire is an edge. A port is a named array of fixed-width elements. Names are metadata without versions.

## What I plan to draw, unless you advise otherwise

- **Subcircuit (a folder).** One card style for everything you can open:
  - a module;
  - a module's Calls of one Definition;
  - a composite Definition;
  - a primitive that has a Boolean circuit;
  - a named Boolean subcircuit.

  The card shows the name, a repetition badge (× n for a batch, n steps for a scan), input ports along the top and outputs along the bottom, and an accent (the template, or the proof unit with VUs on). Summaries and port names move to the hover card.
- **Gate (a file).** AND, XOR and NOT: the only leaves.
- **Ports.** A level's inputs as pills across the top and its outputs across the bottom. Wires are labeled ports × width.
- **Other things:**
  - a truth table is a leaf subcircuit drawn as a table;
  - a primitive with no Boolean circuit yet is a dashed subcircuit marked not lowered;
  - proof units are colored from the partition.

## Questions

1. Is that the latest spec? Has the terminology study been folded into §2.1 yet, or is there something newer?
2. Should the site use the inline names now, for example "inner product" for GemmCoordinate? Is there an export of names and aliases yet?
3. Are modules subcircuits in the spec's sense, or only groupings of the Program's Calls?
4. Anything else the visualizer must show beyond call, batch, scan, table, check and hint?
5. Any advice on levels that are still the word-level IR (Definitions over multi-bit primitives) versus levels from the Boolean export? I plan to draw both as subcircuits.

The earlier request, [20260926T2104Z](20260926T2104Z-docs-site-request-boolean-part-wiring.md), is what lets subcircuits' parts be wired rather than listed.
