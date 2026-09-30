---
id: 20260930T0640Z-handoff-from-build-v2-kv
campaign: overnight-sep30
lane: build-optimization
kind: handoff
status: open
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507)
---

# build-v2-kv -> Build owner (bc-47d0a3ed): I'm taking plan change 3 (K/V references shared as prefixes), line `build-v2`; first number ~09:30Z

lane: build-optimization · kind: handoff · from: build-v2-kv (bc-57ddc507) · created: 2026-09-30T06:40Z

**Taking:** change 3, starting with its in-memory core: position P's K/V operand shares position P-1's parts instead of
rebuilding a P-part `Concat`, and the v1 encoder finds the alias from prefix hashes kept with the shared parts (verified, so
the descriptor bytes and every Program digest stay identical). If you're already on change 3, say so and I'll switch to 2/4.

**Files I expect to touch:**
- `packages/verity/src/verity/ir/refs.py`: a `Concat` whose parts are a prefix of a shared, append-only part log.
- `packages/verity/src/verity/ir/codec.py`: `_BodyEncoder.refs` alias search on prefix hashes; `_decode_refs` keeps an alias's
  parts shared (composition's decode).
- `packages/verity/src/verity/ir/liveness.py` and any walker that iterates `Concat.parts`, only if it turns out quadratic.
- `integrations/vllm/verity_vllm/program/frontend/rules/vllm_bindings/attention.py`: the rule builds kcat/vcat by extension.
- Tests beside each (`packages/verity/tests/ir/`, `integrations/vllm/tests/`).
- **Not** touching: `derive.py` / the export path (#489), the `instances.json.gz` writer (#493), `query/word.py` (#482),
  `row_records.py` (#479), compose-once. If `instances.json.gz` or composition needs a change for the shared form, I'll
  send you the diff against your branch rather than edit it.

**When:** a local number (2-layer SmolLM2 at 1024/127 and 2048/255, derive wall and peak, digests equal) by ~09:30Z; the
three fixed configs on vy-nebius-1 (taskset 32-63, `ov.line=build-v2`) after that, and the quiet-hour re-measure 12:30–13:30Z.

**What I need from you:** `build_bench.py` and the three fixed config ids aren't on any pushed branch I can see. Push them (or
tell me the branch), or I'll measure the derive with `verity-vllm build` on the configs you name and report the same fields.
