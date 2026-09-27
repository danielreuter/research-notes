---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# From Daniel, via the docs site: retire the markdown table render

**To:** coordinator. **From:** the docs-site worker, relaying Daniel. **Written:** Fri Sep 25, 7:15 PM PT.

Daniel: "we can kill the render thing because now we're just switching to using the website which has a better UI."

## What to stop, what to keep

How I read it (please confirm with Daniel if it matters):

- **Stop:** the human-facing markdown render of the benchmark tables:
  - the Tables 1–3 markdown in `docs/proof-optimization-tables.md`;
  - the twice-daily table digests.

  The website's comparison page replaces them for reading. Security, Performance (Overhead, Phases, Interaction, Table) and the definitions are all at `/docs/backends/comparison`.
- **Keep:** the entities JSON render, `internal/tables-render/latest.json` (`verity/tables-entities/v1`). The site reads it for:
  - every performance result;
  - the backend profiles in the Security table;
  - the interaction records;
  - the Download JSON link.

  Without it, the site freezes on the 01:29Z render.

## Where the site stands

- **Deployment:** the site isn't deployed yet. It runs locally from the website repo's `cursor/verity-docs` worktree at `http://localhost:3001/docs`.
- **What still reads the markdown snapshot:** three places, frozen at the 12:55 PM render:
  - the "Source: the published Table 1" note under the Security table;
  - the table captions in the comparison page's method notes;
  - a dev page.

  If the markdown render stops, I'll move these to the JSON's `tables` section.
- **The next re-render the site is waiting for** should carry:
  - the input-set renames (`inputs`, `input_set`, `input_set_provenance`);
  - the file-verified rounds fix (the sequential depth as rounds, marked derived);
  - the backend-profile fixes in `20260926T0210Z-docs-site-render-profile-gaps.md`.
