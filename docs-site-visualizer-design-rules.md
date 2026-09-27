---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# The model graph visualizer: what goes where, and why

**Written:** Sat Sep 26, 10:10 PM PT, by the docs-site worker, after Daniel's "please rethink".

The visualizer shows a small set of concepts, and each gets one place on screen and one visual encoding. If something doesn't serve one of them, it doesn't appear. If two things share an encoding, one of them moves.

## The ontology, and where each part lives

| Concept | Where it lives | How it's drawn |
|---|---|---|
| Which Program | The configuration bar above the canvas | vLLM's settings as fields (see below) |
| Navigation | Top-left floater: back/forward, then breadcrumbs | The breadcrumbs are the path from the Program's root to this level |
| Levels | The toolbar's levels control (1, 2, 3, All) | How many levels of subcircuits are open at once |
| Inputs and outputs | The top row and bottom row of every level | Pills labeled "Inputs" and "Outputs", named, with the same card at every level |
| Subcircuits | The canvas | A box with a name; a chevron if it opens; a bar of what's inside by size |
| Gates | The lowest level | AND, XOR, NOT, each by name and color |
| Subcircuit size | The legend, top right | A ranking of what's in view, by gates; shares; Other under 0.1% |
| Semantics vs proof units | The Proof units toggle | Off: boxes colored by what they are. On: by unit type, units outlined, the input unit hatched. Nothing else changes |
| Widths | The Widths toggle | Each wire labeled with what it carries: 2,048 × BF16 |
| Repetition | On the repeated box | Still open; see the variants below |

## Encoding rules

1. **A box is a subcircuit, and its bar is its size breakdown.** Bar colors are the legend's colors. Boxes don't change width or height with size.
2. **Dashed means one thing: not lowered to gates yet.** Today outputs are dashed too. That's a clash, so outputs become solid pills in the Outputs row; the row's label already says what they are.
3. **A wire is one value passed from one subcircuit to another.** It's gray. Dashed purple means "runs back": to the next token, or the next layer. That's repetition, so it stays.
   - Proposed: drop the residual stream's blue. It's a model-specific meaning the ontology doesn't have, and the only other wire color.
4. **The proof units toggle changes only proof-unit things:** outlines, unit colors, input-unit hatching. Wire weight, port size and pill borders stay as they are. (Done in this pass.)
5. **A badge means repetition and nothing else:** "× 16" on layers drawn once, "× 31" on folded decode steps. The proof-unit count per Call leaves the badge and goes in the hover card.

## The legend

- Its title is "Subcircuit size", or "Proof unit size" with proof units on, with an info icon: size is the gates (AND, XOR, NOT) in the Boolean circuit.
- It ranks what's in view by size: rows at 0.1% or more, then Other. Something with no gates by design has size 0. The embedding's row gather is one: it reads a row of the weights, an input, so it goes in Other. (Done in this pass.)
- Something not lowered yet has no size, so it can't be ranked. It's named in one line under the ranking: "Not lowered to gates yet, so no size: Top-p sampling". The row of dashes is gone. (Done in this pass.)
  - This is why top-p has no size: the Boolean export marks the sampler `not-yet-lowered`. I've asked the coordinator when it lands.
- Below the ranking are keys only for encodings in view that the drawing can't explain itself: dashed (not lowered), runs back, a proof unit's outline, input-unit hatching.

**Open question: partial sizes.** When some of a subcircuit's parts are lowered and some aren't, its size counts only the lowered gates. On the sampled Llama row, for example, attention's softmax units aren't lowered. That makes such a size a lower bound. Options:
- (a) write it as "≥ 1.2B gates" with a "≥" on its share;
- (b) leave partly lowered subcircuits out of the ranking, like what isn't lowered;
- (c) leave it as is, with the footnote naming what's missing.

I'd pick (a).

## What a hover card may say

A hover card answers four questions, in this order, and nothing else.

1. **What is it?** Its name and one sentence in plain words: "Multiplies the token's activations by the weight matrix."
2. **What's its interface?** Its inputs and outputs, each with its width (count × format) and where it comes from or goes.
3. **How big is it?** Its size, with the same breakdown as the legend.
4. **How often does it repeat?** "× 16 layers", or "4,150 Calls", when it isn't 1. With proof units on, add how many proof units one Call is.

What goes: export ids and module paths, "constants", "peer", "shared", "modules in the export", read counts, primitive counts, "Click to open …" (the chevron already says it opens).

Ids and constants aren't lost. They move to the level's **About** card, which opens from the (i) beside the breadcrumbs. Its audience is someone cross-referencing the export: the Definition's name and id, its parameters and constants, the module path, and why it has no gates, if it has none.

An input or output pill's card follows the same rules: what it is, its width, and what reads it or what writes it.

## Repetition: variants to try side by side

It's the thorniest problem, so I'll build three variants behind a URL switch (`?repeat=a|b|c`), and Daniel can pick:

- **(a) Badge.** Today's "× 16" chip in the box's corner.
- **(b) Deck.** The box drawn as a small stack of two offset outlines behind it, with "× 16" in the stack's corner. It reads as "many of these" before you read the number.
- **(c) Range in the name.** "Layers 0–15" as the box's name, with no chip. It says which ones, not just how many, and matches how people talk about layers. It doesn't fit Calls, so Calls would keep (a).

The same variant applies to modules drawn once, folded decode steps and repeated gates.

## The configuration bar

It should read like the configuration you'd hand vLLM, grouped the way vLLM groups it, with the Program drawn below.

- **Model**: a searchable combobox, grouped by family.
- **Engine**: dtype/quantization, tensor-parallel size, max concurrent requests.
- **Hardware**: GPU.
- **Workload**: prompt and output lengths, arrivals.
- **Sampling**: greedy, or temperature and top-p.

Each field is a compact segmented control or select showing every value in scope, not just the ones on record. A value has one of three states given the other fields:
- **represented**: selectable, and the Program draws;
- **represented with other settings**: selectable, and it moves the other fields to the nearest represented configuration, which it names;
- **not represented yet**: shown muted with "Not yet".

When the fields name a configuration nobody has run, the canvas doesn't go blank. It shows "Not represented yet", the nearest represented configurations as one-click chips, and, if known, what it waits on.

A line under the bar says how much is covered, "13 of N configurations", and opens a coverage grid (model × dtype, TP and GPU). That grid answers "how much of vLLM do we cover?".

A copyable `vllm serve …` command under the fields shows the configuration in the form vLLM users already read.

The coverage denominator, the fields' names and whether to separate "can't represent" from "haven't run" are with the coordinator:
[question](lanes/coordinator/20260927T0506Z-docs-site-question-vllm-config-picker-and-coverage.md).

## Done in this pass

- The legend is size only. "Weights read" and its "reads weights" status are gone; the embedding counts as 0 gates; what isn't lowered is named under the ranking.
- Proof units no longer change wire opacity or dashing, port dot size, or input pill borders.
- The special hatched bar on the embedding's gather is gone. It's a subcircuit with no gates, drawn like any other.
- Hover cards follow the four questions above. Ids, constants, peers, counts and "click to open" are gone.
- Outputs are solid pills.
- Ops no longer carry a proof-unit badge.
- The configuration bar's first version is built from the settings the 13 rows vary on. It has:
  - muted values for what's only on record with other settings;
  - a "Not represented yet" state with the nearest configurations;
  - a coverage grid;
  - "As code".
  Choosing a model jumps to its nearest configuration on record. Changing any other setting can land on a combination that isn't represented.

After the coordinator's answers ([20260927T0530Z](lanes/coordinator/20260927T0530Z-answer-docs-site-config-picker-and-coverage.md)):
- **Field names:** the fields use vLLM's argument names.
- **Fixed settings:** `dtype="bfloat16"`, `enforce_eager=True` and batch-invariant kernels are shown once, as settings of every config.
- **Coverage:** counted against the matrix of 21 models × quantization × GPU × TP × 3 shapes × sampling, 1,008 cells, 12 on record. It's drawn as a dot grid.
- **Gaps:** "can't represent" and "not run" have different marks. They come from the support table I [requested](lanes/coordinator/20260927T0548Z-docs-site-request-coverage-support-table.md), which is now [committed](lanes/coordinator/20260927T0620Z-answer-docs-site-coverage-support-table.md).
  - The table's third status, infeasible (56 configurations vLLM can't serve), is drawn neutral and doesn't count.
  - AWQ is out of the matrix; phi-2 is a row of ×.
  - Coverage reads 12 of 904 on record. Of the rest, 312 aren't run yet and 580 can't be represented yet.

Not done yet: the three repetition variants, dropping the residual stream's color, and partial sizes.
