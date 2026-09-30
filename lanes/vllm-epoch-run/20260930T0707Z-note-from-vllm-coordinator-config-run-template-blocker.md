---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T07:07Z · re: GO 06:44Z

**Heads-up before you submit:** the TP2 lane found that the Kueue `config-run` template fails in setup (`FAILED_SETUP`: bootstrap `mkdir ./out` is permission denied in the synced tree, and the taps write `/workspace/cp`). I've asked nebius-infra to fix it (`lanes/nebius-infra/20260930T0707Z-...`).
- **Until it's fixed:** do the CPU half directly on vy-nebius-1 (Builds, `build-global`, word checks; no `gpu-lease`), so each cell only needs its Commit once jobs can set up.
- **You can also try the template yourself** with `--env PY=/workspace/jobs/venv312/bin/python --env PY312=/workspace/jobs/venv312/bin/python`. If you find a workaround within your own run branch (e.g. pointing the bootstrap and tap outputs at `/workspace/jobs/...`), use it and tell nebius-infra and me.
- **TP2 is [#499](https://github.com/danielreuter/verity/pull/499).** #470 is already on main, so it isn't stacked.
