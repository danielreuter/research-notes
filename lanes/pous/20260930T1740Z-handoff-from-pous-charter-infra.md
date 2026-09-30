---
cursor:
  subagentId: "bc-27b53f62-e217-5187-8bc2-6e76e43f7085"
id: 20260930T1740Z-handoff-from-pous-charter-infra
campaign: verity
lane: pous
kind: handoff
status: open
repo: verity
origin: pous
---

# Handoff to the infra coordinator: pous's infra pieces

For the infra subcoordinator in Daniel's one-Project structure: utilization, the scheduler, buying compute, and one API for
agents' task infra (`note:20260930T1725Z-handoff-from-pous-coordinator-project-restructure`). State as of 30 Sep 17:35Z. Paths
follow the pouw charter's conventions (`note:20260930T1740Z-handoff-from-pous-charter-pouw`); bare paths are in the pous Project
store `/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/`.

Everything here concerns node 2 (`vy-nebius-2`: 8× RTX PRO 6000, `research@81.85.2.121`). It stops itself at
2026-10-07T14:55Z. None of the work below has changed anything on either node.

## 1. Node-2 ops: bc-efe47341-6cdf-5f91-a26b-d3946ca153b5 (RUNNING)

- **What it owns:** node 2's operations, which Daniel put with pous at 06:53Z. That covers:
  - `gpu-lease`, with memory caps and preemption;
  - the fill queue and its runner;
  - the OOM guard and the alerts;
  - hourly backups to the store;
  - the per-minute status page and the 10 s sampler.
- **Where it's written down:**
  - how it runs and the sharing rules: `docs/pouw/compute-plan.md`, § "Ops" and § "How node 2 is shared";
  - the live page: `/workspace/pouw/infra/status.md` on the node;
  - the numbers: `internal/pouw/infra/utilization-report.json`.
- **State:** 38% GPU-busy for 16–17Z, against an 80% target.
  - The cause is GPU work the lanes haven't written. Infra doesn't pad the queue (the pous root's ruling, 15:27Z).
  - About 1,327 GPU-h were left at 17:03Z.
- **Shared code:** `infra/nebius` ([#496](https://github.com/danielreuter/verity/pull/496)) is the one branch shared with Verity.
  - Its rules and file owners: `docs/pouw/compute-plan.md`, § "Sharing infra with Verity".
  - Lessons: research-notes `lanes/nebius-infra/lessons.md`.
  - Urgent pings go on [#494](https://github.com/danielreuter/verity/pull/494).
- **In flight:**
  - the `gpu-lease` per-lease usage report, report-only (one-cluster phase 1a,
    `note:20260930T1727Z-reply-from-pous-infra-to-pous-one-cluster-phase-1`);
  - a pause of `research run` samplers during timed windows, live since 17:25Z
    (`note:20260930T1725Z-handoff-from-pous-infra-to-pouw-no-sampler-timed-runs`);
  - an NVML A/B inside a timed window, which bc-2aa33ad8 asked for at 17:27Z.
- **Verity's side of the servers** (status at 17:35Z):
  - the nebius-infra steward, bc-fd19a2fe-4dd1-5d17-b138-509b5268e910 (IDLE);
  - the Nebius owner, bc-96a2e856-76ff-54b4-a303-b9b1e0a69896 (IDLE): launch, lease, deadline and clocks;
  - the Kueue owner, bc-c445c55b-453a-5b6a-b6a1-f6fe3d1eda07 (IDLE);
  - node 1's dispatcher, bc-70706bc3-bf17-5315-9276-4811c214ffee (IDLE);
  - the research coordinator, bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628 (waiting on background work).

## 2. One-cluster design: bc-c3ade0aa-358b-5271-a050-adadf3997e9f (IDLE)

- **The design** is `docs/infra/one-cluster.md`. It recommends running nodes 1 and 2 as one cluster:
  - one description, one allocation ledger and one failure feed;
  - scheduling authority stays with each node;
  - SSH stays for interactive work;
  - observability is report-only (§1).
- **The foundation** is [#586](https://github.com/danielreuter/verity/pull/586), a draft: `tools/cluster/` with the description,
  planner, router, ledger and simulation tests.
- **Four decisions for Daniel** (§1):
  1. **Cross-node borrowing.** May Verity's work use node 2's idle GPUs, not only its CPUs? May PoUW's untimed fill use node 1's?
  2. **Cutover appetite before 7 Oct:** shadow runs only, or replace node 2's `gpu-lease` and fill runner with the node agent
     between panel series?
  3. **Identity:** one SSH CA with per-agent certificates. Who holds its key?
  4. **Node 1's Kueue:** does it stay as the container runtime for vLLM deployments under the node agent, or do those move to host
     processes?
- **Replies to its requirement asks:**
  - pous infra, `note:20260930T1721Z-reply-from-pous-infra-to-pous-one-cluster`. It also said yes to phase 1b's shadow runs, on
    conditions, in the phase-1 note above.
  - the RTX PRO coordinator, `internal/pouw/infra/one-cluster-rtx-pro-answers.md`. It wants the submission command changed only
    after 7 Oct, or `gpu-lease` kept as an alias.
  - Verity's research coordinator, `note:20260930T1722Z-reply-from-verity-root-to-pous-one-cluster`. It marks which points need
    Daniel, and recommends that Daniel hold the CA key.
  - **Still missing:** the steward's reply to `note:20260930T1640Z-handoff-from-pous-one-cluster-to-nebius-infra-steward-requirements`.
  - None of the replies is folded into the doc yet; §2 and §15 still say "pending".
- **Next** (§14):
  - 1a, the usage report: pous infra is building it.
  - 1b, read-only shadow runs: this needs the steward's yes as well as ours.
  - 1c, `research run` connection reuse and streamed logs: this needs the research coordinator's review.
  - Phases 2 and 3 change nodes, so each needs a written cutover plan that goes to Daniel first.

## 3. Live-console exporter: bc-26712550-34fa-5920-b821-a24a22ab3f5a (IDLE)

- **What exists:**
  - the code, in `code/live-console/`: `export.py`, `run.sh` and `request-key.sh`;
  - the eleven panels and their sources, in `internal/live-console/pous-panels.md`;
  - the dry run passes on all eleven.
- **Where it runs:** armed on bc-26712550's VM, in tmux `live-console-publish` and `live-console-key`. The key file lives only on the
  host that asked for it.
- **What blocks it:**
  - The scope stays `panels:write`. The site code that adds it is finished on the website branch `cursor/live-console-de55`.
  - The deploy waits on Daniel's go-ahead. After it, Daniel approves the key at /approvals (`note:20260930T1718Z-handoff-from-verity-root`).
  - Verity root asked us to stop the 15-minute key retries, and to ask once after it posts in `lanes/pous/` that the deploy is up.
    The sources don't say whether the retry loop has been stopped.

## 4. Spare CPU on node 2 for Verity: interim terms with the nebius-infra steward

- **The notes:**
  - the ask: `note:20260930T1620Z-handoff-from-nebius-infra-steward-to-pous-infra-spare-cpu-ask`;
  - our terms: `note:20260930T1629Z-reply-from-pous-infra-to-nebius-infra-steward-spare-cpu`.
- **The gist:** Verity's CPU-only jobs run through our fill queue as `project=verity`, in a pool of their own:
  - CPUs 48–95;
  - capped memory;
  - frozen during timed windows;
  - their data in `/workspace/verity-cpu`;
  - all of it removed before the stop.
- **Status: agreed on pous's side, not deployed.**
  - The enforcement is written and tested, and waits for a path to be chosen.
  - The access half, a restricted node-1 key on node 2, needs Daniel's explicit yes. The pous root was asking him at 16:29Z, and
    no answer is recorded.
  - The one-cluster design's queue-only certificates could replace the key route.

## 5. GPU budget

- **Nebius:** node 2 is paid from Verity root's Nebius budget, and pous creates no Nebius resources.
  - The spend alerts are about $800/day and $24k/month. Both servers together run about $710/day
    (`note:20260930T1502Z-handoff-from-nebius-infra-steward-to-pous-infra-hard-stop-oct-7`).
  - `notes.md` says Daniel is to raise those alerts.
- **The bound is the node's self-stop** at 2026-10-07T14:55Z, from the deadline file on the node, never from a scheduler.
  - The sources give no dollar cap for node 2 since Daniel's extension to 7 Oct.
  - The last cap on record was root's $450 overnight ceiling.
- **RunPod:** no pous line is live in research-notes `budgets.toml`.
  - Root approves no new pod spend; a new line needs Daniel's budget, through root
    (`note:20260930T0930Z-handoff-from-verity-root-spend-lines-nebius`).
  - Today's pous RunPod spend is about $2.5, all on CPU check pods.
- **Rules for any pod:**
  - only under a `budgets.toml` line, with `--max-hours`;
  - a kill timer on the pod itself;
  - terminate idle pods without asking.

## 6. Pending asks

- **For Daniel** (decisions, through the top-level):
  - the four one-cluster decisions, and whether Verity gets a standing share on node 2;
  - yes or no on the spare-CPU access;
  - the site deploy, then approving the panels key;
  - rotating the Nebius key: fragments were possibly exposed in two worker terminals today, and rotation is his call;
  - raising the Nebius budget alerts, if he still wants to.
- **Owed to infra:**
  - the steward: its one-cluster reply, its yes on phase 1b, and the path for spare CPU;
  - the research coordinator: a review of phase 1c;
  - Verity root: a note in `lanes/pous/` once the deploy is up.
- **Owed by infra:**
  - bc-efe47341: the usage report's commit and deployed sha256, and the NVML A/B. It keeps asking bc-2aa33ad8 for GPU supply
    (asked at 15:25Z, 16:09Z and 17:10Z).
  - bc-c3ade0aa:
    - fold the replies into §2, §8 and §10;
    - read node 2's GPU-to-NUMA topology, which is assumed today to match node 1's;
    - settle whether a timed window gives a session a grace period.
  - bc-26712550: stop the key retries.

## Standing rules

- The pouw charter's list applies unchanged.
- **Access:** no access change without Daniel's explicit yes.
- **Live nodes:** no change to a live node without a written cutover plan brought to Daniel.
- **Secrets:** never print them.
- **Velocity:** SSH is fine for interactive work.
- **Spend:** a guard never fails open, and nothing that bounds spend or preserves results depends on an agent VM.
