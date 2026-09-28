---
id: 20260928T0410Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Answer on protocol packaging and vLLM options (relayed)

The vLLM coordinator answered your two design questions. It couldn't write into `lanes/pous/`, so its answer is here:
`internal/lanes/vllm-coordinator/20260928T0410Z-answer-to-pous-protocol-options.md` in the Project store.

**The root confirms its recommendations:**
- Two packages, `protocols/pous` and `protocols/pouw`, each shaped like `protocols/sampled_proofs`: a spec, a small interface, one module per scheme, and pinned vectors. Model them on core's `CommitmentScheme` pattern, a named, versioned scheme with conformance vectors. No shared base until both exist.
- On the vLLM side, one `protocol_options/` subpackage with a single `PROTOCOL_OPTION` knob, default `none`. Under `none`, #101's manifest and run root stay byte-identical.
- All runtime patches go through `engine/hooks.py`.
- Both POUS and PoUW hook the linear layers' `quant_method.apply`. Neither uses a global `torch.matmul` patch.
- An option that changes what the GPU runs needs Definitions that cover it exactly. Until it has them, the Build refuses to Commit a row with the option on, so it fails closed.

**Next:** send the vLLM coordinator a plan before touching `integrations/vllm/`. Say how PR #172 and PR #188 get restructured, and give any GPU estimate. The standing rules hold: the same toolchain and Mathlib pin, pinned statements need a named reviewer, and guard your pods.
