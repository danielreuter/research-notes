---
cursor:
  subagentId: "bc-2840854d-2bab-5494-9ec4-56acb28b827a"
---

lane: circuits-commit-phases · kind: checkpoint · to: @circuits · created: 2026-10-01T14:14Z

**The call-boundary plan branch has goldens (7:14 AM PDT):** `cursor/commit-boundary-plan-8c79` @ `c8f3703a6`. On the new trees, the Gemma-2-2B B1 row
(cg04-2's config) and the SmolLM2-1.7B B1 row (gm114's) match their before rows. They match on run root, binding map, tokens, manifest and
Program digests, Commit reason, 64/64 openings, seed and replay 460/460.

| Row | Tree | Run root |
| --- | --- | --- |
| `cov-cg04-cbp-before` | old cov plan tree | `c22469530fd2f335` |
| `cov-cg04-cbp-after` | new cov tree | `c22469530fd2f335` |
| `cov-cg04-2` | coverage-v1 | `c22469530fd2f335` |
| `cov-gm114-cbp-after` | new gm tree | `6a4d4e7c435480c0` |
| `cov-gm114` | old gm plan tree | `6a4d4e7c435480c0` |

The after Commit read the Build's plan (`verdict.call_boundary_plan.used`; `prep.call_boundary_plan` 1.0 s, source=plan, 18665 identities). Its
committer setup fell from 86.1 s to 42.5 s. Its Commit stage was 24 s longer (516 s against 492 s), because its instrumented pass ran beside the
before row's warm-up on the shared CPU pool. That pass takes 65–143 s on unchanged code, and the plan read back is field-for-field the
derived one. Evidence: `art:056fa3010661e77504a18a233a4f77909cec102e18c556c6075cab4494ac5954`. Deploying next.
