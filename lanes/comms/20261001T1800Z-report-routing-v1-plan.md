---
id: 20261001T1800Z-report-routing-v1-plan
campaign: verity
lane: comms
kind: report
status: done
repo: danielreuter/verity
origin: comms (bc-3e100045-0b60-5d20-951e-7207a989b252, under bc-7f347b4b), moved from its coordinator's agent store internal/comms/routing-v1-plan.md on Daniel's 4 Oct ruling
---

# Comms: `@lane` routing, first version (plan, 1 Oct 10:10 AM PDT)

This builds infra's design (`internal/infra/slack-direct-routing-design.md`): inbox threads, routing by `@lane`, and the
loop and noise guards. It adds what the data points from compute accounting and console showed. Comms builds and owns it.

## Changes to infra's design

1. **It works from any checkout.** VMs boot from old snapshots whose `research` has no `slack` command. `slack.py` is
   stdlib-only except for one `timefmt` import, which I inline, so it runs as a single file. The skill gets one line that
   works anywhere with git access: `git -C /workspace fetch -q origin main && git -C /workspace show origin/main:tools/research/src/research/slack.py > /tmp/vslack.py && python3 /tmp/vslack.py ...`.
   The registry is read the same way (`--registry` from `origin/main`) when the checkout's copy lacks a handle.
2. **Any agent can be addressed, with or without a coordinator handle.** A route is `{name, holder bc-id, inbox_ts}`. A
   worker, an old coordinator's worker or a laptop agent opens its own inbox with `inbox open --as <name>`, and that one
   overlay line is the whole registration. No user group, no `groups sync`, no admin. `ask`, `announce` and `reply` accept
   any routed name in `--as` and `--to`, which closes the "`announce` needs a registry handle" gap.
3. **Self-hosted agents** (console on Daniel's laptop, which has no Slack tool and no Cursor OIDC):
   - Posting works with `SLACK_BOT_TOKEN` in the laptop's env, so the CLI posts directly. Putting the token there is
     access, so Daniel decides.
   - Waking needs a Slack subscription, which a laptop agent doesn't have. Until it does, its inbox thread is read on its
     own timer or at turn start (`research slack inbox read --as console --since`), and top-level keeps forwarding to it.
4. **Thread replies route.** A reply that starts with `@x` pings x. A reply also pings the root's poster and the root's
   addressees, as in the design. This closes the lander/owner gap.
5. **Running workers can be reached mid-run.** A Task-tool worker can't be messaged until it returns, and a resumed one is
   refused while it runs. Circuits hit this with a resource-safety rule that never reached two Boolean workers, and
   compute accounting hit it too. A running worker needs no wake, because it already runs `research notes checkpoint`
   every 20 minutes or less.
   - `checkpoint` (and `research slack inbox read --as <lane>`) prints the lane's unread inbox-thread pings next to the
     notes inbox, and marks them read in the lane's state.
   - A coordinator reaches a running worker with `@<lane>` and is heard within one checkpoint interval.
   - `--urgent` makes the worker's checkpoint exit nonzero until the ping is read, for a stop order or a safety rule.
   - The coordinator opens the worker's inbox at launch, with `inbox open --as <lane> --holder <bc-id>`, so the worker
     needs no setup.
6. **Machine notices move to Slack** in v1.1: the merge queue's refusals and the steward's kills, which today are notes
   handoffs, post `@owner` in #agent-coordination.

## Probe result (10:30 AM PDT): passed

- A thread subscription fires on our own bot's reply in that thread. The pointer posted at 10:14 AM PDT in comms' inbox
  (`1790874830.577669`) woke comms, delivered once the turn it was posted in ended.
- Side effect: my own reply in a subscribed thread (the console ask, `1790874951.467319`) also woke me. Doorbell
  delivery therefore wakes an agent for its own posts in threads it subscribes to. Self-delivery has to be filtered by
  the router (the follow-up adapter), or the agent ends such a turn silently, as `match` already does for its own posts.

## Directory entries opened

- `@comms` (comms, bc-3e100045), inbox `1790874830.577669`.
- `@lean` (bc-19c498a8-628e-5c04-8f61-fe785a24741b), inbox `1790876784.355249`, opened 10:46 AM PDT at top-level's request.
  Remit: review of every audit-flagged Lean guarantee change (Daniel 10:18). Notes commit `419cbea6`. Its onboarding post
  (`1790876975.076739`, from @comms) went through the broker under a routed, non-registry username and rang its inbox.
  So the broker doesn't restrict `username` to registry handles. Lean isn't subscribed to its inbox yet; top-level relays
  the pointer.

- 10:57 AM PDT, after Daniel's 10:56 ruling (only leads get handles): infra, circuits, proofs, compute-accounting,
  memory-accounting, network-accounting, console, pr-captain (ci), old-circuits-and-proofs (the lander, bc-8ece7cde)
  and top. The registry gains pr-captain, lean, comms and top, and `names open` refuses non-handles. The checkpoint's
  Slack read (the mid-run path for workers) is removed. Rollout thread for confirmations: `1790877503.074029`.

## Build order

1. Probe, before anything else: does a thread subscription fire on the bot's own reply in that thread? I'll check with
   comms' own inbox. If it doesn't, delivery falls back to pinging the target from a top-level post, which costs noise. I
   report the result before going further.
2. `slack.py`: `inbox open | read`, the routes (`registry.json` handles gain `inbox_ts`, plus an add-only overlay at
   `kb/slack-routes.json` in the notes), routing in `ask`, `announce`, `reply`, `done` and `decline`, and the guards: no
   routing out of inbox threads, no self-pings, one ping per (post, target), status lines and `--quiet` don't ping, and a
   cap of 6 pings per inbox per source thread per hour. Tests run against the existing fake Web API. Standalone run.
3. The mid-run path: `checkpoint` reads the lane's inbox thread (change 5), with tests.
4. `research slack traffic [--since]`, the monitor. It reports pings per inbox per hour, cap trips, `@name` posts that
   addressed no route (dropped), and asks with no 👀 after 2 h. I run it on a timer, and its output is the monitoring
   record. It feeds Daniel's open question about how much chatter is right.
5. Skill: wake recipe = subscribe to your inbox thread and renew it. Remove the user-group and `groups sync` sections, and
   lift "workers stay off Slack" for agents with an inbox.
6. Pilot on comms, infra and circuits from the branch, then every handle, then each coordinator's running workers.

## ETA (Pacific)

- The probe result by 10:45 AM PDT.
- The PR with tests (items 2 to 5, mid-run path included) by 2:00 PM PDT. The pilot starts from the branch right away, and it merges on the next
  train.
- The monitor runs from the pilot onward. The first traffic report is due at 4:00 PM PDT.

## Open questions

- Daniel: do his own typed `@lane` posts route in v1? If he says no, as infra recommends, top-level keeps forwarding those.
  If he says yes, it needs a poller on the control pod, about an hour more.
- Daniel: may `SLACK_BOT_TOKEN` go into the laptop env, so console can post?
