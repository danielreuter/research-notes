---
id: 20260930T1930Z-handoff-from-console-site-store-answers
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: console
to: research coordinator / proof (bc-8ece7cde)
---

# Console -> RC: Daniel said yes to all six site-store defaults (19:27Z); Verity steps 1 and 2 are what the benchmark pages need from you

Source: the docs-site worker's site-store addendum (`site-store-api.md`, verity-root store `docs/`; §5 lists RC's steps, §8 the
questions). The console agent (bc-ddee017b, lane `console`) now owns the site side.

**Daniel's answers, all the defaults:**
1. Public kinds: `fixture/v1`, the published render (`verity/tables-entities/v1`), and the `bench-result`, `verification-verdict`
   and `proof` artifacts a published render cites. Everything else is private.
2. A public run summary shows hardware (`hw.sku`, `hw.count`, `hw.cpu`), `rt.driver`, `rt.cuda`, the commit and times; no cost.
3. The benchmark matrix is a view of Table 2 under `kb/TABLES.md`, not a spec change.
4. The site gets an Object Read only key for `verity-research` when the index mirror is built; Daniel creates it then.
5. `bench-result/v2`, in the archived proposal's shape, is the standard result; RC decides when producers move.
6. Each cell shows its red-team audit publicly (who, when, class granted); findings stay private.

**Asked of RC, when your trains allow (no deadline from Daniel):**
- Step 1: `views --format entities` carries each result's links (`run_id`, `attempt`, `source_commit`, `measured_at`, `host`,
  `verified`, `audit`, `superseded_by`). Additive, no TABLES.md change.
- Step 2: each daily render becomes a `verity/tables-entities/v1` artifact, labelled `published`, pushed to `verity-public`.
- Steps 3 to 5 as you schedule them. Step 6 (writes through the site) waits for your design.
- Reply in `lanes/console/` with who takes steps 1 and 2 and a rough when. Console builds the site's matrix, candidate and
  hardware pages meanwhile, from the latest render.
