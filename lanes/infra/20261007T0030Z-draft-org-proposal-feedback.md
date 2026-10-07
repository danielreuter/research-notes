---
id: 20261007T0030Z-draft-org-proposal-feedback
campaign: verity-repository
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: top's announcement 1791331591.766669 (Daniel's "Verity repository" + CI, Security, Platform design; art:8ae63b72a5e911c1fd44c4e7606dc4449a2744a52561965d4265af00886d16a5)
---

# infra on "Verity repository": the Platform page, the `research` split, "nothing imports infra/"

## 1. Where infra's code goes

Today `tools/research/src/research` is one distribution doing three jobs. Split by who needs it:

- **tools/ (any clone, no secrets): the run-store client and the run record.** `store/` (local, remote, ids, custody,
  preserved, labels, vocab), `record.py`, `result.py`, `runs.py`, `compare.py`, the `fetch`/`inspect` commands. Custody stays
  here: it is "a run uploads its record as it goes", which a laptop run needs too. `tools/check` already imports
  `research.store.custody`, `research.store.remote` and `research.runs` (preflight.py, post_train.py), so the store client must
  sit on the tools/ side or `verity check` imports infra/.
- **infra/: running our machines.** `pods/nebius/*` (deploy.toml, the systemd units, gpu-lease, fill_runner, the Lean sandbox,
  write/preflight probes, n1/n2 custody, keeper, node sweep, monitoring), `tools/cluster`, `deploy.py`, `disk.py`, `mem.py`,
  `jobuser.py`, `keeper.py`, `steward.py`, `retention.py` (gc and node-local keep records), `monitors.py`.
- **infra/messaging:** `slack.py`, `notes*.py`, `approaches.py` (comms' answer covers the Slack side).
- **Retires to standard tools, no home needed:** `queue.py` (grants, carry), `merge.py` (trains, prepare), `quick_tier.py`,
  `gates.py` → GitHub's merge queue + Buildkite; slots, `fill/windows`, gpu-lease → Kueue (gpu-lease stays only if the
  re-timing test fails); `monitors.py` and the alert loops → Grafana alerting; `deploy.py` → Argo CD.

**No home:** the Lean build sandbox (`vy-lean-sandbox`) and the daily cache publisher. The cache *key and format* must be in
tools/ (`verity check lean` reads it on any clone), the *producer* is infra/. Lean put the unit in infra/; the key goes with
the check.

## 2. Rules that would break or slow infra's work

- **"Nothing imports infra/"** breaks in four places today: `spec_alert.py`, `monitors.py`, `n1_alerts.py`,
  `preflight_probe.py`, `write_probe.py` import `slack.py`; `check.py` imports `research.remote` and `--record` goes through
  `research run`. Change: `verity check` writes its run record and any alert as records in the run store; the platform
  runner (infra/) wraps it, signs the record and delivers alerts. Then infra/ imports tools/, never the reverse, and a check
  runs byte-identically on a laptop and on the cluster. tests/infra may import infra/.
- **"Desired state lives in git; the repo is the only way to change the platform"** conflicts with what keeps nodes alive
  at night. Tonight alone: relocating `.lake/packages` for inodes (21:24Z), releasing a booked window by editing
  `fill/windows`, killing a hung probe. With Argo self-heal a hand fix gets reverted. Change: a break-glass hand fix is
  allowed, filed as an incident, and reconciled into git the same day (Argo's drift report lists what's outstanding).
- **"Capacity is static, sized from measured peaks"** misses inodes. Node 1 went 65% → 74% of inodes in 30 min tonight with
  4-5 concurrent checks (each exported tree + Lean `.lake` ≈ 330k inodes; `research/scratch` 4.1M, `cache/verity-check`
  3.0M, `jobs` 1.6M) while bytes sat at 67%. Kubernetes' `ephemeral-storage` counts bytes, not inodes. Change: each check
  gets its own volume (an XFS project quota or a per-job PVC) with an inode limit, and eviction counts inodes;
  `vy-store-evict` today is byte-only.
- **"The LMS key stays on node 2; only jobs that need it may run on that node"** collides with node 2 as the first quiet
  node and with every platform-signed run on node 1 or the cluster needing a signature. Change: a signing service on node 2
  with one narrow call (sign this run digest), the key readable only by its own Unix user, so other jobs may share the node
  and nothing else ever reads the key.
- **"Day one: run today's check on the new check nodes unchanged"** can't be literal. `vy-lean-sandbox` runs as root through
  `sudo -n` and builds in a transient systemd unit (user `lean-build`, no network, nothing writable outside the tree), and a
  pod has neither sudo nor the host's systemd. In a pod, the same properties are its security context (`runAsUser`, no
  network policy, read-only root, one writable volume), so the sandbox retires into a pod spec, but its probes, run inside
  before every build, should stay as the check's first step. PoUW's timed rows also lock GPU clocks, which needs a
  privileged pod on the quiet nodes. Plan both before day one, or day one fails on the sandbox, not on verdicts.
- **"Next day: delete what the shadow replaced"** is fine, provided the inventory lists node 1's units first:
  vy-custody, vy-store-evict(-research), vy-lean-cache-daily, vy-keeper, vy-node-sweep, vy-steward-watch, vy-alert-sink,
  vy-exporter, vy-lease, infra-pool-publish. Each becomes a CronJob/DaemonSet or is deleted, and the list is the checklist.

## 3. What's wrong about infra's area today

- Node 1 already runs **k3s** (single node), and it owns all 8 of node 1's GPUs (`/etc/vy/direct-gpus`: none). They sat
  at 0% all evening. "GPU work moves in later, as a node group made from node 1" is half done already; the "pod holds a
  GPU at 0%" alerts come from it.
- **Grafana already runs** self-hosted on node 1 (alerting rules in `pods/nebius/monitoring/alerting.yaml`, `alert_sink.py`).
  Grafana Cloud replaces it; the rules move, not start from zero.
- "Five mechanisms decide who gets a GPU": today they are gpu-lease, the `fill/windows` booking file, the slot leads in
  `locks/slots`, node 1's k3s, and the cluster agent in shadow mode. Kueue replaces the first three and the fifth.
- Naming: infra borrows research words in `fill/windows` (a booking, not a PoUW window), the Lean *audit* (`tools/lean/audit.py`
  → `verity check lean`), and grants. The sweep should rename these with the rest.
- Retention: "whatever a ref points to is kept" misses node-local data (compute-accounting's 28 GB). Today's
  `research keep` records are exactly a node-local ref; make a keep record a ref with a location so there is one retention
  rule (PR #1418 already refuses `retention rm` of passes without a preserved artifact).

## 4. The one change

Put the run record, custody and the store client in tools/, and make the platform runner in infra/ a wrapper that runs
`verity check` unchanged, signs its record and delivers its alerts. That makes "nothing imports infra/" true without
moving anything else, makes "it runs anywhere with no store and no secrets" literal, and gives the shadow test its
criterion: the same command, the same record, only the signature differs.
