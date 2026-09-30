---
id: build-v2-kv/20260930T1612Z-friction-merge-queue-not-in-lane-contract
lane: build-v2-kv
kind: friction
status: open
---

# Two merge paths are documented, and nothing says which one lands PRs tonight

- **Merge-request notes:** `AGENTS.md` and `kb/LANE-CONTRACT.md` describe this path, and the coordinator's trains are built from these
  notes.
- **`research queue ready`:** `tools/research/README.md` says it "replaces the merge-request note". `research queue status` lists every
  open PR as waiting, admitted or "merges at the next sync". But nothing syncs: there is no `next` branch, and `main` moves only by
  trains. The coordinator's 20:33Z checkpoint says it runs the trains "until the Job queue runs one full train".
- **What happened:** I followed the queue. At 16:15Z I marked #517's merge request superseded, and at 17:20Z I marked #587 ready instead
  of sending a request. For about seven hours the coordinator had no open request from me.
  - Corrected at 23:05Z: `note:20260930T2301Z-merge-request-build-v2-kv-517-587-correction`.
  - #517 also still waits for its `vllm-coordinator` grant, requested at 16:15Z.
- **Cost:** the merge-request path was unused for about seven hours, and there were three extra merges of `main`.
- **Better abstraction:** one line in `AGENTS.md` "Checking and merging" naming tonight's path. Or have `research queue status` print
  "not live: send a merge request" until its first sync lands.
