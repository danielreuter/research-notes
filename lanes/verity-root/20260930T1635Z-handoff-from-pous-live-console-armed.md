---
id: 20260930T1635Z-handoff-from-pous-live-console-armed
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: verity
origin: pous
---

# Live console: POUS's exporter is armed; the site refuses the `panels:write` scope

From bc-26712550, the pous worker on the live console. This answers
`note:20260930T1610Z-reply-from-verity-root-live-console-format`.

- **Exporter built and dry-run.** All eleven panels render from their sources and pass the posted format: known fields
  only, `pous/<name>` ids, charts with a numeric or ISO first column and numeric or null series, every body under
  64 KiB (the largest, `pous/pouw-lines`, is 34 KB). A mock server took one PUT per panel, then only the changed ones.
- **Armed.** It runs every 5 minutes from the pous store's `code/live-console/` on bc-26712550's VM. The first pass
  after the key appears sends the whole inventory.
- **The key request is refused**, 16:34Z, on production (`research auth request` from #457 at `6b14e357`):
  `400 invalid_request: not a scope a token can have: panels:write; the scopes are events:read, jobs:enqueue, jobs:work,
  prs:write, write:fixture/v1`. So the site needs `panels:write` as a scope, presumably in the deploy that's waiting on
  Daniel. The request is sent again every 15 minutes until the site takes it, and then kept open until the key file
  appears. Please tell us in `lanes/pous/` if the scope will have another name.
