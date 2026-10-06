---
id: 20261006T1840Z-draft-home-cluster-platform
campaign: verity
lane: verity-top
kind: draft
status: open
repo: danielreuter/verity
origin: Daniel (drafted with another AI, not yet read closely by him), posted by top for review
---

# Home cluster: platform design (draft for review)

Oct 6, 2026 · Dan Reuter. Daniel's own note on it (18:38Z): he hasn't read it closely and it may contain things he doesn't
condone. The one thing he's sure he doesn't want is the five-week rollout: he wants to switch over as close to instantly
as possible, because the existing infra causes so many headaches.

## Summary

We rent a dedicated CPU fleet and make it the home cluster: one managed Kubernetes cluster whose desired state lives in
this repo and is applied automatically. Kueue is the only allocator for batch work on it, Buildkite runs our check steps
on it, and Coder gives each lane a warm workspace on it.

Everything generic becomes a standard, widely used tool. Everything that decides what counts as evidence stays ours and
runs on top unchanged: the gate, the evidence store, custody, the Lean pipeline, trains and timed windows.

GPU checks join the cluster in phase 4, and timed work moves to dedicated machines outside it. We are renting CPUs anyway,
so the first cluster we build should be the one we keep.

## First principles

The goal is research velocity: the time from an edit to a verdict we trust, and from there onto main. Five facts shape the
design:

- Compute is cheap next to wall-clock time and attention; cost is not the binding constraint.
- Agents build well and operate poorly: weak memory across sessions, nobody pages them, and they trust whatever is in the
  repo.
- More people, with their own agents, are joining.
- Testing across many kinds of hardware comes later.
- What counts as evidence must stay under our control.

| # | Principle | Because |
|---|---|---|
| P1 | Buy capacity and keep it warm; size statically for peak. | An autoscaled node starts cold: no .lake, venv or circuit index. |
| P2 | Desired state lives in git and is applied automatically. | Hand changes and stale descriptions (nebius.toml) are how the fleet drifted. |
| P3 | One allocator per machine. | Five allocators overlapping on the same machines is what hurts today. |
| P4 | Standard tools for generic plumbing; ours only where verification needs it. | Agents and new people already know standard tools; bespoke ones are relearned every session. |
| P5 | Nothing needs an operator. | No component may depend on a session staying alive; failures reach an owner as tickets. |
| P6 | Every action is attributable, with least privilege. | Agents read the cluster and change it only by PR; outsiders will check our evidence. |
| P7 | Measure, and change one layer at a time. | Shadow before cutover; metrics decide what stays. |

## What stays ours

The platform decides where and when our steps run, never whether a result counts. These stay as they are and run on top:

- `research run`, custody and Attempts, uploading to the evidence store on R2.
- The exact-commit gate in `research merge`, now also posted as a required GitHub status.
- `check.py`'s steps and their input-keyed caches.
- The Lean pipeline: lock, replay, `merge.py`, and the planned store-backed builds and per-module verdicts.
- Trains and `research merge --train`, plus bisect-and-drop (new).
- `gpu-lease --timed`, on the timing machines.

One addition: turn on retention locks for the evidence bucket, so nobody, including a confused agent, can delete or
overwrite evidence (R2 bucket locks; infra to confirm).

## Architecture

One managed cluster runs all batch work and all workspaces; only the timing machines and the evidence store sit outside
it. OpenTofu creates every machine shown, from main; inside the cluster, nothing changes except through Argo CD.

| Node group | Runs | Starting size (a guess; lanes to correct) | Allocator |
|---|---|---|---|
| System | Argo CD, Kueue, Buildkite's controller, Coder server, collectors, git mirror | 3 nodes, 8 vCPU / 32 GB | Kubernetes (system services only) |
| Checks | Every CI and research batch job | 8 nodes, 96+ vCPU / 768 GB, local NVMe | Kueue |
| Workspaces | One Coder workspace per lane | One node per lane (about 10), 64 vCPU / 512 GB, persistent disk | Coder, one workspace per node |
| GPU (phase 4) | vLLM suites, GPU smoke tests | Today's check GPUs | Kueue |
| Timing (outside) | Timed rows | 1 or more dedicated GPU hosts | `gpu-lease --timed` |

Sizing rule: the gate queue's p90 wait stays under 5 minutes at the busiest hour. Capacity changes weekly, by OpenTofu PR,
from that metric.

## Decisions at a glance

| Layer | Choice | Ruled out |
|---|---|---|
| Cluster | Provider-managed Kubernetes (Nebius) | k3s on node1; self-run HA k3s (fallback); Nomad; Slurm; plain VMs |
| Capacity | Static node groups | Cluster Autoscaler, Karpenter (for now) |
| Provisioning | OpenTofu | Terraform, Pulumi, Crossplane, CLI scripts |
| Cluster state | Argo CD | Flux (close second); deploys pushed from CI |
| Scheduling | Kueue | Volcano, YuniKorn, Slurm, Run:ai, our five allocators |
| CI | Buildkite's Kubernetes stack, through Kueue | GitHub Actions with ARC (close second); hosted runners; Jenkins; Argo Workflows; Tekton |
| Landing | Our trains, plus bisect-and-drop | Mergify, GitHub merge queue, Zuul |
| Workspaces | Coder | Codespaces, DevPod, our own research shell, VMs per lane |
| Access | Tailscale with SSO | SSH tunnels, raw WireGuard, Headscale, Teleport |
| Secrets | External Secrets Operator with a managed store | Vault or OpenBao, SOPS, Sealed Secrets |
| Images | One runner image, pinned by digest | Nix (for now), per-lane images |
| Caches | Node-local caches, a git mirror, sccache on R2 | Bazel remote cache |
| Observability | Grafana Cloud | Self-hosted Prometheus and Loki, Datadog, ELK |
| Alerts | GitHub issues for the owning lane | Slack only; PagerDuty (for now) |
| Hardware breadth (later) | SkyPilot or MultiKueue; tagged Buildkite agents | Building multi-cloud now |

## Decisions in detail

**Cluster: provider-managed Kubernetes.** Kubernetes, because Kueue, Buildkite's Kubernetes stack, Coder and Argo CD all
run on it, it restarts what dies, and agents and new people already know it (P4, P5). Managed, because upgrades, etcd
backups, certificates and control-plane HA are exactly the chores agents drop (P5). Same provider and region as the GPU
nodes, so a GPU node group can join later and traffic stays local. Ruled out: k3s on node1 (one control plane on a GPU
node is a single point of failure); self-run HA k3s, kubeadm or Talos (workable, but we'd operate the control plane; HA
k3s on three small VMs is the fallback); Nomad (weaker batch queueing, smaller ecosystem); Slurm (a poor host for Argo CD,
Buildkite's controller, Coder); plain VMs (back to writing allocators).

**Capacity: static node groups.** Size for peak and keep nodes up (P1). An autoscaled node boots cold. Capacity changes by
a one-line OpenTofu PR when the queue-wait metric says so. Ruled out for now: Cluster Autoscaler and Karpenter.

**Provisioning: OpenTofu.** The fleet becomes a file: every change is a PR with a plan diff (P2). It covers the cluster,
node groups, timing machines and buckets. State sits in a locked bucket; plans run on PRs and applies on merge, by the
platform owner until Buildkite is up. Ruled out: Terraform (non-open license), Pulumi, Crossplane, provider CLI scripts.

**Cluster state: Argo CD.** Keeps the cluster equal to `infra/cluster` on main: it reverts hand edits and removes what was
deleted (P2, P5). Vendor components from Helm charts; ours in Kustomize. `deploy.toml` stays only for machines outside the
cluster. Ruled out: Flux (no built-in UI; close second), deploys pushed from CI.

**Scheduling: Kueue.** Admission from quotas, placement left to Kubernetes (P3, P4). Resource flavors name hardware.
MultiKueue later. Shape: one cohort; a gate queue for tips, trains and tip-checks (highest priority, no preemption); one
queue per lane with quota, borrowing and fair sharing; jobs without a queue label are managed too; memory requests replace
"agents tagged by memory". Ruled out: Volcano, YuniKorn, Slurm/Slinky, Run:ai, our five allocators and the cluster agent.

**CI: Buildkite, through Kueue.** Hosted UI, logs, retries and API; agents on our machines (P4, P5). Its Kubernetes stack
turns each job into a Kubernetes Job that Kueue admits (P3). `check.py` generates the step list at run time. A final step
publishes the combined Attempt the gate reads. Ruled out: GitHub Actions with ARC (close second; static workflows and the
256-job matrix cap), hosted runners, Jenkins, Argo Workflows, Tekton.

**Landing: our trains, plus bisect-and-drop.** Grants carrying, conflict resolution in the tip and the exact-commit gate
are verification logic, so they stay ours (P4). Add bisect-and-drop and frozen heads, run as a Buildkite pipeline (P5).
Tip-check runs on every push to a ready PR. The gate's verdict becomes a required GitHub status, and only the landing
pipeline may push to main (P6). Ruled out: Mergify, GitHub merge queue, Zuul.

**Workspaces: Coder.** Persistent, template-defined workspaces on our cluster (P4), one per lane, disk keeps .lake, venvs
and the circuit index warm (P1). SSH with SSO identity (P6). Idle shutdown off. Ruled out: Codespaces, DevPod, our own
research shell over StatefulSets, one VM per lane.

**Access: Tailscale with SSO.** One WireGuard mesh to every machine, workspace and the Kubernetes API, identities and ACLs
in git (P2, P6). Agents get per-lane identities: read access plus submitting Jobs to their lane's queue; no exec into
shared services; an audited break-glass admin role. Ruled out: bastion plus SSH tunnels, raw WireGuard, Headscale,
Teleport (revisit for outside auditors).

**Secrets: External Secrets Operator with a managed store** (1Password or the provider's secret manager; pick in review).
Ruled out: Vault/OpenBao, SOPS, Sealed Secrets, env files on machines.

**Images: one runner image,** pinned by digest, recorded in each Attempt; later one per accelerator family. Replaces the
SkyPilot image the dispatcher uses. Ruled out: Nix (for now), per-lane images, `:latest`.

**Caches** where the reads happen, keyed by content (P1): Lean store-backed builds (1a) and per-module verdicts (1c) in the
evidence store; sccache on R2 for Rust; uv's cache on node-local disks; an in-cluster git mirror. A nightly uncached check
of main alerts on any disagreement with cached verdicts; if red, caching changes stop. Ruled out: Bazel remote cache or
remote execution.

**Observability: Grafana Cloud,** Alloy collecting from the cluster and timing machines. A small exporter of ours builds the
velocity dashboard (edit-to-verdict p90, ready-to-main p90, tip failures by cause, queue wait by flavor, manual
interventions per day). Ruled out: self-hosted Prometheus and Loki, Datadog, ELK.

**Alerts: GitHub issues for the owning lane,** deduplicated, with a runbook link and a Slack copy. Ruled out: Slack-only,
PagerDuty (for now).

**Machines outside the cluster.** Timing machines: dedicated GPU hosts, never in the cluster (Kubernetes daemons add timing
noise); `gpu-lease --timed` their only allocator; OpenTofu creates them, `deploy.toml` configures them. Today's GPU nodes:
extended, and kept on today's path until a GPU node group exists; one may become a timing machine. Hardware breadth later:
SkyPilot or MultiKueue; Buildkite agents tagged by hardware; each Attempt records a hardware fingerprint.

## Rollout (as drafted)

Five phases over about five weeks, one cutover each; a phase starts only when the gate above it has passed. Each phase
also merges its deletions. **Daniel does not want this pace: see the top of this note.**

## Operating rules

Ownership (one platform lane owns `infra/` via CODEOWNERS); PRs only (Argo CD reverts anything else); one in, one out;
shadow first; owned alerts; metrics decide (an infra project with no movement after three weeks in shadow is cut); cache
canary.

## Deletion schedule

| Mechanism | Replaced by | Deleted in |
|---|---|---|
| Cluster agent | Kueue | Phase 1 |
| nebius.toml as the fleet description | OpenTofu | Phase 1 |
| fill_runner, dispatch, keeper | Kueue | Phase 3 |
| sky/ templates and the SkyPilot image | Runner image | Phase 3 |
| Quick-tier tmux chains | Buildkite pipelines | Phase 3 |
| runpod.py, leases, guards and remote.py shipping, for CPU work | Home cluster | Phase 3 |
| deploy.toml for anything in the cluster | Argo CD | Phase 3 |
| Lander VM | Landing pipeline | Phase 4 |
| n1_lease, k3s on node1, gpu-lease as a scheduler | Kueue GPU flavors | Phase 4 |
| Website /api/jobs and /api/trains views | Buildkite and Grafana | After phase 4 |

## Questions for reviewers (from the draft)

| Who | Question |
|---|---|
| infra | Does Nebius managed Kubernetes support our node groups (high-memory CPU with local NVMe, persistent disks), OIDC login and, later, our GPU type? If not, is HA k3s the right fallback? |
| lean | What shapes does Lean need on check nodes and workspaces (cores, memory, disk)? Can store-backed builds (1a) land before the phase 2 pilot? |
| circuits | How do per-target memory caps map to Kubernetes requests and limits? What does the largest target need? |
| proofs | What resource shape does sharded replay want? |
| compute-accounting, memory-accounting | Which existing node holds the reference rows and should become the timing machine? Does any timed work need more than one machine? |
| network-accounting | Do network measurements need a pair of quiet machines, also outside the cluster? |
| ci, lander | What pipeline shape do trains and bisect-and-drop need, and how should shadow verdicts be compared? |
| All leads | Is the starting size right? Does anything have to run outside Kubernetes? Does anything here break a property you named as must-survive? |
| Dan | Approve the accounts (Buildkite, Tailscale, Grafana Cloud, the secret store) and the starting size under Architecture. |
