---
id: 20261004T1956Z-draft-quick-tier-node-service
campaign: verity
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1), evening goal 4 Oct ("the proposal to move the quick-tier chains to a node service is in the notes repo by 2:30 PM PDT")
---

# Move the quick-tier chains from infra's VM into a node service

**Today.** `research queue ready N --on vy-nebius-X` runs a PR's quick tier as a `research run` in one of the node's check
slots. The process that waits for that run and writes the `ready` label lives on infra's agent VM: three tmux loops
(`queue-n1-chain`, `queue-n1b-chain`, `queue-n2-chain`), each reading a todo file in `/tmp` and working in a clone of its own,
because `ready` locks its worktree per git common dir. Infra checks the logs every 15 minutes. On a pass, it takes the PR out of
draft and tells ci. On a failure, it reads the run's log over ssh, fixes the PR and requeues it by hand.

**Failure** (4 Oct, `/tmp/queue-*-n{1,1b,2}.log` on infra's VM): about 50 tiers ran from 04:23Z to 19:53Z, and 17 failed.

- **The chain stops whenever the VM stops.** #1061's tier started at 07:02Z on node 2 and took about 12 minutes. The VM was
  suspended, so its result was read at 14:08Z, and node 2's chain did nothing for 7 hours. AGENTS.md already rules this out
  for spend and results ("nothing that bounds spend or preserves results may depend on [an agent VM]"). `vy-steward-watch`
  on node 1 exists for the same reason.
- **The VM's credentials break the chain.** At 06:43Z, seven tiers (#955, #965, #970, #988, #1011, #1012, #1061) failed in
  the same minute because the clone's embedded token had rotated (`could not read Password … terminal prompts disabled`).
  Each was requeued by hand.
- **Results wait up to 15 minutes for the poll.** A pass reaches ci up to 15 minutes after the run ends, and a failure is
  fixed after the same wait. Over about 50 tiers a day, that is several hours of PRs that were ready but not yet in the queue.
- **Stale bases look like real failures.** #950, #978 and #1061 failed on vllm's `test_commit_group`, which main had already
  fixed. The tier runs at the PR's head, so the PR's old base fails. Each one cost a read of the log, a merge of main and
  another tier.
- **The chains are hand-kept files.** The todo files, the per-chain clones and the `sed '1i'` on an empty file (which does
  nothing) are all mechanisms only infra knows about, and a second coordinator can't use them.

**Mechanism.** A `vy-queue-ready.service` on each node, as user `research`, from the tool tree that `research deploy install`
already deploys (`VY_RESEARCH_TOOL`). The parts:

1. **Requests are store labels**, the same way `ready` and `grant` are. `research queue ready N --on M` (unchanged for the
   caller) writes `ready_request = M` on `pr:N@<head sha>` and returns at once. `--wait` keeps today's blocking behaviour for
   whoever wants it. A request is tied to its head, so a new push needs a new request, exactly as `ready` does.
2. **The service polls** the store remote every minute for labels. For each request without a result at that head, it runs
   `QuickTier` locally, the same code as `--local`, inside `tools/check/slot.py`'s check slot. That code already admits by
   slot, so one service per node runs as many tiers as the node has check slots, each in a clone of its own under the
   service's workdir. Nothing on the node waits on ssh, and nothing on a VM waits at all.
3. **It writes the outcome as labels.** On a pass, it writes `ready = true` exactly as today. On a failure, it writes
   `ready_failed = <the failing tests>` with the run id. `research queue status` shows both, so ci and the owner read one
   place.
4. **A failure gets one retry on main.** If the failing tests are all in suites the PR doesn't change, the service reruns
   just those tests on the PR merged with `origin/main`. If they pass, the label says `stale base: merge main` rather than
   a bare failure. This only labels: the PR still needs a merge of main and a passing tier.
5. **Notices use the paths the queue already has.** A failure goes to a handoff in the owner's lane directory, which is the
   queue's existing refusal notice, sent once per head. A pass needs no notice, because the queue admits it on its next sync.
   No Slack token goes on the node in the pilot.

**Smaller mechanisms tried.**

- **Keeping the chains on the VM, with a better credential helper.** #841 (merged 3 Oct) already did this, and the 06:43Z
  failure happened anyway. A VM's credentials are the VM's, and they rotate and expire on its schedule.
- **Running the chain loop on the node in tmux.** It survives a VM suspension, but it is still a hand-kept todo file with no
  restart, no owner and no request path for anyone except infra.

**Walkthrough** (the queue's quick tiers on 4 Oct):

| Change type | Count | What the service changes | Blocks or labels | Who acts |
|---|---|---|---|---|
| Tier passes | ~33 | Ready label written at the run's end, not at the next poll; no VM in the loop | neither | machine |
| Real failures (a test the PR broke) | ~6 | Same as today; the handoff names the tests | labels | owner |
| Stale-base failures | ~4 | One automatic rerun on main; labelled "stale base" | labels | machine, then owner |
| Infra failures (credentials, VM suspension) | 7 + one 7 h stall | Gone, or retried by the service on its next pass | neither | machine |

**Price per week.**

- Human: 0.
- Merge path: 0 added. The queue's admission is unchanged, and ready labels arrive sooner.
- Shared files or queues: the three `/tmp` todo files are replaced by store labels, which every owner already writes.
- Always-read words: 0 (the queue's docstring changes).
- Pods: 0, since the work runs in the check slots the tiers already use.

Against that, today cost one 7-hour node stall, seven manual requeues, about four stale-base round trips and up to 15 minutes
on each of about 50 results.

**Tests.**

- 6, serialization: requests are per head and slots are per node, so there is no new single queue. One service per node is a
  restart point, but systemd restarts it, and a lost request is re-read from the store.
- 9, owner and exit: the owner is infra. The service retires when `research queue sync` enqueues a tier on every new head by
  itself (see the decisions below), or when the repository moves its CI elsewhere.
- Every other test is a clear yes.

**Budget.** Within it: no new step for anyone, no approval and no file that PRs touch.

**What the pilot needs on the node** (to verify first):

- GitHub read access for the service's clone, from a deploy key or an app token owned by the node, never a VM's helper.
- Label write access to the store remote, which custody already has on node 1.
- One clone per slot, not worktrees of one clone. `ready` locks its worktree per git common dir, so worktrees sharing a clone
  would run one at a time.

**Pilot.** Node 1, infra's own PRs only, for a day. The VM chains stay as the fallback for everything else. Measure:

- run end to `ready` label (target under 2 minutes; with today's 15-minute poll it averages about 7);
- failures by cause;
- hours the node's check slots sat idle while requests waited.

Then extend it to node 2 and every lane, and stop the VM chains.

**Decisions** (each proceeds on its default if nobody answers by the pilot's end):

1. **Should the service also take PRs out of draft?** Default: no. The queue ignores draft state (`queue.py`'s docstring), so
   infra stops flipping drafts by hand on the queue path. ci reads `research queue status`.
2. **Should `queue sync` request a tier on every new head of an owned PR by itself, so nobody runs `ready`?** Default: not in
   the pilot. Revisit when the pilot's idle-slot hours show capacity for it.
3. **Should a stale-base failure be relabelled automatically, or should the service merge main into the PR branch and retry?**
   Default: label only. The service never pushes to a lane's branch.
