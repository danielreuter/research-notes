---
id: 20260930T2000Z-handoff-from-accounting-state-for-successor
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: accounting subcoordinator (bc-e90634dd-8e87-5b7b-8ecd-97abfd87e3fa; @compute-accounting, @memory-accounting, @network-accounting)
---

# @old-accounting (bc-b729c175): please send your successor your full state, as one handoff in `lanes/accounting/` plus one evidence-store tree

I'm bc-e90634dd, the accounting subcoordinator in the top-level Project (bc-7f347b4b). Since Daniel's 19:50Z restructure I
hold @compute-accounting, @memory-accounting and @network-accounting, and you advise as @old-accounting
(`note:20260930T1955Z-handoff-from-infra-slack-advisor-accounting`). I've read your charter
(`note:20260930T1740Z-handoff-from-pous-charter-pouw`), so there's no need to repeat it. Send only what has changed since 17:35Z
and what the charter doesn't cover.

Your Project store isn't mounted on my VM, so please ship it through the evidence store. Your reply to me goes to
`lanes/accounting/<stamp>-handoff-from-pous-state.md`.

## 1. The store, as one tree

Run `research data put --kind evidence/v1 --meta '{"lane":"pous","what":"pous store handover to accounting"}' --tree <dir> --preserve`
over a copy of your store's `notes.md`, `preferences.md`, `docs/` and `internal/` (including `internal/pouw/panel/`,
`internal/pouw/rtx-pro/server.md` and `workers/`, and `internal/pouw/red-team/ratings.md`). Leave out `private/`. If
private material is something I must know, name its path and I'll ask for it separately. Name the `art:` id in your reply.

## 2. The handoff: what the charter doesn't have

1. **Agents.** For each of your agents still RUNNING, and for bc-2aa33ad8 (RTX PRO) and bc-824e54a2 (crypto) with their
   workers, give:
   - its current task;
   - when it expects to finish;
   - what it hands back, and to whom;
   - whether it should stop after that task or has a next one queued.

   Also list any agent you would retire now.
2. **PRs.** Which PRs are merge-ready and in which train order (today it's #449, then #548 and #534; plus #491, #567 and #577),
   which are superseded and can be closed, and which have red-team verdicts outstanding (the verdict only, with the private
   path). Say whether anything is waiting on the research coordinator.
3. **Daniel's decisions.** For the beacon (drand quicknet), per-row seeds (`-h3` or `-h2`) and registered weights (keyed
   rotation or a curated list): has Daniel answered any of them, where is each question written, and has anything since changed
   your recommendation? From `docs/project-context.md` § "Morning questions", which questions are still open?
4. **Promises owed.** For each thing you promised Daniel, infra, cluster-build, the research coordinator, circuits or proofs:
   what it is, who it's owed to and by when. In particular, did the freeze-list sign-off reach `lanes/cluster-build/`?
5. **Plans.** The next three moves you'd make for PoUW, and anything for PoUS or network accounting that shouldn't wait, such
   as the paused PoUS lanes and the idle network-timing agent bc-6b78649f.
6. **Traps.** Anything that bit you and would bite me.

## 3. From now on

- **Relaying.** Your workers' results go to me. Until your VM can post, put them in `lanes/accounting/`. After that, post them
  on Slack tagging @compute-accounting (or @memory-accounting or @network-accounting).
- **Feedback.** About once a day, and before a big decision, I'll ask you for feedback on what I'm doing.
- **Where to find me.** My lane is `lanes/accounting/`, and agent-facing write-ups go to the top-level store,
  `internal/accounting/`.
- **Timing.** Please reply by 21:00Z (2 pm PT). If the full tree takes longer, send the agents and promises sections first.
