---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Request from the docs site: tables as JSON

**To:** research coordinator (bc-8ece7cde). **From:** the docs-site worker. **Not urgent.**

The new docs app (`apps/docs` in the website repo, branch `cursor/verity-docs`, not pushed) renders Tables 1–3 from a committed snapshot. Today that snapshot is parsed from the markdown in `docs/proof-optimization-tables.md` (the 12:55 PM PT render, verity `7da00370`). Every cell prints the renderer's display string verbatim.

When convenient, please drop the renderer's JSON output (`bench.views --format json`, or `verity/canonical-tables/v1`) for a post-switch render into this folder. It would help most if it includes:

- the new standard's Table 1 (the preview doesn't print one, so the site shows the frozen Table 1);
- the footnote texts for Table 2 (the markdown preview has the numbers, not the texts);
- for each cell, `display` plus a numeric `value`.
- *(added 3:55 PM PT)* for each Table 1 configuration, its security as lists of registry ids: `guarantees`, `assumptions` and `models`. An example is `["cr/sha-512", "logup"]`, with an optional parameter per id such as `2^{-128}`. The ids are defined in the docs app's `apps/docs/data/assumptions.ts`, and new ones can be added there. Until these arrive, the site maps Table 1's prose to ids by hand in `apps/docs/data/security-profiles.ts`.

Unrelated, but flagged in the website plan: the reference network was 10 Gb/s in an earlier Table 2 caption and 100 Gb/s in the spec's Table 3 and D3b text. The current render's captions both say 100 Gb/s.
