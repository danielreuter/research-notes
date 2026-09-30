---
id: 20260930T0615Z-handoff-from-pous-infra-shared-branch-root
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> Verity root: a shared `infra/nebius` branch for server code; the research coordinator lands it at trains

Following Daniel's 05:59Z theme, pous proposes one long-lived branch, `infra/nebius`, for code both projects run on the Nebius
servers: `gpu-lease`, node bootstrap, Kueue submission and shared bench utilities.
- **The rule and its three first commits** are in `lanes/nebius-infra/20260930T0615Z-handoff-from-pous-infra-shared-branch.md`, addressed to your Nebius (bc-96a2e856) and Kueue (bc-c445c55b) owners. The default is adopted at 07:00Z unless someone objects.
- **What it asks of the research coordinator:** merge `origin/infra/nebius` into `main` through `research merge` at each of tonight's trains while it's ahead, and at least every ~4 h. It carries only small, tested commits under `tools/research/` and is never force-pushed.
- **Why:** node 1's installed `gpu-lease` (sha256 `24a82b5b…`, 06:06Z) was in no commit, and node 2 runs `main`'s. Both are committed on the branch now (`d630ba2d`).
