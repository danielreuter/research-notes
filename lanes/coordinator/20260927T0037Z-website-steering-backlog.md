---
id: 20260927T0037Z-website-steering-backlog
lane: coordinator
kind: handoff
status: open
---

# Daniel's visualizer feedback, turn lost to the unpaid-invoice stop

The website agent (bc-41cff24f) errored at 00:37Z with these messages from Daniel still unaddressed. Resend them when it restarts.

1. Legend in Vercel's style: https://vercel.com/ai-gateway/leaderboards/models. A leaderboard of how much of the work each thing is; no number needed, percentage on the right.
2. Can react-flow show the outline of parts over the gates, i.e. nesting that carries the semantics?
3. What is "embedding shard (an opening)"? "Other" should be the catch-all for anything below 0.1%.
4. Hierarchy depth: e.g. embed tokens in Qwen MoE wraps lookup, ranks rows and all-reduce. How many levels to show at once should be customizable, up to the whole model laid out; make it a toggle. Use shadcn for the options and icons.
5. The hover tooltip should be at the top of the screen (it's below the legend now), with a small sub-legend showing the same work decomposition. Replace "share of ANDs" with "Subcircuit size" (number of gates); talk about size everywhere.
6. Nesting is broken: from program, clicking all-gather (nested inside logits) navigates to program/all-gather and shows nothing, while both appear on the same screen.
7. Say "Embedding" and "Unembedding", not "embed tokens" and "logits".
8. Inputs and outputs must be first class, ideally with inputs coming in at the top. Seed and splits look like inputs but carry no information about what they are.
9. Ports: every output port shows two copies of the dot, and arrows don't line up with ports. Probably non-standard react-flow use. Keep the look, fix the mechanics.
10. Inputs aren't standardized: top-level circuit inputs and subcircuit inputs should look the same, and clicking into a subcircuit should still show its inputs and outputs.
11. Proof units are hard to follow; Daniel doesn't understand what he's looking at. The natural view would be an outline grouping each proof unit.
12. What do the bits icons in the subcircuit dropdown mean?
