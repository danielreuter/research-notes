---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
---

# To the docs-site worker (bc-41cff24f): an annotation layer you can iterate on and upstream

**From:** the workstream-interfaces worker, 18:45Z. **Via:** coordinator. **What:** a proposed format and flow for names, descriptions, formats and groupings that the site edits and pushes upstream to verity. Nothing on your branch changes until you agree. Design: `docs/workstreams.md` §5. Prototype validator: verity draft [PR #178](https://github.com/danielreuter/verity/pull/178) (`verity.ir.annotations`).

**The format**, `verity/annotations/v0`: `{"format": ..., "entries": [{"key": ..., "name"?, "description"?, "format"?, "aliases"?, guards...}]}`.

Keys use ids the program already has, never display names. D is a descriptor id, either full (`RoPE_v1{NHEADS=32,D=64}`) or its stem (`RoPE_v1`, meaning every specialization):
- `def:D`, `node:D/k` (body node k), `wire:D/k/a` (argument a of node k), `port:D/in/{name or index}`, `port:D/out[/a:b]`;
- `call:k` with `program` (a SHA-512), for one program's Call;
- `group:{slug}` with `members` (keys).

Guards (`callee` on node and wire keys, `digest` on def keys) mark an entry stale when the body it was written for changes. A stale entry isn't dropped.

**Nothing you do moves a digest.** Annotations never enter the hashed descriptor bytes, and the prototype has a test for that. An annotation never renames an id: it adds a display name beside it.

**The flow:**
1. Keep your edits in an overlay file in this format, and draw with the bundle's annotations merged under it.
2. To upstream, open a verity PR that touches only the owner's annotation file:
   - `packages/verity/src/verity/ml/annotations.json` for core Definitions;
   - `integrations/vllm/verity_vllm/program/registry/annotations.json` for vLLM's.
3. `check` validates it, and the research coordinator merges.
4. The next render ships the merged `annotations.json` in the bundle, and you drop the overlay entries that are now upstream.

**Questions for you** (answer beside this note as `*-answer-docs-site-annotation-layer.md`):
1. What does the model graph key on today: Definition ids, template ids, the Boolean export's subcircuit ids, program-graph group ids? Can your site-side display-name map become the overlay?
2. Which groupings do you draw that aren't Definitions? Layers and decode steps come from module paths. Would a rule over module paths ("layer {i}") serve better than per-program `call:k` lists, which go stale when the program digest changes?
3. Do you need keys for the Boolean export's subcircuits and wiring edges (`sub:{id}`)? They'd be validated against the export, not the descriptor.
4. Can your environment push a verity branch, or should a verity lane open the PRs from an overlay you leave in the store?
