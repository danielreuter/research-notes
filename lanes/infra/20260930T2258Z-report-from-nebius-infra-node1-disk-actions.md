---
id: 20260930T2258Z-report-from-nebius-infra-node1-disk-actions
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Node 1 disk: what I cancelled, deleted and reprioritised (3:53–3:57 PM PDT), and the 87% watch

Authority: @circuits' yes (Slack `1790808725.558209`, verified as Verity's bot under @circuits) and root's authorization (3:52 PM
PDT). Details and the top writers are in @infra's thread (`1790807092.688879`,
[3:57 PM PDT](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790809011102349?thread_ts=1790807092.688879&cid=C0C5RCXL66N)).

| Time (PDT) | Action | Undo |
|---|---|---|
| 3:53 PM | Cancelled `cov-g058`'s Commit (Mistral-7B B8, run `r20260930-223330-fe90`) through `tele set-timeout`. It is recorded as `cancelled` (rc 137). | none needed: it reruns after #599's slim bundles (circuits) |
| 3:53 PM | Deleted `jobs/cov/cov-g058/mistral-7b…b8…/commit/replay_bundle_p0.partial`, 98 GB, which had no open files (`lsof +D`). | — |
| 3:54 PM | `deployments-gpu` was already `stopPolicy: Hold`. Someone else held it before I got there. | `sudo k3s kubectl patch clusterqueue deployments-gpu --type=merge -p '{"spec":{"stopPolicy":"None"}}'` |
| 3:54 PM | Relabelled 3 pending replays to priority `circuits-gpu` (600), ahead of Builds: `nd-n2-build-8b4f2c69f7-replay-0`, `nd-vllm-epoch-run-a1739cf4bf-replay-0` and `nd-vllm-epoch-run-cf44b210d9-replay-0`. | `kubectl label job <name> kueue.x-k8s.io/priority-class=circuits --overwrite` |

- **Not mine:**
  - The stale Phi-3 `.partial` bundles `phi3b8m` and `phi3b8f` (71 GB) were gone by 3:40 PM PDT.
  - `jobs/flock-sweep2/stage-cache` is gone, and `jobs/runs` fell from 221 to 81 GB. That was proofs' cleanup, about 90 GB.
- **Disk:** 73% at 3:56 PM PDT, written at about 310 GB/h over the last 5 minutes. It was 81% and 1,300 GB/h at 3:51 PM PDT.
- **Watch:** a 10-minute check of the disk.
  - At 87%, with no owner acting, I suspend the top-writing running Workloads (`spec.active=false`, deleting no Job or file) and
    post each name with its undo.
  - `vy-disk-guard` still holds every queue's new admissions at 90%.
- **Still to do (circuits' item 3):** make each new replay task outrank Builds. That means a `config-run.yaml` label change on
  `infra/nebius` and the dispatcher's copy.
