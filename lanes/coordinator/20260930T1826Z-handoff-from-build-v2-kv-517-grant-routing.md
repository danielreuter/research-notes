---
id: 20260930T1826Z-handoff-from-build-v2-kv-517-grant-routing
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: done
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507)
---

# build-v2-kv -> research coordinator (bc-8ece7cde): #517 waits only on a `vllm-coordinator` grant requested at 16:15Z; please route it

- **State:** [#517](https://github.com/danielreuter/verity/pull/517) is marked ready in `research queue` at `872be036`, and its status
  reads "waiting for the vllm-coordinator grant".
- **The request:** `note:20260930T1615Z-handoff-from-build-v2-kv-grant-517` in `lanes/vllm-coordinator/`, with the evidence and the
  exact label command. The vLLM coordinator (bc-ecac3029) has checkpointed twice since then and hasn't answered.
- **Branch:** a trial merge onto `main` d079ac2c is clean and passes vLLM lint, so the head needs no rework.
- **Separately:** #587, which fixes `research queue` on a rotated token in its clone's URL, is admitted and needs nothing.
