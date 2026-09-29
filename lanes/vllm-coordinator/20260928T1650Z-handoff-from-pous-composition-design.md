---
id: 20260928T1650Z-handoff-from-pous-composition-design
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

From the worker "Build composable vLLM protocol options" (bc-23d60f13). Revised 23:59Z to #311 `4c4b8290`, after your GO (`lanes/pous/20260928T2115Z-verdict-from-vllm-coordinator-311-312-315.md`). It adds a merge plan (§7) and PoUW's per-forward default (#315 `14000398`).


# Composable protocol options in vLLM: PoUW, POUS and sampled proofs

28 Sep 2026; revised 23:59Z to match [PR #311](https://github.com/danielreuter/verity/pull/311) at `4c4b8290`: `69153d43`
plus the default-path test the vLLM coordinator asked for, merged with `main` `816c3682` (train T). PoUW's composition needs
(`internal/pouw-mvp/composition-needs.md`, bc-dd22acf8) are folded in, and the vLLM coordinator's verdict on the stack is GO
with conditions (§7). It supersedes the single
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
  - `weight_operands` defaults to `per-forward`, and `resident` is opt-in (§3).

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
- `"per-forward"`, the default in #315 at `14000398`, prepares operands from the weight each `apply` is handed, forming them
  in chunks. It keeps no copy, so it composes with POUS.
- `"resident"` is opt-in. It is prepared at install and noised once per epoch, keeps a copy, and is refused with POUS.
- `14000398` was not yet on GitHub at 23:59Z. #315's pushed head, `58c3bc49`, still defaults to `resident`.

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

Alone, every call returns before any adapter is imported, and the Commit runs the same code.
`test_with_no_protocols_the_commit_path_is_a_no_op` checks this in a fresh interpreter. With `target.protocols` unset:
- `at_commit` is None and no adapter module is loaded;
- `into_verdict` leaves the verdict byte-identical and writes nothing;
- `weights_view` is the model itself.

The vLLM coordinator takes that test in place of a pod A/B. The follow-up epoch's first row on `main` is the live check
(§7).

## 6. Owners

- **#311 (this scaffold, bc-23d60f13):** the selector, the interface, `sampled_proofs.py`, `engine/hooks.py`, the grammar,
  the profile field, `LLM(protocols=…)`, the row knob, the Commit's calls, and `tests/protocol_options/` (CPU,
  torch-free).
- **#312 (`pous.py`, bc-13eada34)** and **#315 (`pouw.py`, bc-dd22acf8),** stacked on it, over the protocol packages from
  #208 and #218.

## 7. Merge plan

The vLLM coordinator's verdict (`lanes/pous/20260928T2115Z-verdict-from-vllm-coordinator-311-312-315.md`) is GO on all
three, in one train, with two conditions:
- merge after tonight's epoch rows are written (by about 23:30Z) and after D3′;
- a CPU test of the default path, which #311 has had since `bb1db10e`.

**Order:**
1. **D3′ first** (#208 `verity_pous`, #218 `verity_pouw`, #298 and #301). #298 and #301 also edit `pipeline/commit.py` and
   `pipeline/tp/commit.py`. At 23:59Z D3′ was not on `main`.
   - #311 then merges D3′ in and re-runs the recorded `check`. The one conflict is two imports at the same place in
     `pipeline/tp/commit.py`; the resolution was tried against D3 `de4118fc`.
2. **#311, the scaffold.**
   - **Adds:** the selector and composition, the adapter interface, the sampled-proofs adapter, `Service` and tagged
     hooks, `TargetProfile.protocols`, `LLM(protocols=…)`, the row knob, and the Commit's calls.
   - **Runtime effect:** none until a set is declared.
   - **Evidence:**
     - `check` `r20260928-200103-b2b8` passed on `69153d43`;
     - on `4c4b8290`, `check` `r20260928-235507-0a7b` is running, and the vLLM tests under torch ran as
       `r20260928-235358-f68a`.
3. **#312, POUS.**
   - **Adds:** `pous.py` over `verity_pous`, `band-chain/d12/v1` by default.
   - **How it works:** it wraps the linears' `apply` and hands the decoded `W` inward. It releases the plaintext, and
     returns it through `Option.decoded` for `weights_view`. The responder runs as a `Service`. It covers the linears only.
   - **Result:** `LLM(protocols="pous:…")` serves from the encoded store. A row with sampled proofs and POUS runs as a
     placeholder composition, with `verdict.protocols.of_record = false`.
4. **#315, PoUW.**
   - **Adds:** `pouw.py` over `verity_pouw`. It is the one executor at the linears' `apply`, with `EXECUTES`,
     `traced_as` returning None, and `commit_weights`.
   - **Settings:** `weight_operands` defaults to `per-forward` (chunked forming), with `resident` opt-in.
   - **Label:** #315 is labelled not auditable.
   - **Result:** `LLM(protocols="pouw:ncp-v1")` and `pouw` + `pous` serve.

Each adapter merges #311's final head, re-runs its own `check`, and lands after #311 in the same train.

**What stays refused after the train:**
- `pouw` beside sampled proofs, in any scheme, until the int7 linear has a Definition (question 2). `pearl-fp8-v4` stays
  refused beside sampled proofs for good.
- `pous` with `pouw` at `weight_operands = "resident"`.
- TP > 1, compiled execution, protocol options in the hot Commit worker, and sampled proofs in `LLM`.
- The embedding and the tied head under POUS (question 5).

**Composable after the train:**
- **Serving, through `LLM`:** `pous`, `pouw`, and `pous` + `pouw`.
- **A row:** sampled proofs alone, which is today's Commit, unchanged. Also sampled proofs + `pous`, as the placeholder
  composition.

**First evidence on `main`:** the follow-up epoch's first re-recorded row (the verdict's condition 2(b)). Its regression
record must equal the epoch's rule, with no `protocols` key in `verdict.json`.

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
   - **Built:** per forward is required when both are on. It is now PoUW's default (#315, `14000398`); `resident` is
     opt-in and refused with POUS.
4. **Challenge order.** One beacon round after every commitment, or one per protocol?
   - **Built:** one per protocol. The domains are disjoint, so one beacon could feed all three, each keeping
     commit-then-draw.
5. **The embedding under POUS.** Wrap `VocabParallelEmbedding` and the tied head (28% of Qwen2.5-0.5B's weight bytes)?
   - **Built:** linears only.
