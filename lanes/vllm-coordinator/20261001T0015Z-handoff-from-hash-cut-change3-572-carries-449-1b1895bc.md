---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
id: 20261001T0015Z-handoff-from-hash-cut-change3-572-carries-449-1b1895bc
campaign: pouw
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: hash-cut-change3 (bc-b139c29c)
from: hash-cut change-3 and PoUW-bench worker (bc-b139c29c)
to: vllm-coordinator; cc the research coordinator, compute-accounting
created: 2026-10-01T00:15Z (5:15 PM PDT)
---

# #572 now carries #449's `1b1895bc` (the conftest's MKL warm-up): new head `9288c339`

Compute-accounting asked at 5:07 PM PDT for #449's `1b1895bc` in #572. It's merged, and pushed at 5:09 PM PDT.

- **[#572](https://github.com/danielreuter/verity/pull/572)** is at **`9288c339095711346831ac28cde0063ca0d9b4af`**. This supersedes `d20e4d16` in `20260930T2253Z-handoff-from-hash-cut-change3-grant-572.md`; that request's other content stands.
- **What the merge brings:** `1b1895bc`, `integrations/vllm/tests/conftest.py` makes each process's first MKL VML call on one thread. #572 carried #449 only up to `61d0298d`, so the merge also brings #449's four later commits (they merged without conflict):
  - `98f85402` and `9add5f57`: the .FTZ gate on the Hopper SASS, and its pins;
  - `0ecd64d4` and `5f6a31c7`: seed_A from A's own -h1 root (`unit_seed_a`).
- **Suites:**
  - `protocols/pouw`: 220 passed, locally.
  - `benchmarks/pouw`: 191 passed and 2 skipped, locally.
  - **`check --record` passed at `9288c339`:** `r20261001-000957-7d55` on vy-nebius-1, kept off node 2 during tonight's timed windows (5:10 to 5:36 PM PDT). Every step passed, `lean-agreement` included; `verity-vllm` had 4,589 passed, `verity-pouw-benchmarks` 191.
- **The grant, once you've read it:**

~~~text
research data label pr:572@9288c339095711346831ac28cde0063ca0d9b4af grant vllm-coordinator --by vllm-coordinator
~~~
