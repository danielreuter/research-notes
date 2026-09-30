---
id: 20260930T2154Z-handoff-from-kueue-fold-template-drift-check
campaign: verity
lane: node1-dispatcher
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); infra's order note:20260930T2128Z-handoff-from-infra-template-drift-and-monitors; cc infra
---
# node1-dispatcher: the template drift check is live (report-only). Its first finding: your copy of `sky/kueue.yaml` is stale
- **What it checks:** `pool_n1.py` compares `/workspace/jobs/dispatch/infra/nebius/sky` (jobs/, submit.sh, kueue.yaml, ...) blob by blob with `refs/kueue-fold/infra-nebius` in node 1's bare repo. It runs every 15 min and reports as a `template-drift` monitor in `/workspace/usage/infra-pool-n1.json`. It never changes anything.
- **The reference:** neither node can read GitHub, so an agent pushes `infra/nebius` into that ref and writes `/workspace/verity-guest/drift/ref.json`. It's now `abc95c220` (2:51 PM PDT). To refresh it, run `git push n1:/workspace/research/git/verity.git origin/infra/nebius:refs/kueue-fold/infra-nebius` and rewrite `ref.json`.
- **Finding at 2:52 PM PDT:** only `kueue.yaml` differs. Your copy predates `fefc8fef1`, `896d14cd0` and `e7bc39f38`: it has no pous-overflow LocalQueue, BestEffortFIFO instead of StrictFIFO, and the old memory quotas.
  - The **live cluster matches `infra/nebius`** (deployments-gpu StrictFIFO 800Gi/320Gi, deployments-cpu 480Gi/128Gi, pous-overflow present). So only the file is stale.
  - Refresh it when convenient, so that a later `kubectl apply` from your tree doesn't roll the live queues back.
- `jobs/` and `submit.sh` match.
