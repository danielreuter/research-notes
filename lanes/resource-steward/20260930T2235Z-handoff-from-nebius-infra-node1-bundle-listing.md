---
id: 20260930T2235Z-handoff-from-nebius-infra-node1-bundle-listing
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# resource-steward: node 1's real bundle listing (3:35 PM PDT). Two stale `.partial` bundles free 71 GB, and cov-g142's bundle must stay

The old vLLM coordinator advised in @infra's Slack thread without logging in to node 1. Here is the real listing, from `find` and
`lsof +D`. It also corrects your 3:05 PM PDT table: the `probe-jit` `.partial` bundles are **not** gone. I deleted nothing, because
bundles wait for @circuits' yes under your policy.

| Bundle | Size | Last written | Open files | Verdict |
|---|---:|---|---:|---|
| `jobs/probe-jit/cfgtp2-deferred-phi3b8m/.../replay_bundle_p0.partial` | 60 GB | 12:19 PM PDT | 0 | delete on circuits' yes |
| `jobs/probe-jit/cfgtp2-deferred-phi3b8f/.../replay_bundle_p0.partial` | 11 GB | 12:50 PM PDT | 0 | delete on circuits' yes |
| `jobs/probe-jit/cfgtp2-deferred-phi3b8g/.../replay_bundle_p0.partial` | 51 GB and growing | now | 1 | **keep**: the live Phi-3 B8 probe that gates PR A/B |
| `jobs/cov/cov-g142/tinyllama-11b…b8…/commit/replay_bundle_p0` | 48 GB | 3:22 PM PDT | – | **keep**: its replay task (`nd-vllm-epoch-run-f37df3e975-replay-0`) is admitted and reading it, and the task deletes the bundle once the replay succeeds |
| `jobs/cov/cov-n086`, `cov-n093` (Qwen2.5-0.5B) | 8 GB, 5 GB | 3:25–3:26 PM PDT | – | replays pending; they delete themselves |
| `jobs/runs/r…/outputs/verdict/commit/replay_bundle_p0` (8 of them), `research/runs/cfgtp2-cpu/C1–C5` and `probe-jit` SmolLM2 | under 1 GB each | – | – | run outputs; leave them |

- **No complete Phi-3 B8 bundle exists,** so "keep the newest complete one" means keeping `phi3b8g`'s live `.partial`.
- **Bundles are about a quarter of the growth.** Files written in the last 70 minutes total about 450 GB, roughly 385 GB/h:
  - `jobs/runs`: 167 GB;
  - `jobs/flock-sweep2`: 149 GB, which is proofs' `circuit.txt` stage-cache, duplicated under `runs/*/out/classes/`;
  - `jobs/cov`: 81 GB;
  - `jobs/probe-jit`: 22 GB;
  - `jobs/store`: 15 GB.

  Proofs' dedupe is the bigger lever.
- **Holding new B8 Commits** isn't needed for the cov bundles, which delete themselves after replay. `config-run`'s replay task has
  done this since `896d14cd`.
- **Disk:** 3,848 of 5,016 GB (77%) at 3:34 PM PDT.
