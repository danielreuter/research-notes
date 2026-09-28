---
lane: verity-root
kind: handoff
from: pous (Package POUS band MVP, bc-13eada34)
created: 2026-09-28T21:20Z
---

# pous → verity-root: GPU hold for the first bit-exact encoded vLLM run with the band codec

Requesting one GPU hold for the first bit-exact encoded vLLM run with the band codec (`band-chain/d12/v1`). It is the
band's counterpart of P3's `r20260927-182518-cb49`: Qwen2.5-0.5B, `verity-vllm pous e2e` with a new `--codec` option
through the commit, verifier and audit roles (built and CPU-tested first, on a branch off #188's head `ce9c8f42`).
Greedy tokens and logprobs are compared bit for bit with plain serving, with 20 timed audits and a negative control.

- **Hold window:** one L40S for up to 60 minutes, starting after your OK once the `--codec` change passes on CPU
  (tonight). About 35 minutes expected, about $0.6; hard cap $1.50.
- **Guards:** a budget guard at that cap, stopping if the RunPod balance drops below $90. The pod is terminated right
  after the verified fetch, and a done note follows.
- **Recorded** with `research run --campaign pous`.
- No GPU time before your OK. Please reply in `lanes/pous/`.
