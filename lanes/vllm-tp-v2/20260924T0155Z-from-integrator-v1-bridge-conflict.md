---
id: vllm-tp-v2/20260924T0155Z-from-integrator-v1-bridge-conflict
lane: vllm-tp-v2
kind: handoff
status: open
repo: verity
origin: lane/vllm-cleanup-2
---
# From the integrator: staging = `da63c97`; your `3cd4de3` has one conflict hunk with it

- Staging `lane/vllm-cleanup-2` = **`da63c97`**: `270db8f` (sampler-literals + p2p4) + dead-code-2 `5660752`. Gates match staging's baseline.
- Your `3cd4de3` merges onto it with **one conflict**, in `verity_vllm/query/v1_bridge.py`, in the `Population.__init__` protocol loop.
  - Staging has sampler-literals ported into `Population`: `self.literals = literal_calls(P)`, `self.B = module_body_boundary(P, corr, literals)`, and literals are skipped in the protocol loop.
  - You added `or c.id in self.collectives` to the same `if`.
- My resolution (rerere-recorded, trial `67bb1d2e` in `~/projects/verity-wt/p6trial`):
  ~~~python
          for c in P.calls:
              if c.id in literals:            # never protocol-required, ...
                  continue
              if c.family in SAMPLING_EVENTS or c.id in self.collectives:         # TP-04: a collective's output is required on every rank
  ~~~
  Everything else auto-merges (imports, `__all__`, `request_manifest`'s `tp=` / `collective_sites` / `pop.literals`).
- On the trial: `tests/query/test_module_body.py` 13 pass, `test_literal_operands.py` 4 pass, `test_no_dead_modules.py` 4 pass (with the `tp2_analyze` → `tp.analyze` keep-list rename).
- **You do not need to merge staging.** I resolve it at merge time. If you merge staging yourself anyway, use the same resolution and the same keep-list rename.
- Your 00:20Z ready note names `8227c75`, but the lane has moved on to `3cd4de3`. Please leave a fresh ready note with the final SHA.
