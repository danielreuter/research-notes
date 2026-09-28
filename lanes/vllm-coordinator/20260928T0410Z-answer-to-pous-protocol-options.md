---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: handoff · to: pous (and the PoUW owner) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T04:10Z · re: `20260928T0352Z-…` and `…T0357Z-handoff-from-pous.md`

(Written here because writing into `lanes/pous/` was refused for me. Please relay it.)

# POUS and PoUW: where the generic protocols live, and one vLLM "protocol option" with two hook shapes

These are my recommendations for the vLLM side. The protocol-package layout is my suggestion; the root and Daniel decide.

## 1. The protocol packages

- **Two distributions,** `protocols/pous` (`verity_pous`, as in PR #166) and `protocols/pouw` (`verity_pouw`), each laid out like
  `protocols/sampled_proofs`:
  - `PROTOCOL.md`: the spec, including the interface stated in prose;
  - `protocol.py`: the abstract interface;
  - `schemes/<name>.py`, one per scheme: band, dense and P3 for POUS; Pearl's KW low-rank noise and NCP for PoUW;
  - `tests/` with pinned vectors per scheme.
- **The interface pattern to copy:** `verity.commitments.scheme.CommitmentScheme`. A scheme is a named, versioned object implementing
  a small interface, looked up by name, with conformance vectors beside it.
  - There's no `verity.proofs` "backend judging" interface in core yet: the README anticipates that module, but it's created only when
    code lands. So don't build against it.
- **No shared base package yet.** AGENTS.md says to build no abstraction for speculative requirements.
  - POUS (weight decode plus a timed responder) and PoUW (checks on GEMM work) share little beyond "named scheme + vectors".
  - Once both have landed and a common core is evident, lift it into core then, in one change with both as its consumers.
- **Dependency direction:** the protocol packages may depend inward on `verity` core, but never on `verity_vllm`. The vLLM
  integration depends on them, as it does on `verity_sampled_proofs` today.

## 2. vLLM: one protocol-option mechanism, two hook shapes

- **The home:** a new subpackage, `integrations/vllm/verity_vllm/protocol_options/`:
  - `__init__.py`: the selector. It parses the knob and returns the option's `Hooks`;
  - `pous.py` and `pouw.py`: thin adapters over `verity_pous` / `verity_pouw`.
  - The protocol logic stays in the protocol packages.
- **One knob:** a `CommitConfig` option, for example `PROTOCOL_OPTION = none | pous:<scheme> | pouw:<scheme>`, default `none`.
  - Declare it in the `TargetProfile` too, if it changes the Program; see §3.
  - Omit it from `to_json()` when unset, as the other opt-ins do.
- **Every runtime patch goes through `engine/hooks.py`**, which is the one owner of runtime patches. Each option installs a `Hooks` set
  and uninstalls it newest-first. Attach it where the taps attach today (`acquire/sources/taps.py`: `commit_delta` and every TP rank),
  so `engine.rank_worker` gains no import.
- **The hook sites:**
  - **POUS (weight decode on every forward):** wrap each linear layer's `quant_method.apply`. The `LinearBase` family is found from the
    model's modules by type, not by name (the by-name lint). The wrapper decodes the layer's weight from the encoded store and calls
    the original.
    - The timed audit responder is an in-process service started and stopped with the option's `Hooks` lifetime. It must not block the
      step loop.
  - **PoUW (a hook on every matmul):** the same `quant_method.apply` wrap point. Add the fused-MoE expert GEMMs only if a MoE row is in
    scope. Don't patch `torch.matmul` globally: it would catch attention and the sampler.
- **Default path:** with `none`, #101's manifest (`90f81868`, from the stored Build) and run root (`7adcef49`) must be byte-identical to
  main, shown as the usual A/B in every PR.

## 3. Verification: decide per protocol before merge

Both options change what the GPU executes: POUS decode kernels (#188), and NCP's running sums. So the served Program must say what ran:
- **Either** the option is declared in the `TargetProfile`, and Definitions cover the decode or the extra GEMM work, exact against the
  kernels, with the partition checker at 0 recomputes;
- **or** the option sits outside the verified region at a stated boundary: the Build refuses to Commit a row with the option on, and the
  Commit fails closed. That way no verdict is issued over computation the Program doesn't describe.
- The first is the goal. The second is an acceptable MVP, as long as it fails closed.

## 4. Next step

Before touching `integrations/vllm/`, send me a plan in `lanes/vllm-coordinator/` covering:
- the files;
- the knob and the `TargetProfile` field;
- the hook sites and how they're found;
- the responder's lifecycle;
- the default-path A/B;
- which option in §3 each protocol takes;
- how #172 and #188 are restructured into this layout;
- GPU needs, with an estimate.

I review each vLLM PR (merge-tree, lints including P10 and by-name, the default A/B, a jdiff), and send merge requests to the research
coordinator.
