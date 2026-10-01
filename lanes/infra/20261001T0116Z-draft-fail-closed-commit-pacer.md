---
id: 20261001T0116Z-draft-fail-closed-commit-pacer
campaign: verity
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: steward pacer (bc-af6a305f), for infra (bc-17cc41f1); answers note:20261001T0030Z-handoff-from-infra-fail-closed-pacer-plan (item 3 of note:20260930T2355Z-handoff-from-circuits-workflow-fixes)
---

# Cutover: node 1's Commit pacing fails closed (a Kueue AdmissionCheck answered by `commit-pacer.service`), waiting on Daniel's yes

**Nothing below is live.** release.py is still pacing from tmux `commit-release` on node 1, unchanged by me. Code and tests are on
branch `cursor/fail-closed-commit-pacer-7b8f`, off `infra/nebius`, at `c41579dc5`: the label is `5ecac2541`, the pacer
`a70d46f7e`, and the merge of `infra/nebius`'s tip is `c41579dc5`. The scratch-cluster evidence is `art:593130e2b58db5519c3ccd9793ec9e09cea151cc97e4d13d7525c3b9ec98bdd7`.

## What changes, in one paragraph

Node 1 runs **Kueue v0.19.6** (API `kueue.x-k8s.io/v1beta2`) on **k3s v1.36.4+k3s1**. In that version, an AdmissionCheck has a
custom `controllerName`, and its controller writes the Workload's check state through the status subresource. So an "external
AdmissionCheck controller" and "the pacer patching the Workload's admission-check state" are the same mechanism. The pacer is the
controller.

Kueue can't scope a check by label: a ClusterQueue scopes its checks only by ResourceFlavor (`admissionChecksStrategy.admissionChecks[].onFlavors`),
and node 1 has one flavor. So the check goes on all of `deployments-gpu`, and Commits are selected by label in two places:
- **The pacer** marks every other workload Ready at once.
- **A MutatingAdmissionPolicy** creates labelled Commits inactive, so a waiting Commit holds no quota. (A Workload Pending on a
  check keeps its reservation, borrowed cohort quota included, and on scratch that blocked a `provers` job.)

If the pacer is down, nothing new in `deployments-gpu` starts, and `provers` is untouched.

## 1. The AdmissionCheck

Objects (`tools/research/src/research/pods/nebius/commit-pacer-admission.yaml`):
- **AdmissionCheck `commit-pacer`,** with `controllerName: verity.dev/commit-pacer`.
- **MutatingAdmissionPolicy `commit-arrives-inactive` and its binding.** On a Workload's CREATE in `deployments-gpu` whose pod set
  carries `verity.dev/stage: commit` and a `verity.dev/workstream` in circuits' three, it adds `/spec/active: false`, with
  `failurePolicy: Fail`. It is built into the API server (`admissionregistration.k8s.io/v1`), so there's no webhook server to keep up.
- **The ClusterQueue patch** that attaches the check, applied as a separate step:
  `{"spec":{"admissionChecksStrategy":{"admissionChecks":[{"name":"commit-pacer"}]}}}`.

**Which Workloads are Commits.** A Commit's pod set carries `verity.dev/stage: commit`. Commit `5ecac2541` adds the label to
config-run's gpu task and to config-run-row, and a hand copy of the Job keeps it. A pinned item from before the label is
recognized by its Job: task 1 of config-run, or task 0 of config-run-row.

A Commit is **paced** when its workstream is `vllm-epoch-run`, `n2-build` or `vllm-coverage-defs`, as in release.py. The
workstream comes from the item key, or else from the pod label `verity.dev/workstream`, so a copy without annotations is still paced.

**What only the pacer marks Ready:**
- every workload that isn't a paced Commit (the reason it gives is "not a paced Commit");
- every workload that is already admitted (Commits running at cutover keep running: on scratch they got the check as Pending
  and stayed Admitted);
- and its own releases, once Kueue reserves their quota.

It deactivates any other paced Commit, a hand reactivation included. It keeps the AdmissionCheck `Active` and never sets it
inactive: Kueue stops the whole ClusterQueue while a listed check is inactive, which I verified on scratch.

**The rule** (`decide` in `commit_pacer.py`, one test per clause). The rule moved while I wrote this: circuits raised the bundle cap
at 6:04 PM PDT and the in-flight limits at 6:09 PM PDT. So the pacer carries release.py's current rule (md5 `535db739`, running
since 01:09:08Z), not the 150 GB, 3 and 2 of the handoff. A waiting Commit is released, in circuits' wave order and then by batch,
only while all of these hold:
- `/workspace` is under 80%, as df reports it;
- fewer than 6 paced Commits are in flight (released or admitted, and unfinished);
- it is below batch 8, or fewer than 4 Commits at batch 8 or above are in flight;
- the bundles on disk, plus what the in-flight Commits have yet to write, plus its own estimate, fit the cap. The cap is 300 GB,
  and 150 GB from the first time the disk reaches 78% (a latch file, `cap-150`). The estimate is infra's 120 GB × batch/8 ×
  tokens/1152, scaled by the model's hidden size × layers against Phi-3-mini's, with a 10 GB floor;
- it isn't kept: on the keep-list, at batch 64, or at batch 16 or above of a 7B+ or MoE model.

A tick whose disk or bundle reading failed releases nothing. That is stricter than release.py, whose failed bundle reading counts 0.

The clauses are code. The six limits are defaults that `/etc/default/commit-pacer` can override (`PACER_MAX_INFLIGHT=6`, etc.), and
`run` logs the rule it starts with. With three edits to the rule in 70 minutes, a ruling becomes a one-line edit and a restart.

**It agrees with release.py today.** I piped `commit_pacer.py once --mode hold --dry-run` over stdin on node 1, reading release.py's
own state files. It wrote nothing and patched nothing. At 01:14:00Z it printed `cap 300 GB, disk 71%, in flight 4, batch-8+ 4,
bundles 68 GB, projected 288 GB` and the same ten waiting Commits as release.py's 01:13:07Z tick.

## 2. `commit-pacer.service`

These files are in `tools/research/src/research/pods/nebius/`:
- **`commit-pacer.service`:** `ExecStart=/usr/bin/python3 /usr/local/lib/commit-pacer/commit_pacer.py run --every 10`,
  `Restart=on-failure`, `RestartSec=10`, `After=k3s.service`, and `EnvironmentFile=-/etc/default/commit-pacer`.
- **`commit-pacer-cleanup.service` and `.timer`:** hourly, nice and idle I/O.

The pacer runs as root: `k3s kubectl` needs it, and so do `du`, `find` and `lsof` across every bundle directory. A failed tick
(kubectl, du, a bad Workload) is caught and logged, releases nothing, and is retried at the next tick, so the process exits only
on a crash, which `on-failure` restarts.

Its state lives in `/var/lib/commit-pacer/`:
- `released` and `seen-inactive`, in release.py's format;
- `cap-150`;
- `commits.json`, used by cleanup.

The modes:
- **`hold`** is release.py's behaviour, under systemd.
- **`gate`** adds the check.

`commit_pacer.py status` lists every unfinished Commit: running, waiting or queued, its check state, and the pacer's reason.

## 3. Failed-Commit bundle cleanup

A replay bundle is `intermediate`. On success its replay job deletes it; after a failure it stays 6 h for triage.

A Job is deleted 6 h after it ends (`ttlSecondsAfterFinished`), which is the same 6 h, and circuits' items never pass through
`taken/`. So the pacer records each Commit's item key and commit directory (`SWEEP_DIR/ROW/commit`) in `commits.json` while it
can still see the Commit.

`commit_pacer.py cleanup --delete` removes `<commit dir>/replay_bundle_p<N>[.partial]` under `jobs/cov` or `jobs/probe-jit` only
when all of these hold:
- every recorded item of that directory ended **failed** (its last `done.jsonl` line) **at least 6 h ago**;
- **nothing queued names the directory:** no unfinished Job in any queue, no ready item, and no pack-spool entry, queued or
  claimed. A retry under a new item id writes to the same directory, so it counts;
- **`lsof +D` is clean** (exit 1, no output);
- the real path is inside a bundle root.

It deletes with `nice`/`ionice rm -rf`, and each deletion is a line of the hold log. A bundle that no recorded item owns is never
deleted, so bundles from before the cutover stay the steward's, by hand.

On scratch, cleanup listed a fake failed bundle, kept it while `tail -f` held a file open, then deleted it and logged the deletion.

## 4. Cutover (after Daniel's yes; every step reversible)

0. **Merge and check the rule.** Merge the branch into `infra/nebius`. Re-run the dry run and compare it with release.py's last
   tick line:

   `sudo env PACER_KUBECTL="k3s kubectl" PACER_STATE=/home/research/commit-release python3 - once --mode hold --dry-run < commit_pacer.py`

   If release.py has changed since `535db739`, port the change first, or set the override.
1. **Install, no behaviour change.** Copy `commit_pacer.py` to `/usr/local/lib/commit-pacer/` and the three units to
   `/etc/systemd/system/`. Create `/etc/default/commit-pacer` with `PACER_MODE=hold`. Run `systemctl daemon-reload`.
2. **Swap the pacer, still in hold mode.**
   - Stop release.py (`C-c` in tmux `commit-release`).
   - Copy `released`, `seen-inactive` and `cap-150` (if present) from `~research/commit-release/` to `/var/lib/commit-pacer/`.
   - Run `systemctl enable --now commit-pacer`.
   - Check the first `journalctl -u commit-pacer` tick against release.py's last line.

   This is release.py under systemd, with `Restart=on-failure`.
3. **Gate.**
   - `k3s kubectl apply -f commit-pacer-admission.yaml`. The AdmissionCheck has no status yet, and nothing references it.
   - Set `PACER_MODE=gate` and run `systemctl restart commit-pacer`. Expect `marking admissioncheck commit-pacer Active` in the
     log, and `Active=True`.
   - Patch the ClusterQueue to attach the check.
   - Confirm `deployments-gpu` stays `Active=True`, and that running workloads stay Admitted and get Ready ("admitted") within a tick.

   This order matters: a ClusterQueue that references an inactive check admits nothing.
4. **Turn on cleanup.**
   - Review one `commit_pacer.py cleanup` listing (it deletes nothing).
   - Run `systemctl enable --now commit-pacer-cleanup.timer`.
5. Write a line in the hold log for each step.

On scratch I ran the whole sequence from today's state (no check, one B8 Commit admitted), with the files exactly as committed,
and every behaviour above held.

## 5. Stop and roll back

**Back to today's admission, keeping the pacer** (the handoff's item 4):
1. Set `PACER_MODE=hold` and run `systemctl restart commit-pacer`. Unreleased Commits are now held by deactivation, not by the check.
2. Remove the check from the ClusterQueue:
   `k3s kubectl patch clusterqueue deployments-gpu --type=json -p '[{"op":"remove","path":"/spec/admissionChecksStrategy"}]'`.
   Kueue admits at once everything that was Pending on the check, so step 1 comes first.
3. Delete the policy binding, then the policy, then the AdmissionCheck.

On scratch, after this, a non-Commit that was Pending on the check was admitted at once, and every Workload's `admissionChecks`
was empty. Running Commits were untouched, held ones stayed inactive, and hold mode went on releasing by the rule.

**Back to release.py in tmux:** do the steps above, then:
1. `systemctl disable --now commit-pacer commit-pacer-cleanup.timer`;
2. copy the three state files back to `~research/commit-release/`;
3. start release.py in tmux as before.

**If the pacer is down and must stay down:** do steps 2 and 3. Commits that the policy created inactive stay inactive until
something activates them; list them with `k3s kubectl get workloads` (inactive ones show no RESERVED IN).

`vy-disk-guard` (90%) and `vy-quiet-hold` hold queues through other ClusterQueue fields. The pacer's patch touches only
`admissionChecksStrategy`.

## 6. What breaks for circuits while it's live

**A Commit created by hand waits instead of running.** That covers a copy of a Job, a resubmission and a reactivation; today they
are admitted in the same second if GPU quota is free. Another live case of that leak: `95dbf07b36` (Llama-3.2-1B TP2 B8) was admitted
at 01:08:35Z without release.py releasing it. They'll see a waiting Commit in four places:
- **On the Workload:** the annotation `verity.dev/commit-pacer`, `held <utc>: <reason>`. For example, `held
  2026-10-01T01:03:31Z: 2 Commits at batch 8+ in flight (max 2)`, or `kept (keep-list, batch 64, or batch 16+ of a 7B+/MoE model)`.
  It is rewritten only when the reason changes, and says `released <utc>: ...` once released.
- **In the Workload's conditions:** a held Commit shows `QuotaReserved=False`, "The workload is deactivated" (plus `Evicted=True,
  reason Deactivated` if it had reserved quota), and `kubectl get workloads` shows no ADMITTED. A Commit whose quota is reserved
  but whose check isn't passed shows `status.admissionChecks[commit-pacer].state=Pending`. Its Job stays `suspend: true`.
- **`sudo python3 /usr/local/lib/commit-pacer/commit_pacer.py status`** prints one line per Commit: running, waiting or queued,
  with its check and reason.
- **`journalctl -u commit-pacer`** has one line per decision: `hold`, `activate`, `ready`, each with its reason, plus a tick
  summary when it changes or once a minute.

Also:
- A Commit the pacer released, or one already running, behaves as today.
- A kept Commit never runs (as today).
- Nothing waits on circuits to act.
- A wait can be overridden only by the rule. To force a Commit, change the limit in `/etc/default/commit-pacer`, or roll back
  (section 5).

## Decisions and residuals (for Daniel, infra and circuits)

1. **Other workloads in `deployments-gpu` pass through the check.** commit-pack pods and prover-dev items (one today) wait up to
   one tick (10 s) for Ready, and they wait as long as the pacer is down. The alternative is a separate ClusterQueue for Commits
   in cohort `nebius`, which leaves `deployments-gpu` exactly as today. But it splits the queue's quota and touches the
   dispatcher's depth, the exporter, the disk guard and the quiet hour. **I recommend the single queue.**
2. **Scope (circuits' call).** Only circuits' three workstreams are paced, as in release.py. `mps-golden*` and `vllm-staging-bug`
   Commits are passed. To widen: set `PACER_SCOPE=*` and the policy's workstream list (a test keeps that list equal to the code's).
3. **Commits inside commit-pack pods** aren't seen as Commits: the pod's Workload is commit-pack's. They stay under `PACK_PODS`
   and the pack's own 80% pause, and their bundles do count in the bundle reading.
4. **Pinned items from before the label** are still gated, by their template and task, but the policy doesn't catch them. They
   arrive active and hold quota, though never start, until the next tick deactivates them.
5. **Not recognized:** a Job written from scratch with neither the label nor config-run's annotations isn't a Commit, and is passed.
6. **The dispatcher's pending count** (no `status.admission`) treats a workload whose quota is reserved but whose check is Pending
   as admitted. That lasts at most a tick for non-Commits; inactive Commits count as pending, as held ones do today.
7. **The rule keeps moving.** Step 0 of the cutover re-checks it.

**Blockers:**
- Daniel's yes.
- Decision 1 (my recommendation: one queue).
- Circuits' answer on scope (decision 2): the plan works as is with today's scope.
- The branch merged into `infra/nebius` before step 1.
