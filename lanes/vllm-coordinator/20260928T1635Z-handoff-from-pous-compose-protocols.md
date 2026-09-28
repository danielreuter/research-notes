---
id: 20260928T1635Z-handoff-from-pous-compose-protocols
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# Daniel wants PoUW, POUS and sampled proofs toggleable and composable in vLLM

This supersedes the single-choice knob in `20260928T1630Z-handoff-from-pous-protocol-options-go.md`.

Daniel (16:33Z) wants the vLLM integration to toggle PoUW, POUS and sampled proofs independently and compose all three in one run. Placeholder security is fine for now. He expects this to need shared infrastructure, and asked that we coordinate with you on it.

A POUS-side worker, "Build composable vLLM protocol options", will post a design of at most 2 pages here, under `lanes/vllm-coordinator/`, before building. It covers:
- the config shape: a set of enabled protocols with schemes, off by default;
- a common hooks interface under `integrations/vllm/verity_vllm/protocol_options/`;
- hook ordering and what each protocol commits to when they're combined;
- the `TargetProfile` field;
- sampled proofs as one option, unchanged in behaviour when it's the only one enabled.

The thin adapters `pous.py` and `pouw.py` stack on top of it.

What we need from you:
1. Constraints from the sampled-proofs integration and the epoch work in flight, such as files not to touch, profile or digest rules and hook points.
2. A review of the design when it lands.

Please reply in `lanes/pous/`, or here if writing there is refused. The worker will build the scaffold if there's no reply within about an hour, and adjust to your review after.
