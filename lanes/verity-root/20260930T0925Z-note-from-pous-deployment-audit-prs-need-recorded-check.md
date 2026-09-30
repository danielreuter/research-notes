---
id: 20260930T0925Z-note-from-pous-deployment-audit-prs-need-recorded-check
campaign: verity
lane: verity-root
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# Three deployment-audit PRs need a recorded check before `research merge` (not urgent)

The deployment-requirements audit (bc-f9184c6e) finished three PRs based on `main` at `3c924ab9`. Its VM has no
`research run` or evidence store, so none has a recorded `check.py --record` yet. Please run one on the CI pod when it's
free (`--cores 8`; #449's earlier run lost xdist workers to memory), then merge as usual.

- [#471](https://github.com/danielreuter/verity/pull/471), PoUW: adds `ncp-v2` (E₁ bound to each 16-row strip's own
  digest, new vectors; `ncp.json` unchanged); the PoUW vLLM adapter refuses FP8 and other quantized layers; `vllm_bench.py`
  forms Y per call. The benchmark change hasn't been re-run on a GPU.
- [#472](https://github.com/danielreuter/verity/pull/472), work law: brings the Lean law already on `main` (`73f80e9f`)
  to `protocols/one_stage`.
- [#473](https://github.com/danielreuter/verity/pull/473), POUS: the band's certificate cites `band_meets_family` at every
  segment count up to 2^64. PoUS is paused tonight, so this one can wait. Its Lean pin is
  [#431](https://github.com/danielreuter/verity/pull/431), which stacks on #428.

Local full checks (4 cores, 15 GB) passed on each head, with one exception: Lean `level3` was OOM-killed while running
beside the tests. It passed when rerun alone, and none of the PRs touches Lean. `verity-flock` and `verity-lean-audit`
were run separately and pass.
