---
id: 20260928T1650Z-handoff-from-pous-composition-design
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

For your review, as asked in `20260928T1635Z-handoff-from-pous-compose-protocols.md`. From the worker "Build composable vLLM protocol options" (bc-23d60f13). Replies go to `lanes/pous/`, or here.

**Status, 18:20Z:** Daniel wants the scaffold on `main` first, with the adapters following as their own PRs (PoUW's is #315). [PR #311](https://github.com/danielreuter/verity/pull/311) is at `69153d43`, and a merge request to the research coordinator follows once its recorded `check` passes. Since 17:45Z it has taken in PoUW's composition needs:
- one executor per site, with the nesting stated explicitly;
- beside sampled proofs, an executor without a Definition (`traced_as`) is refused. That covers PoUW until its int7 linear is registered, and Pearl permanently;
- weights are committed before any install.

Your review is still welcome, and I'll follow it up in a PR after the merge.


# Composable protocol options in vLLM: PoUW, POUS and sampled proofs

28 Sep 2026; revised 18:20Z to match [PR #311](https://github.com/danielreuter/verity/pull/311) at `69153d43`, with PoUW's
composition needs (`internal/pouw-mvp/composition-needs.md`, bc-dd22acf8) folded in. It supersedes the single
`none | pous | pouw` knob and keeps its hook sites. The protocol logic stays in `verity_pouw`, `verity_pous` and
`verity_sampled_proofs`; the integration imports them, never the reverse.

## 1. Config: a set, off by default

- **The set:** `name:scheme` entries, one per protocol, in install order:
  `pouw:ncp-v1,pous:band-chain/d12/v1,sampled-proofs:vllm-v1`. `config.parse_protocols` gives the one spelling.
  - The names are `pouw`, `pous` and `sampled-proofs`.
  - The schemes are the protocol packages' registered names. Sampled proofs has one, `vllm-v1`.
- **Serving:** `verity_vllm.LLM(protocols=…, protocols_config=…)` installs PoUW and POUS on the built engine. The
  default is none.
- **A row:** `verity-vllm row --protocols` (`PROTOCOLS`), or the workload's `target.protocols`.
  - Either one is the whole set, sampled proofs included, and every stage reads it as the target's `protocols`.
  - `run_row` refuses a set it can't run before any stage, single-GPU and TP alike (exit 3).
  - The default is sampled proofs alone: today's row.
- **Settings** are `{name: {...}}`, from `LLM(protocols_config=…)` or the workload's `protocols_config` block. Each
  adapter validates its own keys and refuses unknown ones. Settings are never hashed.
  - PoUW's keys: `scheme`, `beacon`, `transcript_dir`, `retain_steps`, `weight_operands`.

## 2. Hooks interface (`protocol_options/`)

~~~python
# interface.py.  Context(stage "serve"|"commit", enabled, world, enforce_eager, settings);
#                Target(model, context, rank, weight_commitments)
class Installed(Protocol):
    name: str                            # "pous:band-chain/d12/v1"
    hooks: Hooks                         # every patch and Service, via target.hooks(name): tagged with name
    outside_program: str | None          # why the Program does not describe it; the verdict is then not of record
    def commitment(self) -> dict         # for the composition record; readable after close()
    def info(self) -> dict               # certificate, roots, counters; never hashed
    def weights(self) -> Mapping | None  # plaintext of what it released, by named_parameters()/named_buffers() name
    def close(self) -> None              # hooks off (newest first), then device state; idempotent

# each adapter module: NAME, DEFAULT_SCHEME, schemes(), refusals(scheme, ctx), install(scheme, target), and optionally
EXECUTES: tuple[str, ...]                # sites where it replaces the computation (PoUW: LinearBase.quant_method.apply)
def traced_as(scheme, ctx) -> str | None       # the Definition sampled proofs traces that computation as
def keeps_weight_copy(scheme, ctx) -> bool     # a weight-derived copy stays resident across forwards
def commit_weights(scheme, target) -> Mapping  # its commitment to the plaintext weights (phase 1)
~~~

- **The selector** provides `refusals(ctx)`, `install(model, ctx) -> Composition` and `at_row`.
- **The Commit** makes one-call edits at each site, each a no-op without protocols:
  - `commit_guard`, before the engine is built;
  - `at_commit`, after the committers registered the weights and after the warm-ups;
  - `weights_view` and `register_weights`, at the replay;
  - `into_verdict`, before `verdict.json`.
- **`engine/hooks.py`** gains `Service`, for POUS's responder, and tagged entries (`live(tag)`, `undeclared()`).
- **Layering:** `protocol_options` sits in the `acquire` layer (P9). TP ranks will receive a picklable install, as
  `taps.for_ranks` does. TP is refused until then.

## 3. Ordering and composition rules

**Nesting at a site** (`SITES`, outermost first) is stated explicitly. At most one option executes at a site, and it is
innermost:
- at `LinearBase.quant_method.apply`, POUS wraps: it hands the decoded `W` inward and releases the plaintext;
- PoUW executes there: it replaces the GEMM and reads the weight from the layer it is called with;
- sampled proofs commits at the module boundary, outside every site. Its replay evaluates Definitions and never re-runs
  an executor.

Install order (`config.PROTOCOLS`) is innermost first; uninstall is the reverse. POUS's responder is the last thing
started and the first stopped.

**Phases:**
1. Every option commits to the plaintext `W` of record (`commit_weights`). The model is untouched and no beacon is read.
   All commitments bind to `weights_pin`.
2. Every option installs. PoUW reads its beacon and salt here.
3. Serving. Installs come after vLLM's profile and dummy runs and after the Commit's warm-ups, so no warm-up is counted
   as work.

| Protocol | Commits to | Link |
|---|---|---|
| sampled proofs | the run root over the required values of `P(profile)`; the weights root | the profile digest carries the set; `weights_pin` |
| POUS | its commitment to `W` before the salt; the storage root of `C = Enc(W, salt)`; timed answers | `Dec(C) = W` exactly |
| PoUW | weight roots; per unit, the A-row root and the tile transcript under the epoch salt | its A rows and weight root must match the traced linear's boundary (below) |

**The composition record**, `verity-vllm/protocol-composition/v0` (`protocols.json`), holds, per protocol, its entry,
its weight commitment and its `commitment()`, together with the profile digest and a SHA-256 over its canonical JSON.
Each protocol's own verifier checks its own claims.

**Weights of record.** POUS's `weights()` returns the plaintext it released. Tied names map to one tensor object. The
replay reads through `weights_view` / `register_weights`.

**Refused by the selector:**
- an unknown protocol, an unregistered scheme, or an adapter not on this tree;
- two schemes of one protocol, or settings for a protocol the run doesn't enable;
- TP > 1;
- sampled proofs outside the Commit;
- two executors at one site;
- with `pous` on, an option whose `keeps_weight_copy` is True;
- **beside sampled proofs, an executor without `traced_as`.** Sampled proofs must trace what PoUW declares, never the
  noised GEMM as if it were the stock one. So `pouw` + `sampled-proofs` is refused until PoUW's linear has a
  Definition. `pearl-fp8-v4` stays refused beside sampled proofs, because its useful output depends on its noise.

**PoUW's resident weight copy** is signalled by its `weight_operands` setting:
- `"resident"`, the default, keeps a copy;
- `"per-forward"` doesn't.

**Refused by the adapters:** compiled execution, TP > 1, layers outside a scheme's domain. The embedding isn't wrapped:
POUS covers the linears only (question 5).

**What a Commit does with more than sampled proofs:**
- **With POUS,** it runs as a placeholder composition. It installs POUS, writes `protocols.json`, and marks
  `verdict.protocols.of_record = false`. The Program is unchanged, since the decode is input provenance and `W` is
  bit-identical.
- **With PoUW,** it is refused (above).

**How PoUW gets covered (question 2)**, from PoUW's note. Sampled proofs traces the declared `ncp-v1` linear, not the
noised execution:
- **The computation:** `x → A` by the pinned quantizer (`verity.pouw.symmetric-int7-rowmax-rne-f32/v1`, plus the H2
  rotation for branch E), then `Z = A·Bᵀ` exactly in int32, then `y = bf16(fp32(s_i)·fp32(t_j)·Z_ij) + bias`.
- **The Definition:** a new one for that int7 linear, passing `circuit-check`. It is the same Definition a W7A7 serving
  path would need. PoUW's `traced_as` names it, and the profile binds it the way `moe_construction` binds its
  Definitions.
- **The link:** the traced boundary includes A's rows (one two's-complement byte per entry) and the weight root, and the
  verifier recomputes PoUW's `root_a` and weight root from them. Otherwise a prover could do the work on one A and serve
  another.
- **PoUW's side claim:** the noise, salt, 3k-deep GEMM and checkpoints stay out of the Program. PoUW's own audit checks
  them.
- **Capture:** it happens at the `apply` boundary only, never inside PoUW's forming ops. Openings come from retained
  copies, never from a replay run through the executor.

**Not built:** per-option memory budgets, refused at install when the composition doesn't fit.

## 4. The `TargetProfile` field

`protocols: tuple[str, ...] | None = None`. `None` means sampled proofs alone; it is omitted from `to_json()`, so every
digest is unchanged (`TargetProfile()` is still `86c255b3…`). A declared set is the whole set in its one spelling,
sampled proofs included. The profile refuses:
- a set without sampled proofs;
- the default spelled out;
- duplicates or a non-canonical order.

The digest changes with the set, so `check_reuse` refuses by field. The grammar lives in `config.py`.

## 5. Sampled proofs as an option

`sampled_proofs.py` is a declaration adapter:
- its scheme `vllm-v1` is the commitment scheme `verity_vllm.commit.scheme` and the replay law, with the strata as RUs
  at p = 1;
- its hooks are the Commit's committer and taps, unchanged;
- its commitment is the run roots and the Program and manifest digests, which the Commit binds.

Alone, every call returns before any adapter is imported (checked in a subprocess), and the Commit runs the same code.
The #101 A/B (manifest `90f81868`, run root `7adcef49`) needs a pod and hasn't been run.

## Open questions for Daniel (the built default is marked **Built:**)

1. **The composed Commit.** When the set includes POUS or PoUW, should the Commit's verdict be placeholder, not of
   record? Or should the Commit refuse?
   - **Built:** placeholder with POUS. With PoUW it is refused until question 2 is settled. Until then, all three in one
     run means POUS and PoUW serving through `LLM`, with the Commit running sampled proofs and POUS.
2. **PoUW under sampled proofs, of record.** PoUW proposes the route above: a Definition for the declared int7 linear,
   plus the link between the traced A rows and weight root and PoUW's roots. Build it, and let it lift the refusal?
   - **Built:** refused beside sampled proofs, and Pearl refused for good.
3. **POUS with PoUW.** Must PoUW prepare its weight operands per forward, or may it keep a resident copy outside POUS's
   claim?
   - **Built:** per forward (`weight_operands = "per-forward"`) is required when both are on.
4. **Challenge order.** One beacon round after every commitment, or one per protocol?
   - **Built:** one per protocol. The domains are disjoint, so one beacon could feed all three, each keeping
     commit-then-draw.
5. **The embedding under POUS.** Wrap `VocabParallelEmbedding` and the tied head (28% of Qwen2.5-0.5B's weight bytes)?
   - **Built:** linears only.
