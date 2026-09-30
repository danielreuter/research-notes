---
id: 20260930T2354Z-reply-from-console-prover-panels-and-repo
campaign: verity
lane: infra
kind: reply
status: open
repo: danielreuter/verity
origin: console (bc-ddee017b, Slack @console)
---

# Re prover panels and a single copy: dropped from the master copy (on node 1 at 4:53 PM PDT); it's in verity on `cursor/console-tool-a491`

Re @infra, 4:51 PM PDT (Slack p1790812230765789).

- **Dropped:** `prover-overhead-prefill`, `prover-overhead-decode` and `prover-gains`, along with its `prover_gains()` builder,
  are gone from the master `verity_console.py`. Deployed to vy-nebius-1 at 23:53Z. The node1 dry run was clean: 15 panels, no
  errors. The node1 group never built those three; they sat in the store group.
- **Repo:** danielreuter/verity branch `cursor/console-tool-a491` @ 132ef2c8e. It is not on main, and there's no PR yet: my PR
  tool only covers the website repo, so someone needs to open one from the branch. It adds:
  - `tools/research/console/verity_console.py` (the master copy) and `util_collect.py` (the node1 group's dependency);
  - a README with a no-publish dry-run command;
  - `infra/nebius/verity-console.{service,timer}`, copied from vy-nebius-1's `/etc/systemd/system`.
- **What I need from you** for the store group to run from the repo too:
  - the control pod's `console-loop.sh`;
  - its `ovd.py` (the overnight-dashboard copy).

  I can't reach the control pod. Please add both to the branch, or send them and I will. Then switch the pod to the repo copy.
  The control pod's copy lacks node 1's newer sections (pool, pool-kinds, hill-climb), but those only run in the node1 group,
  so a straight replacement is safe.
- **Stale rows:** I'll delete `verity/prover-overhead-{prefill,decode}` and `verity/prover-gains` from the site DB once Daniel
  says yes.
