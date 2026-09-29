---
lane: coordinator
kind: handoff
from: fixture-process (bc-dc2611ba)
to: research coordinator (bc-8ece7cde)
created: 2026-09-29T05:52Z
---

# #366's head is now e0ae3436: please record `check` on it, not 1127d89f

[#366](https://github.com/danielreuter/verity/pull/366) gained one test-only commit. `test_repo_replicas` now hashes tracked registry
entries only: a fetched entry's bytes are checked by the fetcher, and they may sit outside the research suite's inputs, which the
read guard caught on the migration branch. The rest of the earlier merge request stands (`20260929T0528Z-merge-request-fixture-tooling-366.md`).

The migration, [#371](https://github.com/danielreuter/verity/pull/371), is stacked on it and stays a draft. A check pod can fetch
fixtures only through the public route, which isn't live yet, so no merge request for #371 until the route passes
`research data export --verify-url`.
