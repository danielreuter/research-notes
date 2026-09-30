---
id: 20260930T1711Z-handoff-from-pous-567-vllm-linear-api-merge-request
campaign: pouw
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous -> research coordinator: merge request, #567 at `b4354fdc` (the vLLM linear-site interface), check passed

From bc-f4e8ae34, the pous project's vLLM integration API lane. Daniel approved the rollout at 16:17Z. cc vllm-coordinator: this PR adds a package under `integrations/vllm`.

- **#567** (`cursor/vllm-linear-api-skeleton-e318`) at `b4354fdca97c67fd35ac4476a7084a6fc2d1787d`, marked ready. It contains `main` `b1134766`.
- **Check:** `r20260930-165503-4d59` on vy-nebius-2's check slot, `validation: passed` on every step, lean-agreement included. The earlier head `d8b4bcce` also passed (`r20260930-162056-6994`). Locally, `suites.py verity-pouw repository verity-vllm --quick` passed 3 of 3.
- **What it changes (additive; no behaviour change on any path):**
  - `protocols/pouw/verity_pouw/serving.py`, stdlib only: the hashing formats, the Pearl-C scheme grammar, the schedules, `PassCommitment`, and the kernel-variant and gate data.
  - `integrations/vllm/verity_vllm/linear/{__init__,api}.py`, no vLLM and no torch: the site interface and the `Stack`.
  - Their tests.
  - Two entries in `integrations/vllm/tests/dead_code_keep.json`, until the MVP's install path reaches the modules.
- **Nothing to review beyond the code:** no Lean, no circuit, no pinned statement, no served-path change.
- **What it unblocks:** the MVP migration stack ([#573](https://github.com/danielreuter/verity/pull/573), [#576](https://github.com/danielreuter/verity/pull/576), [#578](https://github.com/danielreuter/verity/pull/578) and [#585](https://github.com/danielreuter/verity/pull/585) on #564) cherry-picks these commits. Once #567 is on `main`, those land as the same content.
