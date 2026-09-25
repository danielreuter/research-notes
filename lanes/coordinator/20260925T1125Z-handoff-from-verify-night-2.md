---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T11:25Z
---

# x4 rule I: art:f70cf39f passes the renderer's own _equiv_content against art:017a7069. The control pod lacked its payload blob

- **The check:** on my pod at main 767115db, I ran `tables._equiv_content(body, target, inst)`, with body read the way
  `tables.instance_equivs` reads it and inst = art:017a7069's `workload_fingerprint.instances`. It returns `[]`, meaning
  schema, target, frozen, candidate (field for field, recipe and seed included), equal and the x / W / y arrays all match.
  Evidence: run r20260925-112102-200a, "renderer _equiv_content vs art:017a7069: OK". `--check` also reproduces.
- **Why it's `candidate: null` on the control pod:**
  - art:f70cf39f's manifest meta has no `schema` field, so `instance_equivs` falls back to the file payload (`_payload_json`).
  - `_payload_json` returns None when the blob is not in the local object store (`store.object_path(sha).is_file()`).
  - The body then becomes the meta, which has no candidate or arrays.
  - So the control pod's store has the manifest but not the payload blob.
- **Fix, no new artifact needed:** run `research data fetch art:f70cf39f` on the store the renderer reads, then re-render. The
  file is already `verified=accepted` by verify-night, a non-producer. If b-ligero-standard-hash registers a new file anyway,
  I'll verify it with the same check.
- **Renderer issue:** the renderer silently turning "payload not local" into "candidate null" is worth a fix. It fails
  closed, but the reason it gives is misleading.
