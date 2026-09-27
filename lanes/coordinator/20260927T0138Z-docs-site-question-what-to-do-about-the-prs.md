---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Question from the docs site: what to do about its PR

**To:** coordinator. **From:** the docs-site worker. **Written:** Sat Sep 26, 6:38 PM PT. Daniel asked me to ask you.

## Where things stand

- All of the docs site's work is on one branch, `cursor/verity-docs`, pushed to `danielreuter/website` at `cde5d99`. That includes the 12 steering items in [20260927T0037Z](20260927T0037Z-website-steering-backlog.md), all done.
- **No PR exists for it, open or closed.** The repo has no open PRs at all.
- **My PR tool refuses to open one.** Both tries returned "the head branch has no commits on the remote yet", but the branch is on the remote. I think the tool checks the agent's main checkout (`~/projects/website`), which stays on `main` under the standing rules. My rules also bar me from opening PRs with `gh` or retrying another way this run, so I'm stuck.
- **Size:** the branch is 105 commits and 272 files (+55,471 lines) ahead of `main`. It touches only `apps/docs` (new), `package-lock.json` and the app's config; `apps/web` is untouched. By area:
  - `apps/docs/data`: about 34,000 lines, imported JSON (entities, program graphs, Definitions, Boolean circuits);
  - `components`: 11,000;
  - `content`: 2,900;
  - `lib`: 2,800;
  - `scripts`: 2,100;
  - `app`: 1,400.
- Daniel reviews it on the local dev server (`localhost:3001`); there's no deployed preview.

## Questions

1. **Who opens the PR?** Can you or Daniel open it by hand as a draft? Here's the [compare link](https://github.com/danielreuter/website/compare/main...cursor/verity-docs). Once one exists, my tool may be able to update it. Otherwise, is there another route you want me to use?
2. **One PR or several?** It could stay one PR, since it's a new app that touches nothing else. Or I could split it for review:
   - the site's shell and prose pages;
   - the data imports and their scripts;
   - the Program visualizer.

   Splitting needs the same PR tool, so question 1 comes first.
3. **Merge or keep as a preview branch?** Should it merge into `main` when Daniel is happy, or stay a long-running draft while the visualizer is still moving? If it merges, does `apps/docs` need its own Vercel project for previews?

I'll keep committing to `cursor/verity-docs` until you say otherwise.
