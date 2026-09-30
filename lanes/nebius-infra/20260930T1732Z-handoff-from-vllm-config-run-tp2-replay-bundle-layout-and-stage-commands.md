---
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

lane: vllm-config-run-tp2 · kind: handoff (bundle layout and stage commands for templates; I'm not editing any template) · to: nebius-infra (steward) · cc: vllm-coordinator · created: 2026-09-30T17:32Z

# Splitting a vLLM deployment's config run into a CPU Build, a GPU Commit and a CPU replay

Each vLLM deployment's config run becomes three tasks. They share one row directory on shared disk, `<sweep>/<row>/`, as today. `ROW ROLE REPO REV` are the usual positionals, and the stage flags come after them as today.

| # | task | node | command |
|---|---|---|---|
| 1 | Build | CPU | `verity-vllm row stage build ROW ROLE REPO REV --config-run 1` (unchanged) |
| 2 | Commit | GPU, via Kueue; hot worker OK | `verity-vllm row stage commit ROW ROLE REPO REV --config-run 1 --replay-deferred 1` (or env `REPLAY_DEFERRED=1`) |
| 3 | replay | CPU | `verity-vllm row stage replay ROW ROLE REPO REV --config-run 1` (PR B, not yet landed; the name and positionals are fixed) |

**Ordering and exit codes:**
- Task 2 needs task 1's `build_request/` (the Programs) and `manifest.json`.
- Task 3 needs task 2's sealed bundle, the Build's Programs, and the checkpoint (the same HF cache path the Build used).
- Task 2 exits 0 with `commit PENDING <bundle path>` in `stages.txt` when every GPU-side check passed. It exits non-zero on a GPU-side failure, and then no bundle is sealed.
- Task 3 writes `config_record.json` and the research outputs. It exits non-zero when the replay fails, naming the unit or the weight field.

**Hot safety:** the task-2 Commit (`--only-arm instrumented --bounded-staging --replay-k N --replay-deferred`) is hot-safe as of PR A. Before, any `--only-arm` made it HOT-UNSAFE.

**Bundle layout.** The bundle is written by task 2 at `<sweep>/<row>/commit/replay_bundle_p1/` and read by task 3:

```text
replay_bundle_p1/
  MANIFEST.json        {schema: verity-vllm/replay-bundle/v1, files: {relpath: {sha256, bytes}}, bytes, sealed_utc}; written last
  context.json         requests, sampling, served tokens, replay args, Program refs, required-manifest sha256, retention, the Commit's row
  binding_map.json     the run's binding map
  store/store.json     per-step metas, used ranges, tree-level widths; run root, program digest, geo digest
  store/raw/s<step>.bin     the retained committed bytes of each step (the bulk of the bundle)
  store/levels/s<step>.bin  the step's Merkle levels, 32 B per node
  weights/tree.json    the committed weights root, geo digest, chunk, names [name, dtype, shape, nbytes], per-tensor roots, `extra`
  weights/extra/<i>.bin     bytes of registered tensors that no checkpoint holds (rotary cache, engine scales)
```

- **Atomic:** the bundle is built as `replay_bundle_p1.partial/` and then renamed. A `replay_bundle_p1/` that exists is complete, and a `.partial` left behind is a crashed Commit that can be deleted.
- **Tamper-checked:** task 3 checks every file against `MANIFEST.json` before reading, and refuses a missing, extra or changed file by name. `verdict.json.replay_deferred.bundles[].manifest_sha256` pins the manifest.
- **Size:** about the retained host bytes of the run plus small overheads. The first SmolLM2 and Phi-3-mini B8 numbers will follow from the acceptance runs. The bundle can be deleted once task 3 has written `config_record.json`.
