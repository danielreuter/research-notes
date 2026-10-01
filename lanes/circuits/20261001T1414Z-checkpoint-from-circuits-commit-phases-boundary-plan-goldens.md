---
cursor:
  subagentId: "bc-2840854d-2bab-5494-9ec4-56acb28b827a"
---

lane: circuits-commit-phases · kind: checkpoint · to: @circuits · created: 2026-10-01T14:14Z

**Goldens agree (7:14 AM PDT):** `cursor/commit-boundary-plan-8c79` @ `c8f3703a6`, on new trees `cursor-grid-boundary-cov-827a` and
`cursor-grid-boundary-gm-827a`.

- **Gemma-2-2B B1** (cg04-2's config): `cov-cg04-cbp-after` equals `cov-cg04-cbp-before` (old cov plan tree) and `cov-cg04-2`.
  - Same run root `c22469530fd2f335`, binding map, seed, verdict, and replay 460/460.
  - The Commit read the Build's plan in 1.0 s, against the plan derivation that made committer setup 86.1 s on the old tree (42.5 s now).
  - Its whole Commit stage was 24 s longer. The instrumented pass ran beside the before row's warm-up on the shared CPU pool, and that pass
    takes 65–143 s on unchanged code. The plan read back equals the derived one, field for field.
- **SmolLM2-1.7B B1:** `cov-gm114-cbp-after` equals `cov-gm114`, with run root `6a4d4e7c435480c0`.

Evidence: `art:056fa3010661e77504a18a233a4f77909cec102e18c556c6075cab4494ac5954`. Deploying now.
