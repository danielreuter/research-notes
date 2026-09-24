---
lane: red-team-ligerito
to: ligerito-pcs-fast
kind: handoff
created: 2026-09-23T18:50Z
severity: SOUNDNESS-LOSS (x2, latent: both bite the moment set B's |S| is used outside the exact shape it was sized for)
---

# SOUNDNESS-LOSS: set B's query counts are valid ONLY for the radix-3 shapes WITHOUT ZK column padding

You own `params.py` / `pcs.py` / `transcript.py` now. `params.py` itself is correct: my independent recomputation
(`backends/direct/ligerito/redteam_soundness.py` @ 9182132 on `lane/red-team-ligerito`) reproduces set B to 3 decimals
(fp8 2^-128.011, bf16 2^-128.026, fp4 2^-128.026). But set B has **0.01–0.03 bits of margin**, and two things that are being
built right now move it off:

**F1 — ZK per-column RS padding (ligerito-zk `zk.py`, `T_PAD = 256` message coefficients on every committed column, every
level) raises every level's rate to `(tall_i + 256)/n_i`.** The design's "ZK adds no soundness term" assumed masks in pad cells;
the padding construction changes the code. Set B's |S| with t_pad = 256:

~~~
fp8  (3*2^28): union 2^-119.34  (L5: rate 3/16 -> 1/4, (5/8)^176)      bf16: 2^-127.20 (L4)      fp4: 2^-124.86 (L4)
~~~

Corrected |S| (same n_i; greedy min-bytes; bytes = params.py model + the `ybar_i` = t_pad ext per level it does not count):

~~~
fp8  [240, 173, 174, 176, 194]  2^-128.10  659.2 KiB (+36.8 vs B)   alt: rates (1,2,2,3,3) [239,172,174,158,163] 651.3 KiB
bf16 [240, 173, 174, 178]       2^-128.20  731.4 KiB (+27.4)        alt: rates (1,2,2,3)   [239,173,173,154]     721.4 KiB
fp4  [240, 173, 174, 183]       2^-128.10  559.6 KiB (+27.9)        alt: rates (1,2,2,3)   [239,173,174,155]     554.5 KiB
~~~

**F2 — set B's |S| on a power-of-two shape.** proto/pcs-fast `Dims`, ligerito-sumcheck's layout (N = 2^30, 16 sub-batches) and
the Rust verifier are pow2-only. Set B's `--rates 1 2 2 2 2 --queries 239 173 174 174 176` at n = 30 gives exact rates 1/2, 1/4:
**union 2^-99.19** (L1 (3/4)^239). pow2 needs `[312, 192, 192, 194, 194]` (fp8, 721.8 KiB; params' own pow2 optimum is
`[312,191,193,194,195]` 722.0 KiB), bf16 `[311,192,193,193]` 836.9 KiB, fp4 `[312,192,192,193]` 623.8 KiB.

**Ask:** never hard-code set B's numbers; derive |S| from `params` for the shape actually committed (pow2 vs radix-3) AND with
t_pad in the message length when ZK is on (add a `t_pad` field to `LigeritoParams` so `rate(i) = (tall_i + t_pad)/n_i` and
`proof_bytes` counts `L * t_pad * 24` B of `ybar`). Assert the union in `pcs.prove`/`verify` against the relation's target.
Details + the rest of the findings: `~/.research/notes/lanes/red-team-ligerito/20260923T1830Z-report-red-team-ligerito.md`.
