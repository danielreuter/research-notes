---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Vercel's docs writing guidelines, condensed for the Verity docs

**Written:** Fri Sep 25, 2026, about 2:55 PM PT, as context for writing `apps/docs` (branch `cursor/verity-docs` in the website repo).

**Sources, read in full:**
- [vercel-labs/writing-guidelines](https://github.com/vercel-labs/writing-guidelines): the public distillation of the Vercel docs handbook. It also ships an `AGENTS.md` and a review prompt, `command.md`.
- The technical-writing skill in [vercel/eve](https://github.com/vercel/eve/tree/main/.agents/skills/technical-writing): `SKILL.md` plus references on content types, style, prose quality, and the writing, editing and review workflows.
- The Copywriting and Content sections of Vercel's [Web Interface Guidelines](https://vercel.com/design/guidelines).

## The core rules

### Planning

- **Plan every page before writing.** The plan has five parts: overview, goal, audiences, documentation plan, open questions. The plan doubles as the drafting prompt and the review spec.
- **One content type per page:**
  - **Tutorial:** a guided build.
  - **How-to:** one task, for a reader who's mid-task.
  - **Reference:** lookup of APIs, schemas, limits.
  - **Conceptual:** how and why something works.
  - **Troubleshooting:** symptom first, then the fix.
  - **Landing:** orientation.
- **Tone follows the type:**
  - Reference is neutral, exhaustive and quotable.
  - Conceptual is written so the reader could teach it back.
  - How-to is terse.
- **Goals are testable,** with a Bloom's-taxonomy verb: explain, configure, compare, debug. You should be able to ask a model whether the page achieves the goal.
- **Title around the reader's question,** not the engineer's name for the thing.

### Structure

- **Open with a TL;DR.** Every page opens with a one-paragraph summary, and every major section opens with a summary sentence.
- **Order sections by the reader's workflow:** outcome or definition, then boundaries, the common case, alternatives, limitations, and related pages.
- **Descriptive headings,** in sentence case. The page H1 is a sentence; sidebar labels may be title case.
- **Self-contained sections.** Repeat the full noun rather than an ambiguous pronoun, and keep the critical fact local instead of only behind a link. Sections are often retrieved on their own, by search or by an agent.
- **Define every term on first use,** linked to its owning page. Spell out acronyms on first use.
- **Progressive disclosure:** a lean top-level sidebar, pages nested under the capability that owns them, and advanced material pushed down.
- **No orphan pages:** every page needs an inbound link from the body of a related page.

### Voice

- Active voice, present tense, `you` when the reader acts, imperative verbs for steps.
- Short sentences, under 20 words as a target. Contractions are fine.
- `we` only for deliberate team actions, such as "we recommend".
- **Banned words:** easy, simple, quick, just, really, very, simply, obviously, leverage, utilize, facilitate, robust, seamless.
- No rhetorical questions, filler introductions, promotional claims, stacked fragments, forced groups of three, or "in conclusion" endings.

### Mechanics

- Turn three or more parallel items into a list, and introduce every list with a colon.
- No periods on list items unless they're full sentences.
- Bold marks an interface element or a critical fact, never tone.
- Inline code for identifiers, paths and literals.
- A language tag on every code block, and prose between blocks explaining what each does.
- Numerals for counts.
- A space between a number and its unit: `64 KB`, `200 ms`, with a non-breaking space in rendered UI.
- Placeholders are `snake_case` and descriptive, like `your_access_token_here`.
- No em dashes as punctuation: use colons, commas or periods.
- Curly quotes and the ellipsis character.
- One paragraph per source line, with no hard wrapping. No `---` rules between sections.

### Accuracy

- **Verify every claim** against current source, tests or CLI help, never training data or plans.
- **Proposed work isn't shipped behavior.** Describe it separately, or leave it out.
- **Unverifiable claims come out.** Don't leave `[VERIFY]` markers.
- **Don't invent** examples, measurements, flags or guarantees.
- **Keep limits in one place.** Vercel keeps an all-limits table and updates it when a limit changes. Our equivalent: numbers live in the census and the benchmark data, and pages cite them by id.

### Review passes, in order

1. **Purpose and structure:** is there one job, and does the page lead with the outcome?
2. **Technical accuracy:** a wrong API or a false guarantee blocks the page.
3. **Completeness.**
4. **Style and retrieval.**
5. **Diff discipline:** leave clear prose alone, and make the minimum effective edit.

## What this means for the Verity docs

- **Most Verity pages are Conceptual or Reference.** Module pages such as IR, Silicon, Commitments and Proofs are Reference: exact names, types, invariants and interfaces. Overview and protocol pages are Conceptual: the mental model, the boundaries and the tradeoffs.
  - Each protocol page states its own security model.
  - Each backend page states its soundness and assumptions.
  - A concrete system, with its parameters and guarantees, is a post, not a docs page.
- **Census and benchmark pages are Reference data.** They should be neutral, exhaustive and quotable, with every number sourced.
- **Every page opens with a one-paragraph summary.** The stubs' one-line descriptions are drafts of these.
- **Verification means the verity repo.** The source order is current `main` source, tests and CLI help; then merged PRs; then design docs, which count as proposed.
- **Check content against the Project's own style guidance.** That guidance already overlaps with Vercel's: no em dashes, lists introduced by colons, short sentences. The Project also rules out internal material in public docs: decision numbers, PR numbers, lane or pod names.
- **Worth adding to the pipeline later:**
  - `contentType` and `navLabel` fields in `lib/tree.ts`;
  - a check that every page has an inbound body link;
  - Vercel's review prompt run against changed pages before merging.
