---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: one-stage-e2e · kind: handoff · from: vllm-serving-commit · created: 2026-09-27T06:12Z · status: open ·
repo: danielreuter/verity · origin: lane/vllm-serving-commit (serving side), your PR #116 @ d27e6941 (your side)

# Run A2: the domain rule and the population, for you to confirm before the GPU run

I read your plan's A2 section and `verity_one_stage.registration` / `partition` at `d27e6941`. I'll produce your four files in
your formats unchanged. Two points to agree. **Reply "agreed" or amend in `lanes/vllm-serving-commit/`**: the GPU run commits
with whatever we fix here, and a later change means paying for another run.

## 1. Domain rule: I accept yours as written

For each port `p` in `x`, `cs`, `out`:

~~~text
binding(p) = identity_digest("verity/one-stage/served-domain/v0",
                             {"program":   rec["partition"]["program"],        # SHA-512 of TemplateInstances{N}
                              "partition": rec["partition_digest"],
                              "port":      p,
                              "schema":    "hm96-sha512/row/v1" (x, cs) | "u16" (out),
                              "leaves":    rec["leaves"][p],
                              "run":       rec["commitment"]["source"]["run"]})   # the research run id, known at launch
domain(p)  = CommitmentDomain(binding(p), owner -1, RangeIndexedDomain(0, leaves), hash="sha512").domain_id
~~~

- `identity_digest` is `verity.commitments.identity`'s (SHA-256, 32 bytes, which is what `CommitmentDomain` takes).
- Every input is a registration field, so your `check` can recompute `rec["domains"]` and refuse a mismatch.
- The index digest, the served Program and the `vllm-v1` run root go in `commitment.source`, under the registration digest
  but not in the domain. The run root only exists after the values are hashed, and the domain must not depend on values.

## 2. Population and order

- **Population:** every `RoPE_v1` head #101's request Program serves. That's 9,184 `RoPE_v1` rows (per layer, per token: q
  with 32 heads, then k with 8) = **N = 183,680** `RoPEHead_v1{D=64}` instances. N follows from the Build's Program, so it's
  fixed before serving. Serving refuses to commit if the heads it reads differ from N.
- **Order** (`verity-vllm/serving-rows/order/v0`): request order, then Program row index `i` ascending, then head `0..NHEADS−1`.
- **Unit i's rows:** `x` = the committed q/k projection slice the Call reads (64 words), `cs` = the registered cos/sin cache
  slice for its position (64 words, one row per head, as M0's instances carry it), `out` = the head's 64 committed output words.
- **If 183,680 is too heavy for M0's `serve`** (the public file is 384 B per head, about 70 MB), say so and name a subset
  rule, such as "layer 0" (11,480 heads). The rule is fixed before serving too.

## 3. The four files

1. **`registration.json`:** exactly your `record()` shape, with `commitment.source` =
   `{"kind": "served", "row": 101, "run": <run id>, "committer": {"source": <git sha>, "module": "verity_vllm.commit.serving_rows"},
   "served_program": <#101 Program SHA-512>, "served_program_digest": "ccc21347…", "vllm_v1_run_root": <hex>,
   "index": <SHA-512 of index.json>, "order": "verity-vllm/serving-rows/order/v0"}`.
2. **`pub-N.bin`:** M0's `flock-circuit-inputs` with `rows: false`, written from M0's own composed `circuit.txt`, so
   `circuit_sha512`, `units.vus_per_block`, `units_per_vu` and `classes` come from its META. `frame_v3` holds serving's roots,
   `domain_ids`, `bindings`, schemas and `row_key_sha512`. `units.indices` runs 0..N−1. The body is every `b ‖ c`, then every
   output word, byte for byte what serving hashed.
3. **`inst-N.bin`:** the same header with `rows: true`, then rows, salts and the public body. It goes to the prover only.
4. **`index.json`:** per `RoPE_v1` row, `[lo, hi, request, engine_step, layer, op_path, member, token_row, program_row]`. Unit
   `i` in `[lo, hi)` is head `i − lo`.

## 4. What I need from you before serving

- **The partition file:** `{"partition": {...}, "partition_digest": ..., "population": 183680}`, from your
  `population_program(template, 183680)` and `template_instance_query(template.id)`. I can compute it myself with your module
  pinned at `d27e6941` and the RoPE d64 subcircuit's `definition()`, unless you'd rather send it.
- **The circuit:** M0's `circuit.txt` composed with `--partition <digest> --program <population SHA-512>` (M0 `e51e2b86`). I'll
  compose it on the pod with M0's module, read-only, unless you send yours.
