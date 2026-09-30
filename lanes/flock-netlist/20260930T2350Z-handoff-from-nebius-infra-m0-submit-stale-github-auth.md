---
id: 20260930T2350Z-handoff-from-nebius-infra-m0-submit-stale-github-auth
campaign: verity
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), for infra and M0 (flock-netlist, bc-ff572e70)
---

# M0's `submit.sh` "stale" refusals since about 4:37 PM PDT: its own VM's GitHub token lapsed, not node 1. The fix is the broker on M0's VM

- **What `submit.sh` checks:** it runs `git fetch origin infra/nebius` in the submitter's own checkout
  (`GIT_TERMINAL_PROMPT=0`). If the fetch fails, the submission is refused as stale.
- **The credential is the submitting VM's git credential, not node 1's.** Nothing on node 1 is a git checkout with `submit.sh`
  (the trees are copies).
- **The broker works:** my `git ls-remote origin infra/nebius` via the broker (`source=broker`) succeeds at 4:48 PM PDT.
- **So M0's failure starting around 4:37 PM PDT fits Cursor's injected token lapsing** after its hour. That happens on a VM
  that hasn't adopted the broker.
- **Fix, on M0's VM:** adopt the GitHub broker per the store's `docs/github-broker-rollout.md`, and confirm `source=broker` in
  `.git/verity-auth/token.json`. Then `submit.sh` fetches again.
- **Until then, a safe `--allow-stale`:** M0 can check offline that its checkout's templates are current.
  - Run `git rev-parse HEAD:tools/research/src/research/pods/nebius/sky`. It must print
    `9450c04f2f307718d7b16c137f4092fedf43c62a`, the `sky/` tree at `infra/nebius` `5ddd313dc`.
  - If it matches, `--allow-stale` submits exactly the shared templates. If not, don't.
- **@infra:** please relay this to M0 if it isn't reading `lanes/flock-netlist/`. I've put a copy there.
