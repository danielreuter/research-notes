---
id: 20260928T1650Z-handoff-from-pous-composition-design
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

For your review, as asked in `20260928T1635Z-handoff-from-pous-compose-protocols.md`. From the worker "Build composable vLLM protocol options" (bc-23d60f13). Replies go to `lanes/pous/`, or here. I start the scaffold now, on `cursor/vllm-protocol-composition-9924` (a draft PR), and will adjust it to your review. Touching `pipeline/commit.py` and `pipeline/tp/commit.py` is limited to one call each (`at_commit`), which is a no-op when `target.protocols` is unset. Tell me if that conflicts with the epoch work.


# Composable protocol options in vLLM: PoUW, POUS and sampled proofs

28 Sep 2026, 16:50Z. Design for the shared scaffold under `integrations/vllm/verity_vllm/protocol_options/`. It
supersedes the single `none | pous | pouw` knob of the 05:40Z plans and keeps their hook sites. Protocol logic stays in
`verity_pous`, `verity_pouw` and `verity_sampled_proofs`; the integration imports them, never the reverse.

## 1. Config: a set, off by default

- **Entry:** `name:scheme`. The names are `pouw`, `pous` and `sampled-proofs`. A scheme is a name the protocol package
  registers: `verity_pouw.schemes.SCHEMES`, `verity_pous.schemes.REGISTRY`, and `vllm-v1` for sampled proofs.
- **Set:** at most one scheme per protocol, written in install order (§3), comma-joined. For example
  `pouw:ncp-v1,pous:band-chain/d12/v1,sampled-proofs:vllm-v1`. There is one spelling: the parser refuses unknown names,
  duplicates, a missing scheme and a non-canonical order.
- **Where it is set:**
  - `verity_vllm.LLM(..., protocols="pous:…,pouw:…")`, for serving and benchmarks. The default is the empty set.
  - A row declares it as `target.protocols`, in the workload or through `--target`. So the Build, Match, Commit and
    Check all read the same copy. The default (`None`) is sampled proofs alone, which is today's row.
- **Settings are not identity.** `PROTOCOLS_CONFIG` names one JSON file, `{name: {...}}`. It holds PoUW's beacon,
  `transcript_dir` and `retain_steps`, and POUS's responder CPU and port and its decode group. Each adapter validates only
  its own keys, and the file is never hashed. Anything that changes the computation belongs in the scheme id.

## 2. Hooks interface

~~~python
# protocol_options/interface.py
@dataclass(frozen=True)
class Target:                      # what an adapter installs onto
    model: Any; stage: str         # "serve" (LLM) | "commit"
    enabled: Selection             # the whole set, so an adapter sees what it is composed with
    rank: int = 0; world: int = 1; settings: Mapping = {}

class Installed(Protocol):         # what install returns
    name: str                      # "pous:band-chain/d12/v1"
    hooks: engine.hooks.Hooks      # every patch and Service it made, tagged with `name`
    def commitment(self) -> dict   # what it commits to, for the composition record (JSON)
    def info(self) -> dict         # certificate, counters, port: beside the run, never hashed
    def close(self) -> None        # hooks.uninstall(), then device state; idempotent

# each adapter module (sampled_proofs.py, pous.py, pouw.py) defines
NAME: str; DEFAULT_SCHEME: str
def schemes() -> tuple[str, ...]                          # from its protocol package
def refusals(scheme: str, ctx: Context) -> tuple[str, ...]  # before the engine is built: stage, TP, eager, dtype, the set
def install(scheme: str, target: Target) -> Installed
~~~

- **The selector** (`protocol_options/__init__.py`) provides `parse`, `refusals(selection, ctx)`, and
  `install(selection, target) -> Composition`. It also provides `at_commit(profile, model, …)`, the Commit's one call.
  Each adapter is loaded by name when it is selected, never at import.
- **`Composition`** installs the adapters in order. If any install raises, it uninstalls the ones already installed. Its
  `close()` uninstalls newest first, and `record()` writes the composition record (§3).
- **`engine/hooks.py` gains two things:**
  - `Service`: an in-process service (POUS's responder) that is started as a `Hooks` entry, listed in `live()`, and
    stopped newest first;
  - an optional tag on every entry, so a committer can find patches from an option that was never declared
    (`live(tag=…)`).

## 3. Ordering and composition rules

1. **Weights first.** Nothing changes the model until every enabled protocol has committed to the plaintext `W` of
   record:
   - sampled proofs: the committer's weights root;
   - POUS: its commitment to `W`, made before its salt exists;
   - PoUW: its weight roots (`Epoch.start`).

   All three bind to the checkpoint's `weights_pin`. In the Commit, this means the composition is installed after
   `register_weights`, beside `TAPS.attach`.
2. **`pouw` is installed first, innermost.** It wraps each `LinearBase.quant_method.apply`, found by type, and replaces
   the GEMM. It reads the weight from the `layer` argument it is called with.
3. **`pous` is installed next, around PoUW.** It wraps the same `apply`, and `VocabParallelEmbedding`'s if agreed:
   - the wrapper decodes `W` from `C` into scratch and calls the inner `apply` with a proxy layer holding the decoded
     weight;
   - install releases the plaintext storage;
   - the responder starts last, as a `Service`.
4. **`sampled-proofs` is outermost.** The Commit's committer and taps work at module level, as today.

**Why this order:**
- PoUW's GEMM consumes the decoded `W`, so the served computation really reads `C`.
- Sampled proofs commits the values the model actually produced.
- Uninstall runs in reverse: responder, POUS wrappers (restoring `W`), PoUW wrappers.

**What each protocol commits to when combined:**

| Protocol | Commits to | Link to the others |
|---|---|---|
| sampled proofs | the run root over the required values of `P(profile)`, and the weights root over `W` | the profile digest (which carries the set); `weights_pin` |
| POUS | its commitment to `W` before the salt; the storage root of `C = Enc(W, salt)`; timed answers | `Dec(C) = W` exactly; the same `weights_pin` |
| PoUW | weight roots; each GEMM's A-row roots and tile transcript under the epoch salt | A rows = the quantized input of the same linear Call that sampled proofs commits (placeholder: stated, not checked) |

**The composition record** (`verity-vllm/protocol-composition/v0`, written to `protocols.json`):
- it holds the profile digest, and per protocol its `name`, `scheme` and `commitment()`;
- its digest is SHA-256 of its canonical JSON.

It is a placeholder: each protocol's own verifier checks its own claims, and no one checks the cross-links yet.

**Refused, in code (`refusals`):**
- an unknown protocol, or a scheme that isn't registered on this tree;
- two schemes of one protocol;
- `sampled-proofs` outside the Commit stage: `LLM` doesn't commit, so it points to `verity-vllm row`.

**Adapter refusals, stated here so both adapters agree:**
- compiled execution with `pous` or `pouw` (the wrappers aren't graph-capturable);
- TP > 1 until a TP run is tested;
- `pous` with `pouw` when PoUW keeps a weight-derived copy (int7 or FP10 planes) resident across forwards. That copy
  would let the GEMMs bypass `C` and empty POUS's claim, so PoUW must prepare weight operands per forward from the
  weight it is handed.

**A Commit whose set has more than sampled proofs** runs as a placeholder composition:
- it installs the others, writes `protocols.json`, and records `protocols` in `versions.json`;
- its `verdict.json` carries `protocols.of_record = false`, with reasons;
- it is never a verdict of record.

The reasons:
- **POUS:** the Program is unchanged, because the decode is input provenance and `W` is bit-identical. But the
  committer's weight re-registration and the replay's weight provider read live parameters, which POUS released. POUS's
  adapter must provide `weights()` for them.
- **PoUW:** the Program's GEMM Calls don't describe PoUW's GEMM. The goal is a PoUW linear construction that
  `target.protocols` declares and binds, the way `moe_construction` binds its Definitions, and that passes
  `circuit-check`.

## 4. The `TargetProfile` field

- **`protocols: tuple[str, ...] | None = None`.** `None` means sampled proofs alone. It is omitted from `to_json()`, so
  every existing digest, #101's included, is unchanged.
- **When set,** it holds the full canonical set, `sampled-proofs:vllm-v1` included.
- **Refused:**
  - a set without sampled proofs (a profile is the target of sampled proofs' Program);
  - the default spelled out;
  - duplicates and non-canonical order.
- **The digest changes with the set,** so `check_reuse` refuses, by field, to use a composed run's artifact for the
  default and the reverse.
- The grammar lives in `config.py`, the lowest layer, so `program/` validates without importing the selector.

## 5. Sampled proofs as an option

- **`sampled_proofs.py` is a declaration adapter:**
  - its one scheme is `vllm-v1`: the commitment scheme (`verity_vllm.commit.scheme` over `verity.commitments.vllm_v1`)
    and the replay law, with the strata as RUs at p = 1 (`commit.challenge.stratum_picks` over
    `verity_sampled_proofs.law`);
  - its hooks are the Commit's committer and taps, installed by the Commit exactly as today;
  - `commitment()` reads the run root, Program digest and weights root from the Commit's record.
- **Alone,** `at_commit(profile, …)` returns `None` before importing any adapter, because `profile.protocols is None`.
  The default Commit therefore runs the same code path. The A/B (#101: manifest `90f81868`, run root `7adcef49`) must be
  byte-identical in every PR of the stack.

## 6. Files and owners

- **This scaffold (branch `cursor/vllm-protocol-composition-9924`):** `protocol_options/__init__.py`, `interface.py`,
  `sampled_proofs.py`; `engine/hooks.py` (`Service` and tags); `config.py` (the grammar); `TargetProfile.protocols`;
  `LLM(protocols=…)`; the `at_commit` call at both Commit sites; `tests/protocol_options/`, CPU only.
- **Stacked on it:** `pous.py` from bc-13eada34 (#208) and `pouw.py` from bc-dd22acf8 (#218).

## Open questions for Daniel

1. **The composed Commit.** Placeholder, with its verdict not of record (recommended; it is what makes "all three in one
   run" possible now)? Or refused, as the vLLM coordinator's fail-closed MVP?
2. **PoUW under sampled proofs, of record.** A PoUW linear Definition that the replay re-evaluates? Or delegation, where
   the replay skips PoUW GEMM Calls, PoUW's tile audit covers them, and the A-row to boundary-value link is checked?
3. **POUS with PoUW.** Require per-forward operand preparation from the decoded `W` (costly for Pearl's FP10 planes)? Or
   accept a resident PoUW copy that lies outside POUS's claim?
4. **Challenge order across protocols.** One beacon round after all three commitments are registered, or one per
   protocol?
