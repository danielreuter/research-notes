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

**Status, 17:45Z:** the scaffold is the draft [PR #311](https://github.com/danielreuter/verity/pull/311) on `cursor/vllm-protocol-composition-9924`, at `0eeb905c`. The interface is stable, and the POUS and PoUW adapters are stacking on it. Since 17:15Z it has gained:
- `Installed.weights()`, read by the replay through `weights_view` / `register_weights`;
- `keeps_weight_copy`, the one rule for a resident weight copy;
- the row knob `PROTOCOLS`, refused in `run_row` before any stage.

`commit.py` and `tp/commit.py` get only one-call edits, and the P10 sizes don't grow. The #101 A/B needs a pod, and I haven't run it.


# Composable protocol options in vLLM: PoUW, POUS and sampled proofs

28 Sep 2026; revised 17:40Z to match [PR #311](https://github.com/danielreuter/verity/pull/311) (branch
`cursor/vllm-protocol-composition-9924`). It supersedes the single `none | pous | pouw` knob of the 05:40Z plans and
keeps their hook sites. The protocol logic stays in `verity_pouw`, `verity_pous` and `verity_sampled_proofs`; the
integration imports them, never the reverse.

## 1. Config: a set, off by default

- **Entries:** `name:scheme`, at most one per protocol, in install order:
  `pouw:ncp-v1,pous:band-chain/d12/v1,sampled-proofs:vllm-v1`.
  - The names are `pouw`, `pous` and `sampled-proofs`.
  - A scheme is a name its package registers: `verity_pouw.schemes.SCHEMES`, `verity_pous.schemes.REGISTRY`, or
    `vllm-v1` for sampled proofs.
  - `config.parse_protocols` gives the one spelling.
- **Serving:** `verity_vllm.LLM(protocols=…, protocols_config=…)` installs PoUW and POUS. The default is none.
- **A row:** `verity-vllm row --protocols` (`PROTOCOLS`), or the workload's `target.protocols`.
  - Either way it is the whole set, sampled proofs included, and every stage reads it as the target's `protocols`.
  - `run_row` refuses a set it can't run before any stage starts, for single-GPU and TP rows alike (exit 3, `at_row`).
  - The default is sampled proofs alone, today's row.
- **Settings are not identity.** They are `{name: {...}}`: `LLM(protocols_config=…)`, or the workload's
  `protocols_config` block, which sits beside the target, not in it.
  - Each adapter validates its own keys; a key for a protocol the run doesn't enable is refused.
  - Settings are never hashed. Anything that changes the computation belongs in the scheme id.

## 2. Hooks interface (`protocol_options/`)

~~~python
# interface.py.  Context(stage "serve"|"commit", enabled, world, enforce_eager, settings); Target(model, context, rank)
class Installed(Protocol):
    name: str                          # "pous:band-chain/d12/v1"
    hooks: Hooks                       # every patch and Service, made through target.hooks(name): tagged with name
    outside_program: str | None        # why the Program does not describe what it changes; a verdict is then not of record
    def commitment(self) -> dict       # what it commits to (the composition record); readable after close()
    def info(self) -> dict             # certificate, counters, port; never hashed
    def weights(self) -> Mapping | None  # plaintext of what it released, by named_parameters()/named_buffers() name
    def close(self) -> None            # hooks off, then device state; idempotent
# Option(name, hooks, commits, details, outside_program, decoded, release) is a ready-made Installed

# each adapter module (sampled_proofs.py, pous.py, pouw.py)
NAME: str; DEFAULT_SCHEME: str
def schemes() -> tuple[str, ...]
def refusals(scheme, ctx) -> tuple[str, ...]      # from the Context alone, before the engine exists
def install(scheme, target) -> Installed
def keeps_weight_copy(scheme, ctx) -> bool        # optional (False): a weight-derived copy stays resident across forwards
~~~

- **The selector** (`__init__.py`) provides `refusals(ctx)` and `install(model, ctx) -> Composition`. An adapter is
  imported by name, and only when its protocol is enabled.
- **`Composition`** keeps every `Hooks` it handed out. If an install raises, all of them come off, newest first.
  `close()` also runs newest first. `record()` and `verdict()` produce the record and the verdict block (§3).
- **The Commit makes one call at each of four sites, each a no-op without protocols:**
  - `commit_guard`, before the engine is built;
  - `at_commit`, after every committer has registered the weights;
  - the replay's `weights_view` and `register_weights`;
  - `into_verdict`, before `verdict.json`.

  The TP Commit and the hot worker refuse a declared set.
- **`engine/hooks.py` gains:**
  - `Service`, a started and stopped entry for POUS's responder, whose counters are kept in `result`;
  - a tag on every entry (`live(tag)`), and `undeclared()`, which finds patches from an option that was never declared.
- **Layering:** `protocol_options` is in the `acquire` layer (P9). A TP install will reach the ranks as a picklable
  callable, as `taps.for_ranks` does, so `engine/rank_worker.py` imports nothing new.

## 3. Ordering and composition rules

1. **Weights first.** Every protocol commits to the plaintext `W` of record before anything changes the model. All three
   bind to the checkpoint's `weights_pin`:
   - sampled proofs: the committer's weights root;
   - POUS: its commitment to `W`, made before its salt exists;
   - PoUW: its weight roots.
2. **`pouw`, innermost.** It wraps each `LinearBase.quant_method.apply`, found by type, replaces the GEMM, and reads the
   weight from the layer it is called with.
3. **`pous`, around it.** It wraps the same `apply`:
   - it decodes `W` from `C` and hands the inner `apply` a layer holding the decoded weight;
   - install releases the plaintext;
   - the responder (a `Service`) starts last.
4. **`sampled-proofs`, outermost.** The Commit's committer and taps work at module level, as today.

**Why this order:** PoUW's GEMM reads what POUS stores, and sampled proofs commits what the model computed. Uninstall is
the reverse: the responder, then POUS (restoring `W`), then PoUW.

| Protocol | Commits to | Link to the others |
|---|---|---|
| sampled proofs | the run root over the required values of `P(profile)`; the weights root over `W` | the profile digest (which carries the set); `weights_pin` |
| POUS | its commitment to `W` before the salt; the storage root of `C = Enc(W, salt)`; timed answers | `Dec(C) = W` exactly; `weights_pin` |
| PoUW | weight roots; each GEMM's A-row roots and tile transcript under the epoch salt | A rows = the quantized input of the linear Call sampled proofs commits (stated, not checked) |

**The composition record** is `verity-vllm/protocol-composition/v0` (`protocols.json`). It holds the stage, the
profile digest, and per protocol its entry and `commitment()`, with the SHA-256 of its canonical JSON. It is a
placeholder: each protocol's verifier checks its own claims, and nothing checks the cross-links yet.

**Weights of record.** POUS returns the plaintext of what it released from `weights()`. Tied names map to one tensor
object. The committer's first registration runs before any install. After install, the replay reads and re-registers
the live weights through `weights_view` / `register_weights`, which are the model itself when nothing was released.

**Refused, by the selector:**
- an unknown protocol, an unregistered scheme, or an adapter not on this tree;
- two schemes of one protocol, or settings for a protocol the run doesn't enable;
- TP > 1;
- sampled proofs outside the Commit;
- with `pous` on, any option whose `keeps_weight_copy` is True, since its GEMMs would bypass `C`. The selector owns this
  rule, and neither adapter checks the other.

**PoUW's signal** is its own settings key `weight_operands`:
- `"resident"` (the default, prepared at install and noised once per epoch) keeps a copy;
- `"per-forward"` prepares operands from the weight each `apply` is handed;
- a scheme that can't prepare per forward refuses `"per-forward"` in its own `refusals`.

**Refused by the adapters, so both agree:** compiled execution, TP > 1 (until tested), and a layer outside the scheme's
domain. **The embedding is not wrapped:** POUS covers the `LinearBase` layers only, and says "linears only" in `info()`
and `commitment()` (question 5).

**A Commit with more than sampled proofs** is a placeholder composition. It installs the others, writes
`protocols.json` and `versions.protocols`, and gives `verdict.json` a block with `protocols.of_record = false` whenever
an option sets `outside_program`. It is never a verdict of record.
- **POUS:** the Program is unchanged, because the decode is input provenance and `W` is bit-identical.
- **PoUW:** the GEMM Calls don't describe PoUW's GEMM. The goal is a PoUW linear construction that `target.protocols`
  binds, the way `moe_construction` binds its Definitions, and that passes `circuit-check`.

## 4. The `TargetProfile` field

- **`protocols: tuple[str, ...] | None = None`.** `None` means sampled proofs alone, and is omitted from `to_json()`, so
  every digest is unchanged: `TargetProfile()` is still `86c255b3…`, pinned in the test.
- **When set,** it holds the whole set in its one spelling, sampled proofs included.
- **Refused:** a set without sampled proofs (a profile is the target of sampled proofs' Program), the default spelled
  out, duplicates, and a non-canonical order.
- **The digest changes with the set,** so `check_reuse` refuses, by field, to use a composed artifact for the default.
- The grammar is in `config.py`, so `program/` validates without importing the selector.

## 5. Sampled proofs as an option

- **`sampled_proofs.py` is a declaration adapter.** Its one scheme, `vllm-v1`, is the Commit path as it runs today:
  - the commitment scheme `verity_vllm.commit.scheme`, over `verity.commitments.vllm_v1`;
  - the replay law, with the strata as RUs at p = 1 (`commit.challenge.stratum_picks` over `verity_sampled_proofs.law`).
- **It adds no hooks.** The Commit's committer and taps are its hooks. The Commit binds the run roots and the Program
  and manifest digests as its commitment.
- **Alone,** the target has no `protocols`, every call above returns before any adapter is imported (checked in a
  subprocess), and the Commit runs the same code. The #101 A/B (manifest `90f81868`, run root `7adcef49`) must be
  byte-identical in every PR of the stack. It needs a pod and hasn't been run.

## 6. Owners

- **This scaffold (#311):** the selector, the interface, `sampled_proofs.py`, `engine/hooks.py`, the grammar, the
  profile field, `LLM(protocols=…)`, the row knob, the Commit's calls, and `tests/protocol_options/` (CPU, torch-free).
- **Stacked on it:** `pous.py` (bc-13eada34, #208) and `pouw.py` (bc-dd22acf8, #218).

## Open questions for Daniel

1. **The composed Commit.** Placeholder, with its verdict not of record (built; it is what makes all three in one run
   possible now)? Or refused, as the vLLM coordinator's fail-closed MVP?
2. **PoUW under sampled proofs, of record.** A PoUW linear Definition that the replay re-evaluates? Or delegation to
   PoUW's tile audit, with the A-row to boundary-value link checked?
3. **POUS with PoUW.** Require `weight_operands = "per-forward"` (costly for Pearl's FP10 planes)? Or accept a resident
   PoUW copy that lies outside POUS's claim?
4. **Challenge order.** One beacon round after all three commitments are registered, or one per protocol?
5. **The embedding under POUS.** Linears only leaves the embedding and the tied LM head in plaintext: 28% of
   Qwen2.5-0.5B's weight bytes. Should POUS also wrap `VocabParallelEmbedding` and `ParallelLMHead`?
