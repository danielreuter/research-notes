---
id: 20261004T2100Z-report-messaging-product-review
campaign: verity
lane: comms
kind: report
status: open
repo: danielreuter/verity
origin: comms (bc-3e100045-0b60-5d20-951e-7207a989b252, under bc-7f347b4b), moved from its coordinator's agent store docs/messaging-product-review.md on Daniel's 4 Oct ruling
---

# Agent messaging: what's hard, what's ours, what to do next

Comms, 1 Oct 2026, after the first day of `research msg` with all 12 leads on it. Companion to
`note:20261001T1800Z-report-routing-v1-plan` (what
shipped) and `note:20261001T1836Z-report-server-side-router-spec`
(console's router).

## 9 Oct

About 1,060 doorbells and 790 posts over 24 hours. old-circuits-and-proofs received 246, ci 193, top 187 and infra 109.
There were no pauses, duplicate doorbells or stale footers.

- **Merge-thread wakes (#1616, on main at 11:07Z).** Lanes subscribed to the merge thread were woken by every reply. A
  reply under an announcement now rings only:
  - its leading names;
  - the owners of the PRs it names;
  - a lane that named a run beside its own PR, when the post names that run.

  Replayed over the night's 138 merge-thread posts, that's 1,044 wakes down to 202. For compute-accounting and
  network-accounting it's 268 down to 41, and network-accounting is still rung for both dd21 landings. My announcement
  (1791544055.042049) asked every handle to drop its subscription to the merge thread. Only memory-accounting replied,
  and top keeps its own subscription. Subscriptions aren't visible to me, so the cut shows only as lanes stop reporting
  "no action needed" turns.
- **Two posts rang nobody they meant (#1649).**
  - 02:18Z, top: `:mega: @lean @proofs … Rules changed since 8 Oct; please reread them now`. The leading `:mega:` hid all
    ten names, so none of them was rung. This is the to-all wake I missed last night.
  - 13:16Z, lean: `lean: Landed: G …` in top's status thread. It named only its author, so it counted as addressed and
    didn't ring top.

  Now one emoji may lead the names, and a reply naming only its author rings the thread's starter. Three vectors pin
  both.
- **`--as` took any handle (#1645, from the lander's friction pass).** The lander's stray `--as ci` post (03:39Z) went
  out as @ci. Every command that posts now refuses a name the agent doesn't hold (its registry `holder`, or its open
  inbox's route). `research msg retract` blanks your own post; it needs the token, since the broker allows no edits.
  `tools/move/` is now ci's in the registry.
- **Asks.** I closed my own resolved train request to ci (#1616 landed). The one other unanswered ask is top's to lean
  (06:10Z).
- **This review's ready step was slow.** `research queue ready --on vy-nebius-1` waited 10 minutes on a quick tier that
  a ready mark doesn't need (AGENTS.md). I labelled by hand, cancelled the quick tier with a reason, and the review timer
  (now `comms-daily-messaging-review-v4`) labels by hand from here on.

## 8 Oct

About 1,200 doorbells over 24 hours. ci (pr-captain's inbox) received 262, top 256 and old-circuits-and-proofs 211. There
were no pauses, duplicate doorbells or dropped names, and no stale footers.

- **The lander-only rule cut the merge thread.** The merge thread (1790957906.278529) carried 887 of the 1,205
  doorbells. Daniel's 14:27Z rule says only the lander lands, restacks and reruns, and lanes go back to research. In the
  14 hours before it, the thread got about 540 posts from 11 handles. In the two hours after, it got 12, nearly all
  from top and the lander. That's his rule, not a messaging change. I'll check tomorrow whether it holds over a full day.
- **The monitor flagged `fyi` posts as unanswered.** Two of the 9 "unanswered" entries were infra's notices to ci, sent
  with `--kind fyi` as I advised on 7 Oct. Their footer is `_fyi_` alone, written by a client older than the change that
  makes `fyi` imply `--quiet`. `cmd_traffic` counted them as asks.
  - `cursor/traffic-fyi-not-asks-b252` (`de1a8f0d1`, from main `3ab2f19c5`) leaves an `fyi` out of the unanswered list.
    Live, the list drops from 9 to 7. The research suite passes (1,929 passed, 3 skipped).
  - Routing is unchanged. The shared vectors pin that a reply tagged `_fyi_` alone still rings its thread's starter, and
    the server router follows those vectors too.
  - The PR waits until #1564 or #1566 lands, because of the two-open-PR cap.
- **The steward's reminder repeats with no answer.** "I can't read node 1's dispatcher ticks" rang circuits every hour
  since 06:14Z, 10 times, in circuits' 1 Oct disk thread, with no 👀 or reply. I asked circuits whether `node1-dispatch`
  is still theirs and infra whether a 👀 stops the reminder (1791477462.106739).
- **The other seven unanswered posts are OOM alerts** from vy-monitors to the owners of the killed runs. The owners
  don't pick them up, and those alerts don't repeat, so they cost one wake each.

## 7 Oct

About 1,250 doorbells over 24 hours, across 42 threads, during the overnight layout move. top received 311 and ci 208.
The merge-train thread (1790957906.278529) carried most of them: 150 of ci's and 143 of the lander's. That is real work,
as before. A doubled leading name (`@ci @ci`) rings once, and no inbox got two doorbells for one post.

- **Long posts split.** Slack breaks a post over about 4,000 characters into separate top-level messages. Top's 05:41Z
  move announcement lost its second half that way (1791351683.801419): the half that addressed infra, ci, the lander,
  comms and console. It rang nobody, and `read --thread` didn't show it. The 6 Oct platform draft had split the same way
  (three extra roots). #1447 (merged 07:47Z, tip 102) makes `_post` cut at line breaks into pieces of at most 3,000
  bytes. The first piece routes as before, and the rest are numbered quiet replies in its thread. There have been no split
  roots since.
- **Status lines in the wrong half.** Because of the split, my hourly lines went into the first half while top read
  the second. Top rang me for silence at 09:17Z. Nobody needs to remember which half to use once posts stop splitting.
- **Notices sent as asks.** 7 of the 8 "unanswered" entries are infra's notices: updates to top and two steward FYIs,
  sent with the default kind. Each rang its addressee and is flagged until a reaction. I told infra to use `--kind fyi`.
  No code change: the kind can't be inferred safely from the text.
- **The move.** Top accepted comms' proposal that `slack.py` stay in `research` until the node redeploy PR, because
  node 1 runs `monitors` and the probes, which import `research.slack`, from installed paths. Comms' part waits on
  `cursor/ops-messaging-b252` (#1456). The layout move (#1450) hasn't landed. `research msg` works on main
  (`c9bb7acef`).

## 6 Oct

About 1,000 doorbells over 24 hours, across 48 threads. ci received 203, down from 330, partly because #1230 stopped
counting its own notes. No pauses, duplicates or dropped names.

- **`fyi` works.** The 6 `fyi` posts woke 9 handles. Starters' unnamed follow-ups still caused 58 wakes from 16 posts,
  most of them top's freeze and deadline corrections in the migration thread. Those concern everyone, so they're fine.
- **A question woke no one.** infra posted as @infra, starting `@infra steward: …` (18:55Z on 5 Oct). A post never wakes
  its author, so nothing rang, and it went unanswered for 22 hours. #1379 refuses such a post, and I told infra.
- **One announcement was misaddressed.** infra's daily GPU-waste post went to every handle (10 wakes), but its body
  started with the three leads it was for. Only `--to` sets an announcement's audience. It's one case in 135
  announcements over 5 days, so I sent infra a note and changed no code.
- **The heavy threads are real work.** ci and the lander exchanged 276 doorbells in the merge-slot thread, with a median
  reply of 400 characters and 8 short acknowledgements in 250 replies.
- #1367 swept the messaging text on main to `send` and `close`; top's #1369 takes the skill.

## 5 Oct

Over 24 hours, about 1,100 doorbells. ci received the most (330), then top (198) and old-circuits-and-proofs (122). Every
check came back clean: no pauses, duplicates, dropped names or stale footers (infra has updated).

- **ci's load is real work.** 116 of its doorbells came from one thread, the merge-slot announcement (`1790957906`),
  where ci and the lander (old-circuits-and-proofs) ran trains overnight, naming each other on every turn. Two more
  working threads gave 54 (with infra, on the CI API) and 26 (with circuits, on landings). Each of those doorbells was
  addressed to ci by name.
- **A starter's progress notes woke everyone.** When a thread's starter replies without naming anyone, the reply wakes
  everyone the root addressed. On top's migration announcement, that turned each `fyi` landing-check note into 10
  wakes: 20 for two notes at 11:34Z and 11:44Z. Unnamed follow-ups caused 44 of 558 reply wakes that day. #1209 makes
  `--kind fyi` quiet: it wakes only its `--to` names, and the rest read it in the digest. Until #1209 lands, I asked top to add
  `--quiet`.
- **"Unanswered" is mostly notices.** Of the 7 listed, 5 are status notes or "ready to land" posts that went out with
  the default `ask` kind. Once #1209 lands they can go as `--kind fyi`, which the monitor skips.
- **The monitor overcounted ci.** It counted ci's own hourly snapshots in its inbox as doorbells. #1230 counts only the
  router's posts.
- The ownership map (#1124) landed on 5 Oct at 01:40Z: `research msg owners PATH...`.

## 4 Oct

Over 24 hours, 570 posts and about 900 doorbells. Console's router fix (live 3 Oct 17:42Z) worked:

- **Delivery:** 1 post that should have rung someone didn't, down from 80, and it predates the deploy. Duplicates fell
  from 16 to 2 (both at 19:16Z, into proofs' inbox). No pauses.
- **Subscriptions lapse silently after 3 days.** The subscribe calls the tool printed asked for 3 days, and most inboxes
  were subscribed on 1 Oct, so every lead that hadn't renewed would stop being woken today, with no warning. I renewed
  mine (it was due at 17:13Z), announced the renewal call to every handle (urgent, 16:31Z), and #1103 makes the default
  30 days. This is row 5 (lapse detection) arriving early. A last-read column in `names list` is still worth adding.
- **Stale clients:** lean has updated; infra still hasn't (6 old footers).
- **Unanswered** is now mostly "Ready: #N" notices to ci, which ci acts on through the queue rather than by replying.
  They aren't asks.

## 3 Oct

Over 24 hours, 689 posts and about 820 doorbells. proofs (164), lean (124) and infra (120) received the most.

- **Silent posts, still.** 80 posts that should have rung a lead didn't, and 73 of them were quiet posts. The router
  never adopted #835's rule, because my request to console mentioned the marker by name, and the router reads the
  marker anywhere in a post, so it silenced the request. #945 counts the marker only as a footer tag or at the end of
  the text. The request was resent without the marker and reached console's inbox (16:32Z).
- **Duplicates** continue: 16 pairs, 0.0–0.5 s apart. They're in the same request to console.
- **One pause** at the new limit of 20: proofs into lean at 06:07Z, during a long Lean review. It cost 6 doorbells to a
  thread lean was already reading. I'm leaving the limit as it is.
- **Stale clients:** memory-accounting and proofs updated; lean (39 posts) and infra (30) haven't. Both were asked again.
- **Lesson:** a client whose rule is ahead of the router's misreports its "rings @x" line. A rule change isn't live until
  console confirms the router passes the vectors, and I now ask for that confirmation.

## 2 Oct: the first full day with the router on

Over 24 hours (to 16:34Z), 1,054 posts and about 1,150 doorbells went into 12 inboxes. The busiest were ci (208), infra
(175), the lander (171) and proofs (147), with at most 18 in an hour into one inbox. Rows 1–3 of the table below are done.
`research msg traffic` and a scan of every inbox gave this:

- **Silent posts (the largest loss).** 74 posts named a lead and also carried `(quiet)`, so they reached no one; 47 of
  them were to the lander. None was an acknowledgment, and 20 asked for an action. Senders write `(quiet)` to mean "no
  reply needed". The lander still answered, up to 26 minutes later, because it watches its train thread. From #835,
  a quiet post wakes the names at its start and no one else. Console's router needs the new vectors. Until then the
  client's "the router rings @x" line is wrong for quiet posts.
- **Duplicates.** 25 doorbells (2%) were posted twice by the router, 0.0–0.5 s apart, with identical text. This is
  console's to dedupe.
- **Pauses.** There were 9 before the limit went from 6 to 20 an hour (05:04Z) and none since.
- **Stale clients.** infra, memory-accounting and proofs still post the old `_posted by_` footer: 34 posts, the latest
  at 16:10Z. Readers handle both forms. These three were told to update from main.
- **Fixed overnight:** an announcement to a user group without a label went to everyone (console); a repeated `--to`
  kept only the last name (#725); the traffic report counted ci twice through `pr-captain` (#835).
- **Unanswered** lists 46 asks, but it only sees replies in the ask's own thread, so it's an upper bound.

## What went wrong on 1 Oct

- **Wasted wakes.** Leads also subscribe to the whole channel to hear Daniel's typed posts. So they wake on their own
  posts (pr-captain twice, compute-accounting once, each a full turn of "my own post, no action"), and on every
  top-level post, whoever it's for.
- **Two reads per message.** A doorbell is a link plus footer metadata, so the recipient runs `read`, then opens the
  thread. The output repeats agent URLs, timestamps in two zones and `&amp;`-escaped links.
- **Distribution.** Checkouts older than the branch had no CLI and no registry. Leads ran a fetched single file, and three
  of them had to pass `--registry` until I added a fallback.
- **Rules that became ritual.** "Read mail at every checkpoint" was cut (Daniel: ritual for no value). The rate cap fired
  a false positive on the roll call, because it counted per thread instead of per author.
- **Identity drift.** Lean answered under @proofs' name before it had one of its own. Workers vs. leads went back and
  forth until the 10:56 ruling.
- **Environments differ.** Console, on the laptop, can't subscribe; its wake needs a launchd loop and a Cursor API key.

## What's standard (don't reinvent)

Addressing, inboxes, threads, mention notifications, dedupe, rate limits and digests are solved problems. Slack already
gives us storage, threads, search, and a UI Daniel reads. We should stay a thin addressing and wake layer on top of it,
with no queue, database or read-receipt protocol of our own.

## What's unique to us

1. **A wake is expensive.** For an LLM agent, a notification is a full turn: tokens, context and minutes. Not a phone
   buzz. So the top metric is *wake precision* (each wake is for a message the agent must act on), then *payload
   economy* (it can act from the wake alone).
2. **Names are roles, holders are ephemeral.** VMs are suspended and lanes are succeeded. A name must outlive its holder
   (`succeeds`, `forward_to`), and nothing may depend on one agent staying up.
3. **Two audiences.** Agents need terse, machine-readable posts; Daniel reads the same channel and must be able to follow
   and step in. Doorbells and metadata belong in inbox threads, out of his way.
4. **Agents follow instructions literally.** Every rule we write gets executed by every lead, every time. Instructions
   must be few, and the default behavior has to be the right one.
5. **One bot identity, self-asserted names.** Every agent posts as the same bot, and the name in the footer is typed by
   the sender. Any agent with the token or broker access can post as `@top`. Other agents' text arrives in a wake and
   must be read as data, never as instructions.
6. **Heterogeneous runtimes:** cloud VMs with subscriptions, a laptop with none, private workers.

## What to do, in order

| # | Change | Fixes | Who | Size |
|---|---|---|---|---|
| 1 | Doorbell carries the text, `from infra (thread T): <text>`; posts lose the agent-link footer; `read` is one line per message | two reads, token waste | comms, with console for the router's copy | small |
| 2 | Server router on; leads keep only their inbox subscription | self-echo, fan-out wakes | Daniel sets `SLACK_ROUTER_ENABLED`; comms flips `router.json`; console owns the route | small, waiting on console |
| 3 | Merge #702 so `research msg` is in every fresh checkout; retire the single-file fetch | distribution | top merges after `check` | done but for `check` |
| 4 | Author attested, not typed: the broker stamps the name from the caller's Cursor identity, matched against the directory's holder; the router marks a post whose name doesn't match its holder; bot-token holders shrink to the few services that need it | impersonation | console (broker), infra (secrets), comms (directory) | medium, after 1–3 |
| 5 | Lapse detection (4 Oct: default now 30 days, #1103): inbox subscriptions expire silently. The router (or `names list`) shows each name's last read, and comms nudges a lead that hasn't read a doorbell for a day | silent lapse | comms | small |
| 6 | Loose ends: a daily digest to `@top` of asks open more than a day | asks that never close | comms, using the existing digest | small |
| 7 | Direct delivery into a conversation (Cloud Agents follow-up) instead of Slack subscriptions, where a Cursor API key is available | wake plumbing, the laptop case | console proves it on itself first | later, only if 2 leaves pain |

Deliberately not doing: names for workers, our own queue or database, read receipts, priorities beyond `urgent`,
checkpoint rules, per-purpose verbs.

## How I'll keep tuning it

I keep only my inbox subscription, and a timer runs this review daily at 9:30 AM PDT. It computes, from traffic alone:
doorbells per inbox, duplicates, pauses, quiet posts that name someone, stale-client footers, wakes that ended in "no
action", and asks still open after a day. I ask
a lead only when the traffic can't explain something, one question at a time, and I fold answers into the skill rather
than into new rules.

Success looks like this: an agent wakes only for a message meant for it, sees the message in the wake, replies with one
command, and never has to think about the plumbing.
