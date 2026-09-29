---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Relay: Daniel's notes on the infra diagram, for the diagram agent

**For:** root, to forward to the diagram agent (bc-52e0a086-df9d-55c2-8dce-f6c32ba68b4a). **From:** the docs-site worker, Tue Sep 29, 12:20 PM PT. Daniel sent these to my chat between 12:16 and 12:19 PM PT. The diagram is the diagram agent's, on `cursor/infra-diagram-8b4a` in `~/projects/website-infra-diagram`, so I haven't touched it. "Now" below means `apps/docs/lib/infra.ts` at `defcb6a`.

## Daniel's notes, verbatim, with what the diagram shows now

1. "Sorry also note agents can talk directly to compute via ssh (it's not entirely brokered by the gateway)"
   - **Now:** there's already an `agents-compute` link to Research, labelled "SSH", with the comment "Agents SSH straight into compute; everything else goes through the broker."
2. "I think what agents do is request compute and storage allocation"
   - **Now:** the `agents-broker` link reads "Request pods, spend, data", and `broker-storage` reads "Scoped reads and writes".
   - **A fact from the store broker, if it helps:** no bytes pass through the site. A write gets a presigned PUT that goes straight to R2, and a read is a redirect to the public bucket. So the broker allocates and authorizes storage, and the data moves directly.
3. "Control plane is all vercel now so vercel can be top right"
   - **Now:** the `control` group has no `provider`, while each of its three cards (Broker, Cron jobs, Console) says "Vercel". The other groups carry their provider on the group itself: Cursor, Slack and RunPod.
   - **My reading:** give `control` the `provider: "Vercel"`, so it shows top right like the others, and drop it from the cards.
4. "Note research and CI are different things -- the sububbles should their own dataflow on hover when important different"
   - **Now:** Research and CI are cards in the `compute` group. Only the SSH link targets Research itself. The broker's, the cron jobs' and storage's links target the whole `compute` group, so hovering CI shows the same flows as Research.
   - **Asked for:** where their flows differ in a way that matters, the links should target Research or CI themselves, so each card's hover shows its own dataflow.

## Related, from me

- The cron jobs Daniel wants on Vercel Cron are the pod reaper, liveness and lease checks, and an hourly `main` audit. The diagram's `jobs` links already show "Reap idle pods" and "Audit main". I'm building the cron wiring on `website-docs` now, with only the store's jobs for today: the staged-upload cleanup and the event roll-up.
