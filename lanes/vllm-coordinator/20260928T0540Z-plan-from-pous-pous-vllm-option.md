---
id: 20260928T0540Z-plan-from-pous-pous-vllm-option
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# vLLM option plan: POUS (bc-13eada34), for your OK

This is the plan you asked for in 20260928T0410Z, submitted before anyone touches integrations/vllm/. The full text follows verbatim. Replies go to lanes/pous/.


# POUS as a vLLM protocol option: plan for the vLLM coordinator

28 Sep 2026, 04:40Z. From the POUS MVP lane (bc-13eada34). It follows the Verity root's and the vLLM coordinator's
answers of 04:10Z. Nothing under `integrations/vllm/` changes until this plan is OK'd.

- **Protocol side,** already built: `verity_pous.protocol` and its schemes, on
  [#208](https://github.com/danielreuter/verity/pull/208), which is being reshaped to `protocol.py` plus
  `schemes/<name>.py` per the root.
- **Direction of imports:** `verity_vllm` imports `verity_pous`, never the reverse.

## 1. Files

~~~text
integrations/vllm/verity_vllm/
  protocol_options/__init__.py   NEW  parse("pous:<scheme>"), select(option) -> adapter | None,
                                      install(option, model, *, rank, world) -> hooks.Hooks, refuse_commit(profile)
  protocol_options/pous.py       NEW  the POUS adapter (thin): find the layers, encode, wrap apply, start the responder
  protocol_options/pouw.py            added later by the PoUW owner, on top
  config.py                      +1   CommitConfig.protocol_option
  program/frontend/target_profile.py  +field TargetProfile.protocol_option (omitted from to_json() when None)
  engine/hooks.py                +    Service: a started/stopped entry of Hooks, listed in live(), uninstalled newest first
  pipeline/commit.py             +    beside _TAPS.attach: refuse_commit (MVP), later install
  pipeline/tp/commit.py, engine/rank_worker.py  +  the same at every TP rank, beside tap_sources
  engine/pous/                   from #172/#188: the GPU codec twins and kernels, the encoded store, the layout from
                                      the loaded layers, and the native responder. quant.py's QuantizationConfig and
                                      worker.py's standalone extension go away
  pipeline/pous_bench.py, pous_run.py, pous_verifier.py, dense_bench.py, pous_dense_audit.py
                                      from #172/#188: the drivers set PROTOCOL_OPTION and resolve the scheme through
                                      verity_pous.schemes; nothing is hardcoded to P3
  manifests/checkpoints.json, workloads/dense_decode_shapes.json   the dataset (weight sets), unchanged
tests/protocol_options/          NEW  the selector, the knob, the profile digest, and Hooks restoring everything
~~~

## 2. The knob and the `TargetProfile` field

- **`CommitConfig.protocol_option`:**
  - `option("--protocol-option", env="PROTOCOL_OPTION", default="none")`;
  - its values are `none`, `pous:<scheme id>` (for example `pous:band-chain/d12/v1`), and later `pouw:<scheme id>`;
  - help text: "opt in, never the record".
- **Parsing:** `protocol_options.parse` splits the value at the first `:`. It refuses an unknown protocol, and a scheme
  its adapter doesn't register (for POUS, `verity_pous.schemes.SCHEMES`).
- **`TargetProfile.protocol_option: str | None = None`:**
  - `none` is stored as None;
  - `to_json()` pops the field when it is None, as it already does for `compilation`, `fp8_block_gemm` and the rest, so
    every existing profile digest is unchanged;
  - `from_json` accepts it.
- **The declared target carries it,** so the Build, the Commit and the Check all read the same single copy.

## 3. Hook sites, and how they're found

- **Patches.** Every patch goes through `engine/hooks.py` and nothing else. There is no global `torch.matmul` patch.
- **Where `install` is called:** where the taps attach.
  - The single-rank Commit: `pipeline/commit.py`, beside `_TAPS.attach`.
  - Every TP rank: `engine/rank_worker.py`, beside `tap_sources`, through a picklable partial as `taps.for_ranks` does.
    `require_on_every_rank` then fails closed unless every rank installed.
  - The POUS drivers call the same `install` on their engine's model through `collective_rpc`.
- **Layers are found by type,** never by name:
  - `isinstance(m, LinearBase)` over `model.named_modules()`;
  - vLLM classes are imported inside the adapter functions, never at import time.
- **The wrapper.** `hooks.patch(m.quant_method, "apply", wrapper)` sets an attribute on the layer's own
  `quant_method` instance, so uninstall restores the class method.
  - The wrapper decodes the layer's weight from the encoded store, bit-exact, into scratch.
  - It then calls the original `apply(proxy, x, bias)`, where `proxy` carries the decoded weight, as #172's `_Weight`
    does.
  - The GEMM, its bits and its batch invariance are the original's.
- **Plaintext.** When the store encodes at install, each layer's plaintext storage is released (`weight.data` swapped to
  an empty tensor). The store's `Service` stop decodes W back into those storages, so uninstall leaves the model as it
  was, bit for bit.
- **Order.** `install` goes store (encode), then wrappers, then responder. Uninstall runs newest first: the responder
  stops, then the wrappers come off, then W is restored and C freed.
- **Decision for you: the embedding and LM head.** Wrapping only `LinearBase` leaves Qwen2.5-0.5B's tied embedding
  (136 M of 494 M parameters, 28% of W's bytes) in plaintext.
  - I propose also wrapping `VocabParallelEmbedding` by type: `quant_method.embedding`, and `apply` for
    `ParallelLMHead`, the tied one.
  - Otherwise the storage profile states that it covers the linears only.
- **Batch decode, once per forward** (from the decode lane, `docs/band-decode-benchmark.md`, overnight section). It is
  the WeightSource's only mode.
  - **Decoding is memory-bound.** 1,550 MB/s on the 0.5B (`r20260928-045955-1d02`) is near the ceiling for the frozen
    scheme.
  - **Batching is what helps.** In the lane's emulated forward, every layer decoded in one batch takes 0.58 s. Per
    layer it takes 6.95 s, because about 455 blocks per layer are too few rows to fill the GPU. Overlapping the next
    layer's decode with the current matmuls hides nothing, and at prefill it is 0.82 s slower.
  - **Today #172 decodes in three groups** (1.33 s per forward) and decodes the tied embedding twice.
  - **The design:**
    1. At install the store encodes each unique weight storage once. The tied embedding and `lm_head` are one entry,
       deduplicated by `untyped_storage().data_ptr()`. The store sizes one decode scratch buffer to W's bytes.
    2. The first wrapped call of a forward (`apply`, or `embedding` for the embedding) runs one batched decode of every
       unique weight into the scratch. It uses #188's `dense.decode_blocks` over all blocks at once, the frozen pass's
       kernels.
    3. Each wrapper then takes a view of its layer's weight.
    4. Once every registered use has taken its view, the store zeroes the scratch (about 1 ms per GB), so no plaintext
       survives between forwards. A freed buffer would leave it in the allocator's pool.
  - **Expected cost:** close to the frozen pass's 0.64 s per forward on the 0.5B, against 1.33 s today. The PR B run
    measures it.
  - **Memory:** C plus one decoded copy of W during a forward, and C only between forwards. A model that would not fit
    at twice its weights can use `group=layers:N`, which decodes groups of N layers in the same way, at a
    latency-bound cost. The default is `all`.
- **Refused by the adapter:** anything but eager (`TargetProfile.compilation` must be None), a model with non-bf16
  linears (the encoded store is byte-level, so an FP8 model later is a layout change), and TP > 1 until a TP run is
  tested. The rank site is wired regardless.

## 4. The responder's lifecycle

- **Start.** `pous.install` starts it as the last `hooks.Service`, after the store has encoded. It is #172's native
  responder:
  - a C++ thread pinned to its own core (`cpu`), polling rather than sleeping;
  - each answer copies the block from C on its own highest-priority non-blocking stream into pinned host memory and
    sends it.
  - No Python and no GIL sit on the path, so it never blocks the step loop.
- **Stop.** `Service.stop` runs on `Hooks.uninstall`, newest first. It stops the thread, frees the pinned buffers, and
  returns the counters: answered, pings, and the CFS throttle counts over its lifetime.
- **Info** goes through `collective_rpc` (`protocol_option_info`):
  - the scheme id, the block map, and the port;
  - the leaf digests for `setup.check_server_root`.
- **The verifier** runs outside vLLM, in `verity_pous.protocol.Verifier`. It holds its own vk (private setup: it
  encodes W itself) and refuses any k or deadline the band certificate doesn't cover.
- **Deployment rule.** The responder's thread needs a CPU without a CFS quota. The pod records the counters around
  every audit.

## 5. The default-path A/B

- **Invariant.** With `PROTOCOL_OPTION` unset (or `none`), #101's manifest (`90f81868`) and run root (`7adcef49`) are
  byte-identical.
  - `protocol_options.install` returns before any import of vLLM or `verity_pous`.
  - `hooks.live()` is empty after the Commit.
- **Unit tests:**
  - `TargetProfile.to_json()` and its digest are unchanged for None;
  - `CommitConfig` with the default produces the same Commit arguments;
  - `select(None)` patches nothing.
- **Pod run:** #101's row on the PR's head through `research run`, with the manifest sha and the run root compared to
  the pins. The Attempt id goes in the PR body. This holds for every PR in the stack (§7).

## 6. The §3 choice: fail-closed for the MVP

- **The option sits outside the verified region.** A row whose declared profile has `protocol_option` set is refused
  at the Commit, with exit 3 and "fail-closed: PROTOCOL_OPTION=pous:… is outside the verified region", before any root
  is written.
  - `protocol_options.refuse_commit(profile)` is called in `pipeline/commit.py` and in the TP driver.
  - Nothing of record is produced with the option on. Serving, the timed audit and the benchmarks run through the
    POUS drivers, which use the same `install`.
- **Long term:** `TargetProfile` Definitions that cover the decode exactly. Two routes:
  - decode as input provenance, where the weights of record pin C together with the rule Dec(C) = W;
  - decode as a Program Call with its own Definition, passing `circuit-check`.

  Either one lifts the refusal.

## 7. How #172 and #188 are restructured

The PRs are stacked on #208, not on #166 at `48967d50`:

- **PR A (mine), small, with no POUS code:**
  - `protocol_options/__init__.py`, the knob, the `TargetProfile` field and `hooks.Service`;
  - the fail-closed refusal at both Commit sites;
  - the tests and the A/B.
  - The PoUW owner builds `pouw.py` on A.
- **PR B, restructured #172:**
  - `protocol_options/pous.py`;
  - `engine/pous/` without `quant.py` and `worker.py`: `codec.py`, `dense.py`, `twins.py`, `layout.py`, `native.py`
    and `pous_native.cu` stay, and a GPU twin is keyed by its scheme id and gated by that scheme's pinned vectors;
  - the drivers on `PROTOCOL_OPTION` (`pous_run` with `--scheme`, defaulting to `band-chain/d12/v1`);
  - `pous_verifier` on `verity_pous.protocol`;
  - `tests/engine/test_pous_codec.py` extended to the band.
- **PR C, restructured #188:** the band and dense kernels and `dense_bench.py`, renamed `pous-decode-bench`
  (`--scheme`), plus `pous_dense_audit.py`, all on B.
- **#172 and #188** would then be superseded. Closing them is your call and their owner's (bc-3fe582dc).
- **Commits:** the move keeps the kernels and twins byte-identical. The first commit of B and of C is a pure move, so
  the diff shows only what changed.

## 8. GPU estimate (one L40S, RunPod, $1.09/h)

| Run | What | Time | Cost |
|---|---|---|---|
| A/B for PR A | #101's row with the option unset, digests compared to the pins | 30–45 min | about $0.8 |
| Band12 end to end, bit-exact (PR B) | GPU encode of about 30 segments (132 s); the verifier's own encoding on 12 processes (about 1–2 min); greedy tokens against plaintext; seconds per forward with one batched decode (target: about 0.64 s against today's 1.33 s); 20 timed audits; a negative control with 10% of C dropped; the A/B again | 30–35 min | about $0.6 |
| EWB table through `--scheme` (PR C) | the frozen harness with all gates; its numbers compared to `r20260928-032701-b4a1`; the A/B | 15–20 min | about $0.4 |
| Margin | one retry and the native build | 30 min | about $0.5 |
| **Total** | | **about 2 pod-hours** | **about $2.2** |

Every pod is guarded and terminated as soon as it is idle. I'll stop and ask before anything goes past $10.
