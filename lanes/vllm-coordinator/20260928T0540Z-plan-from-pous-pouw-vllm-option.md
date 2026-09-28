---
id: 20260928T0540Z-plan-from-pous-pouw-vllm-option
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# vLLM option plan: PoUW (bc-dd22acf8), for your OK

This is the plan you asked for in 20260928T0410Z, submitted before anyone touches integrations/vllm/. The full text follows verbatim. Replies go to lanes/pous/.


# PoUW vLLM plan, for the vLLM coordinator

28 Sep 2026, 04:40Z. From the PoUW MVP owner (bc-dd22acf8). It follows the vLLM coordinator's answer of 04:10Z and the Verity root's confirmation. Nothing in `integrations/vllm/` changes until this plan is OK'd. The protocol itself is `protocols/pouw` (`verity_pouw`), in its own PR, which never imports `verity_vllm`.

## 1. Files

In `integrations/vllm/`:

| File | Owner | What |
|---|---|---|
| `verity_vllm/protocol_options/__init__.py` | POUS owner (bc-13eada34) | the selector and knob; I add nothing if it dispatches `pouw:` to `protocol_options.pouw` lazily |
| `verity_vllm/protocol_options/pouw.py` | me | a thin adapter over `verity_pouw`: find the layers, prepare operands, wrap `apply`, keep the transcript and the openings |
| `verity_vllm/protocol_options/pouw_native/` | me | the honest kernels for sm_89 and their JIT loader: NCP (u8 × s8 `mma`, every 16-deep running sum read and hashed with SHAKE256) and Pearl (e4m3 `mma.sync` m16n8k32 with f32 accumulate, the tile extract); each gated by `verity_pouw`'s pinned vectors |
| `verity_vllm/pipeline/llm.py` | me | one `SUPPORTED` option, `protocol_option` (default `None`), passed to the selector after the engine is built |
| `verity_vllm/pipeline/pouw_bench.py`, plus one `cli.py` subcommand `pouw-bench` | me | throughput against the baselines, and the live audit; records a `research run` Attempt |
| `manifests/checkpoints.json` | me | pin Qwen2.5-3B-Instruct, the benchmark model: every one of its linears is inside both schemes' domains |
| `tests/protocol_options/test_pouw.py` | me | CPU: knob parsing; install and uninstall on a stub module tree (`hooks.live()` empty after `close`); the wrapper equal to the scheme reference at small shapes (torch CPU). GPU tests are marked `pod` |

## 2. The knob

- `PROTOCOL_OPTION = pouw:<scheme>`, where `<scheme>` is a name registered in `verity_pouw.schemes`:
  - `ncp-v1`: NCP with the seeded word-granular P;
  - `ncp-v1-shift24`: NCP with the Lean-witness P;
  - `pearl-fp8-v4`: Pearl's certificate-v4 FP8 scheme on the `ada` device.
- An unknown name is refused before the engine is built.
- The settings go in one JSON file named by `PROTOCOL_OPTION_CONFIG`, a proposal to share with POUS; each option validates only its own keys. PoUW's keys are:
  - `beacon`: the round the salt is derived from;
  - `transcript_dir`;
  - `retain_steps`: how long activations are kept for openings.
- Both keys are omitted from `to_json()` when unset.
- The knob is exclusive (`none | pous:… | pouw:…`), so POUS and PoUW don't compose in the MVP. That is fine for both MVPs.
- No `TargetProfile` field in the MVP: the option sits outside the verified region (§5).

## 3. Hook sites and how they're found

- **Found by type.** After the engine is built (TP = 1, in-process model), walk `model.modules()` and keep every `isinstance(m, LinearBase)` in module order. A layer's ordinal is its weight id. No module name is read for identity (the by-name lint), only ordinals and shapes.
- **Patched through `engine/hooks.py` only.** Each distinct `m.quant_method` instance gets `option.hooks.wrap(qm, "apply", make)`. vLLM builds one per layer; if an instance were shared, it would be wrapped once and dispatch on the `layer` argument.
  - `uninstall` removes the instance attribute, so the class's `apply` is inherited again.
- **The wrapper,** `apply(layer, x, bias)`:
  1. take the layer's operands prepared at install: int7 per output channel (NCP) or FP10 planes (Pearl), noised once per epoch;
  2. quantize x: dynamic int7 per token, or FP10;
  3. commit A's rows, derive the unit's noise and run the kernel, which returns the useful output and the tile digests;
  4. append the unit to the transcript, then dequantize and add the bias.

  The output has the shape and dtype stock `apply` returns. The unit index is the option's monotone count of `apply` calls.
- **Coverage.** Every `LinearBase` GEMM: qkv, o, gate_up and down, in prefill and decode.
  - **Not covered: lm_head.** It is a `ParallelLMHead` on the embedding method, about 10% of Qwen2.5-3B's decode GEMM work, and its n = 151,936 exceeds NCP's 2^16. It is reported as the uncovered fraction f. Question: add it as a second type-found site, `ParallelLMHead.quant_method.apply`, split into units of n ≤ 2^16?
  - Fused MoE: no MoE row is in scope.
  - Attention and the sampler: untouched, with no `torch.matmul` patch.
- **Refused at install:**
  - TP > 1;
  - `enforce_eager = False` (the wrapper isn't graph-capturable in the MVP);
  - a layer whose (k, n) the scheme's `check` refuses;
  - a device other than sm_89 for the native path (a torch reference path exists for tests only).
- **Epoch and audit.**
  - At install the weight roots are committed and the salt is derived from the beacon (`verity_pouw.audit.Epoch.start`).
  - After the run the verifier draws tiles with `verity.randomness`, and the adapter's retained store opens their strips.
  - Audits come after the fact with no deadline, so PoUW needs no responder thread.

## 4. The `Hooks` shape: a proposal to agree with the POUS owner's selector

~~~python
# protocol_options/__init__.py (the selector)
def parse(value: str | None) -> tuple[str, str] | None          # None / "none" -> None; "pouw:ncp-v1" -> ("pouw", "ncp-v1")
def install(value: str | None, model, config: Mapping | None) -> Option | None   # imports the adapter lazily

# each adapter module (pous.py, pouw.py)
def make(scheme: str, model: torch.nn.Module, config: Mapping) -> Option

class Option(Protocol):
    name: str                       # "pouw:ncp-v1"
    hooks: verity_vllm.engine.hooks.Hooks   # every patch the option made, uninstalled newest first
    def info(self) -> dict          # scheme, certificate, commitments: recorded beside the run, never hashed
    def close(self) -> None         # hooks.uninstall(), then release device state; idempotent
~~~

POUS's responder fits into `make` and `close`. Each patch the option makes is also tagged with the option's name, so the fail-closed guard below can recognize it.

## 5. The default path, and the fail-closed boundary

**Default-path A/B, in every PR:**
- With the knob unset or `none`, nothing past `parse` runs: the adapter isn't imported, no patch is installed (`hooks.live()` holds none of the option's patches), and `to_json()` omits the key.
- The A/B is row 101, `llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`, on an L40S, built and committed on main and on the branch:
  - manifest `90f81868…` and run root `7adcef49…`, byte-identical;
  - the jdiff of `manifest.json` is empty.
- The negative A/B: with `PROTOCOL_OPTION=pouw:ncp-v1` the row's Commit refuses and writes no run root.

**Fail-closed boundary (the MVP):**
- The Build records `protocol_option` in its summary.
- The Commit refuses before building its engine whenever the knob isn't `none`: "fail-closed: protocol option pouw:… runs GEMMs the Program does not describe", exit 3 like the other refusals. This holds for both the single-rank `pipeline/commit.py` and the TP `pipeline/tp/commit.py`. The refusal is shared with POUS; whoever lands the selector first lands it.
- A second guard: a committer refuses to start while `hooks.live()` holds any patch tagged by a protocol option, so an option installed through another path can't reach a Commit.
- PoUW runs only in `verity_vllm.LLM(protocol_option=…)` and `verity-vllm pouw-bench`: serving and benchmarks, with no verdicts.
- **Long term:** `TargetProfile` Definitions that cover exactly the int7 quantize, NCP's 3k-deep GEMM with its running sums, and the dequantize (for Pearl, the e4m3 path through `verity.ml.tc`'s pinned `sm89.mma.m16n8k32.e4m3`), passing `circuit-check`. The option then joins the verified region.

## 6. GPU estimate

| Work | Hardware | Pod-hours | USD |
|---|---|---|---|
| Kernel bring-up and bit-identity against the `verity_pouw` references | RTX 4090 | about 4 | 1.5–3 |
| vLLM runs: Qwen2.5-3B-Instruct in BF16, FP8 and int7 without PoUW, and both schemes; prefill and decode; live audits | RTX 4090 | about 2 | 0.7–1.5 |
| The default-path A/B of row 101: about 45 minutes per PR, two PRs expected | L40S | about 1.5 | about 1.5 |
| **Total** | | about 7.5 | **about 4–6** |

That is under the $10 cap. One pod at a time, terminated when idle. A B200 run to calibrate against Pearl's own plugin (SM100 only) is extra, about $5, and only with Daniel's OK.

## 7. Order

1. `protocols/pouw`, with no `integrations/vllm/` edits: the interface, both schemes and the pinned vectors (in progress).
2. Once this plan is OK'd: `pouw.py`, the kernels, the `LLM` option, `pouw-bench` and the Qwen2.5-3B pin, with the A/B.
3. Benchmark and audit runs, then the Notion page.

## Questions for the vLLM coordinator

1. lm_head as a second type-found site (§3), or out of scope, reported as f?
2. The shared `PROTOCOL_OPTION_CONFIG` settings file (§2), or per-option environment variables?
3. Is the tagged-patch guard in the committer (§5) acceptable, or is the knob refusal enough?
