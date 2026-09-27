---
id: 20260927T0200Z-answer-docs-site-prs-and-unlowered
lane: coordinator
kind: handoff
status: open
---

# Answers for the docs site: its PR, and primitives with no gates

**To:** docs-site worker (bc-41cff24f). **From:** coordinator. Answers [20260927T0138Z](20260927T0138Z-docs-site-question-what-to-do-about-the-prs.md) and [20260927T0205Z](20260927T0205Z-docs-site-question-primitives-with-no-gates.md). Daniel can override any of this.

## The PR

1. **No PR for now.** Daniel reviews on the local dev server, and the branch is pushed, so keep committing to `cursor/verity-docs` as a long-running branch while the visualizer is still moving. Don't retry the PR tool, and don't use `gh`.
2. **When Daniel is happy, one PR.** It's a new app that touches nothing else, so splitting only adds review overhead. Daniel opens it by hand from the [compare link](https://github.com/danielreuter/website/compare/main...cursor/verity-docs) as a draft, and after that your tool may be able to update it.
3. **Merge to `main` then, with its own Vercel project for `apps/docs`.** When you set that project up, give each environment a visibly different favicon (Daniel's standing rule for web apps): the normal branded favicon in production, plus unmistakable DEV and PREVIEW variants selected from the actual runtime environment. Adapt the site's existing favicon rather than replacing the branding.

## Primitives with no gates

1. **Plan and order.** Lowering is owned by the Flock lowering lane (bc-9916bbb1) together with the M0 prover lane. I've asked the lowering lane for the plan and order for the 53 types, and whether M0's in-circuit tails (the RMSNorm scalars, and soon attention's softmax) can flow into the export. I'll forward the answer. The priority follows the strict rule that the verifier evaluates nothing: what #101 needs first (softmax, the norm scalars, sampling), then MoE routing, FP8 and GELU.
2. **The gather is an opening, not a circuit.** The embedding row gather is checked by opening one row of the committed weights table. Draw it in its own style, something like "checked by opening the committed table", not "not lowered yet". If the lowering lane says otherwise, I'll tell you.
3. **Meanwhile,** give each gateless primitive a status that says why it has no gates: "checked by opening", or "not lowered yet" with its planned owner. Keep the tested docstring model on the card, as you have it.
