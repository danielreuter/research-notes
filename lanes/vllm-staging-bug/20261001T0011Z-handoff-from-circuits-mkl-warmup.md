---
id: 20261001T0011Z-handoff-from-circuits-mkl-warmup
campaign: verity
lane: vllm-staging-bug
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: small correctness fix: a single-threaded MKL warm-up at every replay entry point that may call torch transcendentals

compute-accounting found that torch's statically linked MKL VML races on its first call when several intra-op threads hit it at once: one
chunk comes out up to 1,771 ulp wrong (16/200 runs on node 1; 0/200 after a single-threaded warm-up). See
`lanes/coordinator/20261001T0006Z-handoff-from-accounting-449-exp-mkl-race.md`. Its test-side fix is in #449 @ `1b1895bc`
(`integrations/vllm/tests/conftest.py`).

circuits' audit (5:10 PM PDT, main `e3ea0c9a0`):
- `bi-eager` replays evaluate with exact numpy/integer models: no torch transcendentals.
- The only torch `exp` / `rsqrt` on a replay path is `program/kernels/compiled_relations.py` (the SiLU variant
  `torch.exp(-g)`, and `torch.rsqrt` in the norm relations), used by `check/replay/compiled_kernel_check.py` and
  `check/compiled_value_check.py` for `compiled` executions.

**Do:**
1. Add one helper: when torch is importable, call `torch.exp(torch.zeros(1))` once with intra-op threads set to 1, then restore them;
   when it isn't, do nothing.
2. Call it at process start of `commit-replay`, `row stage replay`, and the two compiled checks.
3. Add a test that the helper is a no-op without torch and idempotent with it. Check: does any replay path call torch transcendentals
   from Python threads (`ThreadPoolExecutor` in `row_stages` / `row_tp` / `tp/fold_match`)? If so, warm up before the pool starts.
4. Open a branch `cursor/mkl-warmup-<suffix>`, and send me the head; I'll get it granted and trained.

CPU only, small. Results to `lanes/circuits/`.
