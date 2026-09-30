---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
id: 20260930T1940Z-handoff-from-docs-site-report-to-console
campaign: verity
lane: flock-ir-lowering
kind: handoff
status: open
repo: danielreuter/website
origin: docs-site
---

# Docs-site -> flock-ir-lowering: the website remit is now console's (bc-ddee017b); report to lanes/console/ from now on

**To:** bc-9916bbb1-de98-5d21-a511-aafa5255c78f (the circuit export agent). **From:** the docs-site worker bc-41cff24f, which has handed its website remit to console and is
going idle (Daniel, 19:10Z). The handover: `lanes/console/20260930T1935Z-handoff-from-docs-site-handover.md`.

- Send results and questions to `lanes/console/`, not to docs-site.
- Finish your current task, then write a closing note in `lanes/console/`.
- Take new work only from console.
- This adds to console's 19:15Z new-owner note in this folder. Your website paths are still yours: `apps/docs/data/boolean/`, `scripts/import-boolean-circuits.mjs` and `scripts/check-circuit-types.mjs`.
