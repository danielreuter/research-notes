# RQ7 -- cheapest secure KV design: what the systems tricks recover (measured)

Agent W1, phase 2. Worktree `porep2-w1`, branch `p2/w1`, pod c (H100 SXM 80 GB, shared with P1, GPU under
`flock`). Model Qwen2.5-7B-Instruct, weights plaintext throughout (RQ7 isolates the KV side); KV encoded
with the recommended point (l=3, d=4, r=3) and the phase-1 point (2,6,4) as a secondary column; the plaintext
KV baseline is measured in every run. Code: `porep/model.py` (KVOpts, PagedKV, decode_attention),
`porep/bench/kv_tricks.py` (items 1, 2, 4, 5, 6 + correctness), `porep/bench/agentic.py` (item 7, Mooncake
session). CSVs: `results/phase2/rq7/*.csv` with `.cmd` sidecars (pulled to `results/pod-c/phase2/rq7/`).

## Final config: the shipping point (4,6,4) mixer 1 dru with K2's final kernels (2026-09-03 ~14:00 PDT)

Merged `p2/k2` (3ac634e, contains K1's final ca30162) into `p2/w1`: clean merge (K2's `model.py` change is
the `fusedmm` branch of `PoRepLinear`, orthogonal to the KV paths). New in the kernels: out-of-place
ping-pong decode, bounded CTAs by default (`POREP_BPC=2`), 128-bit `replica_key` (`MixerArgs.rkey`), the
fused decode->WGMMA weight path (`PoRepLinear(mode="fusedmm")`, `porep_fused.cu`). Tests pass on pod c
(`tests/test_porep.py` incl. fused GEMV at L4 dru, `tests/test_fused.py`). Security update (S2): mixer 1 at
d=6 needs **r=4** (3 DR has a related-parent distinguisher), so the shipping point is **(l=4, d=6, r=4) drU,
64 KB pages, chunk 32, n=2048** (P1: 64 KB is also required by the challenge deadline, 32 KB is too short).
Run: `results/phase2/rq7/run_final.sh` -> `session_final.csv`, `session_final_raw.csv` (+ `.cmd`),
`kernels.csv` (appended), `final.log`. All tricks on (`--seal side --window 1 --cascade`), plaintext baseline
in-run, B in {1, 8}, tau in {1, 3}.

### KV decode throughput, K2 kernels (1 GB buffer; and the effective in-step rate = decoded bytes / (encoded step - plaintext step))

~~~
config (64 KB, mixer 1)   raw decode GB/s  x memcpy  encode GB/s  page encode ms | in-step eff. GB/s: B=8 30K / 60K / 90K   B=1 30K / 118K
(4,6,4) dru  [shipping]        438          3.44       5.9          3.70        |     332 / 405 / 423                 228 / 346
(4,6,3) dru  [last run]        470          3.22       6.8          3.14        |     355 / 432 / 450                 241 / 371
(3,4,3) distinct [retracted]   649          2.33       9.4          2.27        |      --
~~~

K2's kernel is +8 % over K1's at (4,6,3) (435 -> 470 GB/s) despite the bounded CTAs; the S2-required fourth
round costs -7 % (470 -> 438). The in-step effective rate at B=8, 90K (423 GB/s) is within 4 % of the raw
kernel number: the decode-on-read overhead is the decoder itself, the scratch write + re-read by attention
is nearly free at this batch. At B=1 the per-step decode is 1.7-6.8 GB in one launch and reaches only
228-346 GB/s (occupancy / tail-limited), which is why B=1 sees a smaller absolute but not smaller relative gap.

### Session, all tricks, plaintext baseline in-run (x = vs plaintext at the same B and tau)

~~~
config                                B=8 tau=1: session         TPOT t1       TPOT t30     | B=8 tau=3: session        TPOT t1       TPOT t30
(4,6,4) dru  KV only  [shipping]      2478 s (2.71x)   29.9 ms (2.43x)  100.1 ms (4.74x)   | 1151 s (1.88x)  10.9 (2.23x)  34.3 (4.37x)
(4,6,3) dru  KV only  [last run's pt] 2379 s (2.60x)   28.6 ms (2.33x)   95.3 ms (4.52x)   | 1119 s (1.83x)  10.4 (2.13x)  32.9 (4.20x)
(4,6,4) dru  KV + weights fusedmm     3350 s (3.67x)   61.8 ms (5.03x)  132.9 ms (6.30x)   |  --
plaintext (same tricks)                914 s            12.3 ms           21.1 ms           |  613 s           4.9           7.8
B=1: (4,6,4) tau=1 761 s (2.14x), TPOT t1/t30 17.8/31.2 ms (1.78x/2.66x); (4,6,3) 2.05x; both 1631 s (4.58x), TPOT 49.8/63.2 (4.98x/5.39x);
     tau=3: (4,6,4) 1.84x, (4,6,3) 1.78x; plaintext B=1 tau=1 356 s, TPOT 10.0/11.7 ms
~~~

The (4,6,3) rows reproduce the gate-+6h run within 1 % (2399 -> 2379 s: K2's faster kernel). The extra
round for soundness costs +4 % session time (2.60x -> 2.71x). "Both encoded at the sound point" -- weights in
K2's `fusedmm` tile-major blocks at (4,6,4) dru (`POREP_FUSED_BPC=auto4`), KV as above -- is **3.67x at B=8
tau=1** (the phase-1 harness's 3.8x was at the retracted (3,4,3) point with the phase-1 kernels and no cascade; the
sound point costs about the same because the weights side moved to the fused kernel and the KV side gained
cascade, while losing a layer and a round to security). The weights add a flat ~32 ms per step at every B and context (61.5 - 29.6 ms at B=8 30K; ~13 GB of
encoded linear weights decoded inside the fused GEMMs, ~400 GB/s effective), the KV side adds 17 -> 79 ms from 30K to
90K at B=8; at B=1 the weights dominate (both 4.58x vs KV-only 2.14x).

**Pass criterion `<= 1.8x` at B=8, tau=1: not met at the shipping point: 2.71x** (KV only), 3.67x with the
weights encoded too. With tau=3 speculation (upper bound, all drafts accepted) the KV-only session is 1.88x
vs a plaintext server that also speculates, 1.26x vs one that does not (1151 s vs 914 s). The gap is the
decoder: 438 GB/s of decode-on-read vs plaintext attention reading the same KV at ~1.9 TB/s effective, x4.7 on
the turn-30 step; the systems tricks (cascade -17 % session, side sealing -3 %, window 0 %) are all in.

## With K1's mixer + the security-corrected point (2026-09-03 ~13:00 PDT, gate +6h)

Merged `p2/k1` (466c80e) into `p2/w1` (clean; K1's only `model.py` touch was `gemv_fits`). K1 adds
`PoRepParams.mixer` (1 = injection-ARX + Davies-Meyer feed-forward, the fast winner), `parent_sampler`
{"bucket","distinct","dru"}, and v3 decode kernels (cp.async double-buffered prefetch). Tests pass on pod c
(`tests/test_porep.py`: reference roundtrip + KAT, all (mixer, sampler) bit-exact, fused GEMV M=1..8). The
kernel dispatch templates (W, D, MIXER) with D in {4,5,6,8} for mixers 1/2 and `layers` is a runtime loop, so
**l=4 and l=5 are instantiated** -- I ran both dru d=6 configs (no need for K1 to add them). Token-identity
re-checked at mixer 1 + distinct, 64 KB: plaintext text, sync/side seal, window, encoded generation all
identical to plaintext; cascade equal up to the same bf16 tie as before (attention error 1.5e-4..9.5e-4 vs
fp32). All 64 KB / chunk 32 / n=2048. CSVs: `results/phase2/rq7/session_mixer1*.csv`, `kernels.csv`.

### KV decode throughput per config (1 GB buffer, GB/s; higher = cheaper decode-on-read)

~~~
config                                   decode GB/s   x memcpy   encode GB/s   one-page encode ms
phase-1 32 KB (3,4,3) mixer 0             579          2.61        10.8          1.56
64 KB (3,4,3) mixer 0 (last round's rec.) 514          2.95         7.2          3.00
64 KB (3,4,3) mixer 1 + distinct          630          2.41         9.6          2.23    <- +22 % vs 64KB m0, faster than 32KB m0
64 KB (2,6,3) mixer 1 + distinct          776          1.95        12.7          1.72    <- fastest; nearly memcpy-bound
64 KB (3,4,3) mixer 2 + distinct          290          5.22         3.2          6.78    <- mmaarx: slow here, skip for KV
64 KB (4,6,3) mixer 1 + dru  (corrected)  435          3.48         6.6          3.24
64 KB (5,6,3) mixer 1 + dru               375          4.04         5.4          4.04
~~~

Mixer 1 gives the promised ~1.5x: at equal (l, d) the (3,4,3) decode goes 514 -> 630 GB/s (1.23x) and
against the phase-1 32 KB block it is faster despite the 2x larger page; (2,6,3) reaches 776 GB/s (1.95x
memcpy, near the roofline). The security-corrected point costs the extra layer: 435 GB/s at l=4 (0.85x the
old l=3 m0), 375 at l=5.

### Session at B=8, all tricks (side seal + W=1 + cascade), plaintext baseline in-run (x = vs plaintext same B, tau)

~~~
KV config (mixer 1, 64 KB)          B=8 tau=1  session   TPOT t1     TPOT t30     |  B=8 tau=3  session   TPOT t1    TPOT t30
(2,6,3) distinct   [l=3, insecure]   1801 s (1.97x)  22.5 (1.84x)  66.2 (3.14x)  |   916 s (1.50x)  8.3 (1.69x)  23.0 (2.93x)
(3,4,3) distinct   [l=3, insecure]   1988 s (2.18x)  24.4 (1.99x)  75.6 (3.59x)  |   982 s (1.60x)  9.1 (1.85x)  26.2 (3.34x)
(4,6,3) dru        [CORRECTED pt]    2399 s (2.63x)  28.6 (2.33x)  96.7 (4.59x)  |  1130 s (1.84x) 10.4 (2.11x)  33.5 (4.28x)
(5,6,3) dru        [margin]          2705 s (2.96x)  31.3 (2.55x) 112.1 (5.32x)  |  1234 s (2.01x) 11.4 (2.33x)  38.6 (4.92x)
plaintext (same tricks)               912 s          12.3          21.1          |   613 s          4.9           7.8
B=1: (2,6,3) 1.63x, (3,4,3) 1.75x, (4,6,3) dru 2.00x, (5,6,3) 2.19x (tau=1); (4,6,3) dru tau=3 1.75x
~~~

Mixer 1 at the old (3,4,3) point takes the B=8 tau=1 session from 2.42x (mixer 0, last round) to **2.18x**,
and turn-1 TPOT to 1.99x (~2x at short context). But **the security reconciliation (graphs2.md, S1/S3
bidirectional game) retracts l=3: with the Davies-Meyer feed-forward the first point that holds `eps <= 0.01`
at W=2n is l=4 with a d=6-class graph; drU d=6 at l=4 is the default, l=5 the margin.** At that corrected
point the session is **2.63x at tau=1** (1.84x at tau=3), because the fourth layer adds ~33 % decode traffic
(435 vs the ~630 GB/s an l=3 mixer-1 block would give). So the mixer buys back ~10 % but the +1 layer the
security fix requires gives it back: net, the secure design is *slower* than last round's insecure-l=3 figure.

**Pass criterion `<= 1.8x` at B=8, tau=1: still not met** -- 2.63x at the corrected (4,6,3) point, 2.18x even
at the retracted (3,4,3). It is met only with speculation and only away from the corrected point: (2,6,3)/
(3,4,3) reach 1.50x/1.60x at tau=3, and the corrected (4,6,3) reaches **1.84x at tau=3** (just over) vs a
plaintext server that also speculates. Against a non-speculating plaintext server, (4,6,3) tau=3 is 1.24x
(1130 s vs 912 s). The gap is still the decoder: 435 GB/s at l=4 vs plaintext attention at ~1.9 TB/s, i.e.
~4.4x per-token at 90K that no systems trick touches. Closing it to <= 1.8x at tau=1 and l=4 needs either a
fused decode-into-attention kernel (removes the scratch write+re-read, <= ~30 % of the overhead) or a lower
secure layer count than the bidirectional game currently allows.

---

## Summary / recommendations (2026-09-03 12:50 PDT; "Final config" added 14:00 PDT)

**Final config (the shipping point, measured with K2's final kernels; section above):** KV pages of 64 KB
(chunk 32, n=2048, P=64 tokens per page), encoded with **mixer 1, drU parents, l=4, d=6, r=4** (S2: r=4
is required for mixer 1 at d=6; l=4 from the S1/S3 bidirectional game), 128-bit replica key, bounded CTAs
(`POREP_BPC=2`), side-stream sealing, no plaintext window beyond the partial + in-flight page, shared-prefix
cascade for B >= 2. Raw decode 438 GB/s (3.4x memcpy), 423 GB/s effective in the B=8 90K step; one-page
encode 3.7 ms (hidden on the side stream). **Mooncake session at B=8: 2.71x plaintext at tau=1** (2478 s vs
914 s; TPOT 2.43x at turn 1, 4.74x at turn 30), **1.88x at tau=3** vs a speculating plaintext server (1.26x
vs a non-speculating one); B=1: 2.14x / 1.84x. **Weights + KV both encoded at the sound point** (weights in
K2's `fusedmm`, same params): **3.67x at B=8 tau=1** (3350 s; TPOT 5.03x / 6.30x), 4.58x at B=1. The
`<= 1.8x` criterion is not met at tau=1 (2.71x); it is met only against a non-speculating baseline with tau=3
speculation, and the remaining gap is the decoder (438 GB/s vs the ~1.9 TB/s plaintext attention reads the
KV at), not the systems layer. Relative to the phase-1 design at the same point the tricks recover ~20 % of
session time (cascade -17 %, side sealing -3 %, window 0 %); tau=3 halves it again (2478 -> 1151 s) but the
plaintext baseline speculates too (914 -> 613 s). Security-neutral:
sealing (<= 1 page in flight), cascade (one physical prefix copy), speculation; the plaintext window is data
the adversary holds for free, so W=0 with <= 127 plaintext tokens per (sequence, layer), 0.1-0.4 % of context.

All numbers below: Qwen2.5-7B-Instruct on one H100, plaintext weights, KV encoded at (l=3, d=4, r=3) unless
stated (the point later retracted by graphs2.md; the trick-by-trick savings carry over to the final config),
plaintext KV baseline from the same run; B=8 unless stated. Details and (2,6,4) columns in the dated entries.

**Cheapest secure KV design (recommended):**
* Block = one KV page of **64 KB, chunk 32, n = 2048** (the only size that meets the n >= 2048 constraint of
  graphs.md at the fast chunk width); P = 64 tokens of one layer's K or V for this model. Cost vs the
  phase-1 32 KB / n=1024 block: +2 % on the decode step, one-page encode latency 3.6 ms (hidden, see next),
  re-key 6.3 GB/s. 128 KB pages: +19 % decode, no security need. chunk 64: decodes at 60 % speed, out.
* **Seal on a side stream** when a page fills (staging copy + event, join at the end of the step): the fill
  step costs +8..20 ms instead of +102 ms; TPOT -2..6 % at B=8, -10..15 % at B=1, max step latency 146 -> 56
  ms. Security-neutral: at most one page per (sequence, layer) is in flight for one step.
* **Plaintext working window W = 0**: W = 1-4 pages saves nothing measurable (< 1 %, expected ~3 %); even
  W = 64 pages (7 % of a 30K context in plaintext) recovers only 1-3 %. The plaintext exposure is therefore
  just the partial page (<= P-1 tokens) plus the in-flight page for one step: <= 127 tokens per sequence per
  layer with 64 KB pages, 0.1-0.4 % of a 30K-118K context -- data the adversary holds for free, the
  challenge protocol simply excludes the two newest pages.
* **Shared-prefix cascade for B >= 2**: decode + attend the shared prefix pages once per step (LSE merge).
  -40 % on the encoded step at 30K, -22 % at 60K, -17 % at 90K (B=8); -17 % session time, -40 % turn-1 TPOT.
  Security-neutral (one physical copy of the prefix, as in any paged server with prefix caching). Disable
  at B=1 (+12 % from the extra kernels). Not bitwise identical to plaintext generation (a two-part softmax
  merged in fp32): attention output within 1.2-2x of the single pass's own bf16 rounding error vs an fp32
  reference; the one observed token flip is an exact bf16 tie (top-2 logits 32.75/32.50 -> 32.50/32.50).
* **Speculative decoding** divides the absolute encoded overhead per token by tau as predicted (84.5 ->
  28.2 ms per token at tau=3, B=8, 90K) -- but the plaintext decode step is equally KV-read-bound, so the
  slowdown vs a plaintext server that also speculates only moves from 4.9x to 4.4x (B=8, 90K). It is the
  one trick that changes the session-level ratio materially only when the comparison baseline does not use it.
* **Pool re-key** (portable key -> slot key): encode-bound, 9.4 GB/s at 32 KB / 6.3 GB/s at 64 KB pages =
  0.61 / 0.91 s per 100K-token context (5.7 GB), 1.8 / 3.6 ms per page. Worst-case TTFT impact at 94 % hit
  with every hit page coming from the pool: +0.17 s (turn 1) .. +0.68 s (turn 30) per sequence, +23-35 % of
  the B=8 plaintext TTFT if not overlapped, 0 % if pipelined with the prefill. Run it on a side stream in
  chunks of <= 256 blocks: the concurrent decode step then slows by +15 % (32 KB) / +47 % (64 KB) at 4.5
  GB/s re-key, instead of +25 % / +190 % with one big launch.

**Session (Mooncake, 30 turns, B=8, (3,4,3)):** phase-1 design 3.00x plaintext (2780 s vs 926 s; the
phase-1 figure of 2.84x ignored the synchronous seal, +3.2 ms per token); side sealing 2.92x; + cascade
**2.42x** (2238 s), turn-1 TPOT 1.96x, turn-30 TPOT 4.09x. (2,6,4): 2.83x -> 2.31x. tau=3 column: 1.73x vs a
speculating plaintext server (upper bound), 1.15x vs a non-speculating one. At B=1: 2.11x -> 1.86x.

**Pass criterion (<= 1.8x at B=8): not met with systems tricks alone (2.42x); met only in the speculative
column (1.73x, upper bound).** What is left is the decoder itself: 491 GB/s decode (3.1x the memcpy time,
instruction-bound) against plaintext attention streaming the KV at ~1.9 TB/s -- 3.7-4.1x at 90-118K
contexts whatever the systems layer does. The two remaining levers are outside RQ7: a cheaper mixer (K1;
rerun item 7 when merged) and fusing the decode into the attention kernel (removes the scratch write +
re-read: at most 32 % of the overhead). With both, and the tricks above, <= 1.8x at tau=1 is plausible;
without a cheaper decoder it is not.

**Security accounting of the tricks:** neutral -- side-stream sealing (same blocks, same encoding, one page
in flight), cascade (one physical prefix copy), speculative decoding (KV decoded once per verify step), pool
re-key (slot keys are what prevents the pool copy from being a challenge shortcut). Changes the adversary's
options -- the plaintext window (W pages + partial page + in-flight page per sequence are unencoded: the
adversary can hold them at zero cost; fraction <= (W+2) x P / ctx = 0.1-0.4 % at W=0, 64 KB pages), and the
page size (n = 1024 blocks are below the graphs.md recommendation -> 64 KB / n = 2048).

**Security-corrected point (graphs2.md, gate +6h):** the bidirectional pebbling game (S1/S3) retracts the
l=3 recommendation this section used; the sound point is **l=4, drU d=6** (l=5 for margin), Davies-Meyer
feed-forward mandatory. Numbers for it are in the "With K1's mixer" section above; the (3,4,3)/(2,6,4) numbers
below are the achievable-cost lower bound (they are the cheapest secure design only if l=3 were sound, which
it is not). Net effect of gate +6h: K1's mixer 1 helps ~10 % but the +1 layer the security fix requires
costs ~20 %, so the secure session is 2.63x (tau=1) / 1.84x (tau=3) at B=8, not below 1.8x.

**Deliverables:** code `porep/model.py` (KVOpts, PagedKV, decode_attention), `porep/bench/kv_tricks.py`,
`porep/bench/agentic.py` (kv options, tau, fill-step amortization), `porep/bench/kv_report.py` (tables);
CSVs + .cmd + logs in `results/phase2/rq7/` (copy of `results/pod-c/phase2/rq7/`); token-identity and numerics
checks in `correctness.csv`.

## 2026-09-03 08:10 PDT -- reading, design decisions

Sources read: CONTEXT2, PLAN2 (RQ7), REPORT 4/5/6.9/7, kv_systems.md, graphs.md, costmodel.md, the paged
KV code and the two benches, phase-1 CSVs (`kv_e2e.csv`, `agentic_session.csv`: KV-encoded (3,4,3) session
2.9x at B=8, "both" 3.8x).

How phase 1 works (porep/model.py before this branch): `PagedKV` holds K and V as `[B, n_pages, P, n_kv, hd]`
bf16, one PoRep block = one (sequence, page) = P tokens x n_kv x hd x 2 B = 32 KB at chunk 32 / n=1024 (P = 32
tokens for Qwen2.5-7B: 4 KV heads x 128). `append` writes plaintext and, when a page fills, encodes it **in
place, synchronously on the main stream**; every read (`plaintext_view`) decodes all sealed pages of all B
sequences into a transient scratch (`[B, T, n_kv, hd]`), then SDPA with the KV heads expanded to the 28 query
heads. Two decodes per layer per step (K and V), i.e. the whole encoded KV is decoded once per token.

Design implemented on this branch (all behind `KVOpts`, default = phase-1 behaviour):

1. **Side-stream sealing** (`seal="side"`): in a decode step where a page fills, the page is copied to a
   plaintext staging buffer on the main stream, an event orders a second CUDA stream after that copy, and the
   in-place encode runs on the side stream; the same step's attention reads the page from the staging copy;
   `Model.forward` joins the side stream at the end of the step (`end_step`) and flips the page to "sealed".
   Prefill bursts (L > 1 or more than one page to seal) keep the synchronous path. Everything is
   graph-capturable (fork/join of streams is legal inside capture).
2. **Plaintext working window** (`window=W` pages): pages are sealed only when they age out of the window,
   i.e. `sealed = full_pages - W`; the window pages + the partial page are read directly from HBM plaintext
   (a copy into the same scratch, so the attention path is unchanged).
3. **Shared-prefix cascade** (`shared=S tokens, cascade=True`): the first `S // P` pages are decoded ONCE per
   step (from sequence 0) into a shared scratch; all `B x g x L` query rows attend them in one Flash call
   (`_scaled_dot_product_flash_attention` with the batch folded into the query-length axis, which returns the
   fp32 log-sum-exp); the per-sequence remainder is attended separately; the partial softmax states are merged
   in fp32 (Hydragen / FlashInfer cascade). Shared pages are attended exactly once per KV head per step
   instead of B times, and decoded once instead of B times.
4. **Speculative-decoding emulation** (`tau` query tokens per step): `Model.forward(ids [B, tau],
   all_positions=True)`; `decode_attention` folds the `tau x g` rows into the query axis, attends the keys
   older than the tau new ones with Flash and the causal tail (tau x tau) in a tiny fp32 kernel, merged by
   log-sum-exp. Upper bound on speculative decoding (all tau tokens accepted, no drafter cost).
5. Page size: `PoRepParams(chunk_bytes, n_chunks)` already sets the block; P = block / (n_kv x hd x 2) tokens.
6. Re-key: decode + encode of the same buffer, measured with the existing kernels (encode is sequential per
   block; throughput comes from many blocks in flight).

Token-identity criterion for every attention-path change: greedy generation on the phase-1 prompt (80 tokens)
must reproduce the phase-1 plaintext text; for the cascade path B=4 identical long prompts (1993 tokens, 62
shared pages) compared with plaintext generation.

Pod hygiene: pod c is shared with P1 and both agents' `pod.sh sync` use `rsync --delete`; the first sync from
this worktree deleted P1's files (excludes added), and P1's next sync reverted my edited files in the shared
directory (`kv_tricks.py` gone, `model.py` back to phase 1). Fix: `POD_DIR=/workspace/porep-w1` (new pod.sh
override) -- each agent syncs to its own checkout; the extension is built into `POREP_BUILD_DIR=/tmp/porep_build_w1`.

## 2026-09-03 08:55 PDT -- correctness (pod c, `--phase correctness`, results/phase2/rq7/correctness.csv)

~~~
plaintext (new attention path): identical to the phase-1 plaintext text: True (80 tokens)
tau=2,3,4 batched verify path == sequential greedy: True / True / True
plaintext: KV rows of identical prompts bit-identical: True (62 shared pages)
plaintext + cascade generation identical to plaintext: False   (see numerics below)
s32_n1024_L3_d4_r3 base:              identical: True  sealed=3 plaintext_tokens=25 encode_calls=6
s32_n1024_L3_d4_r3 seal=side:         identical: True  sealed=3 plaintext_tokens=25 encode_calls=6
s32_n1024_L3_d4_r3 win=2:             identical: True  sealed=1 plaintext_tokens=89 encode_calls=2
s32_n1024_L3_d4_r3 seal=side+win=1:   identical: True  sealed=2 plaintext_tokens=57 encode_calls=4
s32_n1024_L2_d6_r4 seal=side:         identical: True
s32_n1024_L3_d4_r3 casc=1984 B=4:                identical: False (text differs at a later token, coherent)
s32_n1024_L3_d4_r3 seal=side+win=1+casc=1984 B=4: identical: True
s32_n1024_L2_d6_r4 casc=1984 B=4:                identical: False
encoded+cascade tau=3 batched verify == sequential: True
~~~

Everything that keeps a single softmax over all keys is token-identical to plaintext (sync/side sealing,
windows, encoded pages, the tau path). The cascade path is not bit-identical by construction: it computes the
softmax in two partial passes (shared prefix, private remainder) and merges them in fp32, whereas the
baseline is one Flash pass with its own internal block order and a single bf16 rounding of the output; the
two encoded cascade variants also differ from each other because their split point differs (with window=1
the last shared page is still plaintext and is attended as private). This is the same property as
FlashInfer's cascade / Hydragen: numerically equivalent, not bitwise identical. The `numerics` phase
quantifies it against an fp32 reference (below).

## 2026-09-03 09:40 PDT -- cascade numerics (`--phase numerics`, rows appended to correctness.csv)

Random KV (B=4, 4 KV heads x 7 query heads, hd 128), identical shared prefix across the batch, one decode
query; max |error| of the bf16 attention output against an fp32 softmax reference:

~~~
                       T   shared     single pass (base)   cascade          cascade+side+win=1
plain            2000     1984       4.7e-4               8.7e-4           8.7e-4
plain            2016     1984       4.6e-4               9.0e-4           9.0e-4
plain           20500    19968       1.6e-4               2.3e-4           2.3e-4
encoded (3,4,3)  2000     1984       5.9e-4               6.9e-4           9.5e-4
encoded (3,4,3)  2016     1984       5.5e-4               8.9e-4           6.7e-4
encoded (3,4,3) 20500    19968       1.5e-4               2.3e-4           2.3e-4
~~~

The cascade path is within 1.2-2x of the single pass's own bf16 rounding error (outputs are O(0.1-1), bf16
ulp there is 4e-4 to 4e-3), i.e. one extra bf16 rounding of a partial output. Generation: plaintext vs
plaintext+cascade on the B=4 long prompt diverge at output token 4; the reference top-2 logits there are
32.75 / 32.50 (a 0.25 gap = one bf16 ulp of the lm_head output at that magnitude) and the cascade run has
them exactly tied at 32.50 / 32.50, while the largest logit difference over the identical earlier steps is
0.375 (1.5 ulp). So the cascade divergence is a bf16 tie flip, not a logic error; the encoded cascade
variants are numerically equivalent to plaintext at the same level as any other reordering of the
softmax reduction. Verdict: the token-identity criterion holds exactly for sealing / windows / tau; for the
cascade it holds up to bf16 ties, and the attention-output error is quantified above.

## 2026-09-03 09:45 PDT -- item 1: side-stream sealing (`--phase seal`, seal.csv)

Setup: KV filled to ctx (random), CUDA-graph step time of (a) a normal step, (b) a step whose appended token
completes a page (the seal is launched inside the step), and (c) an eager 96-token greedy generation with
real appends (3 page fills in 96 steps) -- mean and max per-step latency. Plaintext from the same run.

~~~
(3,4,3)                 step ms    fill-step ms (sync)   fill-step ms (side)   gen mean ms sync -> side      plain gen mean
B=1  ctx=30K            13.31       115.1 (+101.8)         21.0 (+7.7)          18.47 -> 15.69  (-15.1 %)     13.11
B=8  ctx=30K            41.74       144.2 (+102.4)         53.7 (+11.9)         47.51 -> 44.63  ( -6.1 %)     14.84
B=8  ctx=60K            74.42       176.3 (+101.9)         89.2 (+14.9)         79.61 -> 76.86  ( -3.5 %)     19.33
B=8  ctx=90K           106.36       207.0 (+100.7)        125.9 (+19.6)        111.48 -> 109.06 ( -2.2 %)     23.67
B=1  ctx=118K           24.93       126.8 (+101.8)         34.0 (+9.2)          30.08 -> 27.15  ( -9.7 %)     13.45
(2,6,4)  fill penalty sync +91..92 ms, side +7.0 (B=1) .. +21.1 ms (B=8, 90K); gen mean -14 % (B=1) / -2..6 % (B=8)
~~~

* Phase-1 behaviour confirmed: the page that fills is encoded synchronously on the main stream; one PoRep
  encode is a sequential chain per block (32 KB, l=3 layers x r=3 rounds), ~1.8 ms per launch, and the 28
  layers x {K, V} = 56 launches per fill step are serialized on the main stream: +102 ms (3,4,3) / +92 ms
  (2,6,4) on one step in 32, independent of B (blocks encode in parallel across the batch). Averaged over
  32 steps that is +3.2 ms per token: +24 % at B=1/30K, +7.6 % at B=8/30K, +3 % at B=8/90K.
* Side-stream sealing removes 85-93 % of that penalty: the fill step costs +7.7 ms (B=1) to +19.6 ms (B=8,
  90K) instead of +102 ms. The remainder is (i) the join at the end of the step -- the last layers' encodes
  (~2 x 1.8 ms) cannot overlap anything, and (ii) SM contention: the encode kernels (B blocks, one
  sequential chain each) hold a few SMs while the main stream's decode/attention kernels run, which is why
  the residual grows with B and ctx. Deferring the join to the next step's read of that layer (the encode
  would then have a whole step to finish) would remove (i); not done, it is worth <= 0.6 ms per token
  averaged (the fill step is 1 in 32).
* TPOT effect (eager generation, real appends): -6.1 % / -3.5 % / -2.2 % at B=8 for 30K / 60K / 90K, -15 %
  / -10 % at B=1 (30K / 118K). Tail latency: max step 146 -> 56 ms at B=8/30K.
* Plaintext exposure: with window=0 the partial page (<= 31 tokens per sequence per layer) plus, during the
  fill step only, the staging copy of the sealing page (32 tokens) are plaintext: <= 63 tokens per sequence
  for one step, <= 31 tokens otherwise = 0.03-0.1 % of a 30K-118K context. Measured `plaintext_tokens_max`
  after each step: 31.

## 2026-09-03 10:35 PDT -- items 2, 4, 6 (`--phase window,rekey,tau`, window.csv / tau.csv / rekey_v1.csv)

### Item 2: plaintext working window W (pages of 32 tokens), (3,4,3), CUDA-graph step ms

~~~
B  ctx      plain    W=0      W=1      W=2      W=4      W=64 (2064 tok = 1.7-6.9 % of ctx plaintext)
1  30K      8.65     13.19    13.29    13.21    13.25    12.78
1  118K    10.32     24.71    24.75    24.93    24.89    24.94
8  30K     13.00     42.25    42.26    42.03    41.52    41.72
8  60K     17.46     74.42    74.30    74.28    74.25    74.30
8  90K     21.81    106.33   105.20   105.16   106.44   106.37
~~~

The saving is below the run-to-run noise (+-1 %) for W = 1-4 pages (0.05-0.5 % of the context plaintext),
and even W = 64 pages (2K tokens, 7 % of a 30K context) recovers only 1-3 % of the encoded-KV overhead
(expected ~3 % from the model -- confirmed as "small", in fact smaller: a window page is still copied into
the attention scratch, so only the decode's instruction cost is saved, not its traffic). The window does not
reduce encode work either (one page is sealed per 32 tokens whatever W is). Recommendation: W = 0 -- the
plaintext exposure is then the partial page only (+ the in-flight page for one step with side sealing). A
window only makes sense if a design needs the newest tokens plaintext for another reason (e.g. sliding-window
attention layers); its security cost is exactly W x 32 tokens per sequence the adversary holds for free
(0.1 % of a 30K context per page).

### Item 4: speculative-decoding factor tau (query tokens per step, all accepted = upper bound), ms per generated token

~~~
B  ctx    config    tau=1           tau=2          tau=3          tau=4         (x = vs plaintext at the same tau)
1  30K    plain      8.70            5.77           3.90           2.95
          (3,4,3)   13.30 (1.53x)    8.06 (1.40x)   5.42 (1.39x)   4.08 (1.38x)
1  118K   plain     10.32            6.59           4.44           3.35
          (3,4,3)   24.95 (2.42x)   13.91 (2.11x)   9.31 (2.09x)   7.00 (2.09x)
8  30K    plain     13.00            8.11           5.34           4.04
          (3,4,3)   41.72 (3.21x)   22.47 (2.77x)  14.92 (2.79x)  11.35 (2.81x)
8  60K    plain     17.46           10.35           6.83           5.16
          (3,4,3)   74.32 (4.26x)   38.76 (3.75x)  25.78 (3.77x)  19.37 (3.75x)
8  90K    plain     21.82           12.51           8.28           6.24
          (3,4,3)  106.33 (4.87x)   54.77 (4.38x)  36.46 (4.40x)  27.37 (4.38x)
(2,6,4): 12.86 / 7.87 / 5.30 / 3.98 at B=1 30K; 99.29 / 51.22 / 34.09 / 25.60 at B=8 90K
~~~

* The step time is nearly flat in tau for both plaintext and encoded (B=8/90K: plain 21.8 -> 25.0 ms, encoded
  106.3 -> 109.5 ms from tau=1 to 4): weights and the (decoded) KV are read once per step, the extra query
  rows are free. Hence the **absolute** encoded overhead per generated token falls as 1/tau as predicted:
  84.5 -> 42.3 -> 28.2 -> 21.1 ms at B=8/90K.
* But the plaintext per-token cost falls the same way (the plaintext decode step is KV-read-bound at these
  contexts), so the **slowdown factor vs a plaintext server that also speculates** only drops from 4.9x to
  4.4x (B=8/90K), 3.2x to 2.8x (B=8/30K), 1.5x to 1.4x (B=1/30K). The tau=2 -> 4 plateau is a real effect:
  at tau=1 the plaintext step uses the GEMV path and at tau >= 2 the linears switch to GEMM (+3 ms per step
  at every B), which is a one-off that the encoded model pays as well.
* Against a **non-speculating** plaintext baseline (tau=1), encoded tau=3 gives 14.9 / 25.8 / 36.5 ms per
  token at B=8 30K / 60K / 90K = 1.15x / 1.48x / 1.67x, i.e. speculation buys the overhead back only if the
  comparison server does not use it. Both columns are reported for item 7.

### Item 6: pool re-key (decode under the portable key + re-encode under the slot key), 100K-token context = 5.73 GB (K+V, 28 layers)

~~~
params            page   decode ms   encode ms   re-key ms   re-key GB/s   one page (decode+encode) ms
(3,4,3) n=1024    32 KB    11.6        599.1       610.7        9.4          1.82
(2,6,4) n=1024    32 KB    10.6        540.2       550.8       10.4          1.64
(3,4,3) n=2048    64 KB    11.8        898.3       910.1        6.3          3.63
(2,6,4) n=2048    64 KB    11.0        809.3       820.3        7.0          3.26
~~~

* The re-key is encode-bound: the decode of 5.7 GB takes 12 ms (490 GB/s), the encode 0.54-0.90 s (6-10 GB/s
  -- one sequential chain per block, throughput = blocks in flight / chain latency; 64 KB blocks halve the
  number of chains and double their length, so the throughput drops by a third and one-page latency doubles).
* TTFT impact at 94 % hit if every hit page comes from the pool (worst case; local HBM hits need no re-key):
  turn 1 (30K context, 28.2K hit tokens, 1.6 GB per sequence): 172 ms per sequence at (3,4,3)/32 KB; turn 30
  (118K, 111K hit tokens, 6.4 GB): 680 ms per sequence. For B=8 sequences arriving together that is 1.4 s /
  5.4 s of side-stream encode against plaintext TTFTs of 4.0 s / 24 s (B=8 t1 / t30): +35 % / +23 % if it
  cannot be overlapped, 0 % if the pool fetch + re-key is pipelined with the prefill of the (1-hit) miss part
  and the new 2048 tokens (the prefill is compute-bound and the re-key uses integer units on a few SMs).
* Interference (first version): a 1 GB decode (the step's KV decode) alone 2.18 ms; with the re-key running
  on a plain side stream 2.73 ms (+25 %) for 32 KB blocks but 6.47 ms (+190 %) for 64 KB blocks: the encode
  grid saturates the SM thread-block slots and the main stream's kernels wait for encode blocks (1.8 / 3.6 ms
  lifetimes) to retire. The rerun below adds chunked launches and a high-priority main stream.

## 2026-09-03 11:20 PDT -- item 3 (cascade, step level) and item 5 (page size) (`--phase pagesize` + `--phase tau --cascade`)

### Item 3: shared-prefix cascade at B=8 (20K shared prefix decoded + attended once per step), CUDA-graph step ms

~~~
ctx    plain    plain+cascade   (3,4,3)   (3,4,3)+cascade          (2,6,4)   (2,6,4)+cascade
30K    13.00    12.26 (-5.7 %)   41.72     25.18 (-39.6 %; 1.94x)   39.72     23.99 (-39.6 %; 1.85x)
60K    17.46    16.73 (-4.2 %)   74.32     57.65 (-22.4 %; 3.30x)   69.47     54.22 (-22.0 %; 3.11x)
90K    21.82    21.08 (-3.4 %)  106.33     88.76 (-16.5 %; 4.07x)   99.29     84.08 (-15.3 %; 3.85x)
with tau=3 (ms per token): (3,4,3)+cascade 9.18 / 20.00 / 30.37 vs plain+cascade tau=3 4.90 / 6.39 / 7.84 (1.87x / 3.13x / 3.87x)
~~~

* The saving matches the decode-sharing model: shared fraction 20K/ctx x (B-1)/B of the encoded overhead
  (30K: 0.667 x 7/8 x 28.7 ms = 16.7 ms predicted, 16.5 ms measured). Slowdown at B=8 drops from 3.2x /
  4.3x / 4.9x to 1.9x / 3.3x / 4.1x (30K / 60K / 90K). Plaintext also gains 3-6 % from attending the shared
  prefix once (Hydragen effect) -- both baselines are reported in item 7.
* Security: neutral. The shared pages are the same encoded blocks; the implementation reads one physical
  copy (sequence 0's), exactly what a paged server with prefix caching stores (one block, B references).
  Our dense `[B, n_pages]` layout still holds B copies in HBM (a block table would free 7/8 of the prefix
  memory) -- memory is not what RQ7 measures, the compute/traffic saving is identical.

### Item 5: page (= PoRep block) size, (3,4,3): raw kernels and e2e decode step

~~~
block            chunk  n      decode GB/s   decode/memcpy   encode GB/s   one-page encode ms   e2e B=8 90K ms (x plain)   B=1 30K   B=8 30K
32 KB  (phase 1)  32   1024      491            3.08x            9.3            1.80              106.4 (4.85x)              1.53x     3.21x
64 KB             32   2048      479            3.16x            6.2            3.60              108.7 (4.96x)              1.55x     3.31x
64 KB             64   1024      296            5.12x            9.7            2.30              160.5 (7.32x)              1.82x     4.70x
128 KB            32   4096      389            3.89x            2.4            7.20              126.7 (5.78x)              1.67x     3.88x
(2,6,4): 535 / 517 / 377 / 356 GB/s; e2e B=8 90K 4.53x / 4.62x / 6.01x / 6.27x
~~~

* Security constraints (graphs.md): n >= 2048 chunks per block recommended (n = 1024 is the phase-1 block
  and is below the recommendation; n = 512 is out). That rules out every 32 KB variant at chunk 32, and 64 KB
  at chunk 64 (n = 1024, and it decodes at 60 % of the speed: the wider chunk makes the mixer 2x more
  instructions per byte on this kernel).
* **Recommendation: 64 KB pages, chunk 32, n = 2048.** Cost vs the phase-1 32 KB block: +2 % on the decode
  step (479 vs 491 GB/s decode), one-page encode latency 3.6 ms instead of 1.8 ms (hidden by side-stream
  sealing; a page fills every 64 tokens instead of 32, so the per-token fill overhead is unchanged), re-key
  throughput 6.3 GB/s instead of 9.4 GB/s, plaintext exposure <= 63 tokens per sequence (+64 in flight for
  one step) instead of <= 31. 128 KB (n = 4096) buys nothing the constraint requires and costs +19 % decode,
  7.2 ms encode latency, 2.4 GB/s re-key, and a 2x larger plaintext window.

## 2026-09-03 12:25 PDT -- item 6 rerun: re-key interference (rekey.csv; the first run is rekey_v1.csv)

1 GB decode (one step's KV decode) on the main stream while half a 100K-token context re-keys on a side stream:

~~~
                     side launch          main-stream decode ms (alone 2.19 / 2.23)    re-key throughput GB/s
(3,4,3) 32 KB        one launch, same prio     2.73 (+25 %)                                 9.3
                     one launch, main high     2.76 (+26 %)                                 9.2
                     chunks of 1024 blocks     3.17 (+45 %)                                 8.7
                     chunks of 256 blocks      2.51 (+15 %)                                 4.5
(3,4,3) 64 KB        one launch, same prio     6.46 (+190 %)                                6.2
                     one launch, main high     5.57 (+150 %)                                6.2
                     chunks of 1024 blocks     4.28 (+92 %)                                 6.0
                     chunks of 256 blocks      3.27 (+47 %)                                 4.5
(2,6,4): 32 KB +28 % -> +21 % (chunks of 256, 5.0 GB/s); 64 KB +189 % -> +45 % (3.0 ms, 5.0 GB/s)
~~~

The encode grid saturates the SM thread-block slots; stream priority alone helps little (the encode blocks
live 1.8 / 3.6 ms and priority only reorders pending blocks). Chunking the side-stream launches to 256
blocks (8 MB at 32 KB, 16 MB at 64 KB) bounds the slowdown of the concurrent step to +15 % (32 KB) / +47 %
(64 KB) at 4.5 GB/s re-key throughput -- i.e. a 100K-token context re-keys in ~1.3 s while the server keeps
decoding at 68-87 % speed. A proper fix is a re-key kernel with a capped persistent grid (e.g. 16 SMs);
this benchmark has no such knob. Re-key cost per 64 KB page: 3.6 ms latency, 0.16-0.22 ms of encode
throughput-time (6.3 GB/s single stream).

## 2026-09-03 12:35 PDT -- item 7: the Mooncake session (agentic.py, results/phase2/rq7/agentic_session.csv)

Session = 20K shared prefix + 10K first input, 30 turns x (2048 in / 900 out), 94 % prefix hit, contexts 30K
-> 118K; measured points 30K / 60K / 90K / 118K (B=8 up to 90K, 45 GB KV cap; turn 30 extrapolated flat as
in phase 1), prefill of the 2048 new tokens + 6 % miss, CUDA-graph decode step **and the page-fill step** (new:
the seal cost is amortized over the 32 tokens of a page, the phase-1 integral ignored it). Same plaintext
weights everywhere. All rows from `agentic_session.csv`, `x` = vs the plaintext row with the same B and tau.

~~~
B=8                                            session s        prefill s   decode s    TPOT t1 ms     TPOT t30 ms     out tok/s/GPU
plain                                           926.5            421.5       504.9       13.0           21.8            233
plain + cascade                                 914.1 (0.99x)    429.0       485.0       12.3           21.1            236
(3,4,3) phase-1 design (sync seal, W=0)        2779.8 (3.00x)    434.3      2345.5       45.6 (3.50x)  109.7 (5.03x)     78
(3,4,3) side seal + W=1                        2703.2 (2.92x)    431.6      2271.5       42.6 (3.27x)  107.1 (4.91x)     80
(3,4,3) side seal + W=1 + cascade              2238.2 (2.42x)    437.2      1801.0       25.5 (1.96x)   89.1 (4.09x)     96
(2,6,4) phase-1 design                         2617.9 (2.83x)    432.2      2185.8       42.6 (3.28x)  102.2 (4.68x)     82
(2,6,4) side seal + W=1 + cascade              2144.0 (2.31x)    436.5      1707.5       24.3 (1.87x)   84.7 (3.88x)    101
--- tau = 3 (speculative-verify emulation, all accepted: upper bound) ---
plain tau=3                                     617.3            421.6       195.7        5.35           8.29           350
plain + cascade tau=3                           613.0 (0.99x)    429.3       183.7        4.91           7.84           352
(3,4,3) phase-1 design tau=3                   1299.8 (2.11x)    434.1       865.7       18.3 (3.42x)   39.6 (4.78x)    166
(3,4,3) side + W=1 + cascade tau=3             1065.8 (1.73x)    437.4       628.5        9.5 (1.77x)   30.7 (3.71x)    203
   ... the same row vs the NON-speculating plaintext (926.5 s / 21.8 ms):  1.15x session, 1.41x TPOT t30

B=1                                            session s        TPOT t1 / t30 ms
plain                                           317.7            8.7 / 10.3
(3,4,3) phase-1 design                          671.7 (2.11x)   16.5 / 27.8
(3,4,3) side seal + W=1                         590.9 (1.86x)   13.5 / 24.9      <- best at B=1 (cascade is a loss at B=1: 648.1 s)
(3,4,3) side + W=1 + cascade tau=3              287.9 (1.66x vs plain tau=3 174.0; 0.91x vs plain tau=1)
~~~

Per-trick saving at B=8, (3,4,3), relative to the phase-1 design (2779.8 s, TPOT t30 109.7 ms):

~~~
trick                         session time         TPOT turn 30           TPOT turn 1        security
side-stream sealing (+W=1)    -2.8 % (2703 s)      -2.4 % (107.1 ms)      -6.6 % (42.6)      neutral (<= 1 extra page in flight per step)
plaintext window W=1..4       within noise         within noise           within noise       W x 32 tok/seq plaintext (0.03-0.5 %)
shared-prefix cascade         -17.2 % (2238 s)     -16.8 % (89.1 ms)      -40 % (25.5)       neutral (one physical copy of the prefix)
all three (tau=1)             -19.5 % => 2.42x     -18.8 % => 4.09x       -44 % => 1.96x
+ tau=3 vs plain tau=3        1.73x session        3.71x                  1.77x              neutral (KV decoded once per verify step)
+ tau=3 vs plain tau=1        1.15x session        1.41x                  0.73x
~~~

The sync-seal penalty was invisible in the phase-1 integral (the graph step never fills a page); with it the
phase-1 design is 3.00x, not 2.84x. The phase-1 estimate for the cascade (-24 % session-averaged, -59 % at
turn 1) was optimistic: -17 % / -44 % measured on the encoded rows, because (a) the prefix is 20K of a
context that grows to 118K (the shared fraction averages ~30 % over the session) and (b) the private part is
also decoded at B=8. The turn-1 TPOT at B=8 goes from 45.6 to 25.5 ms (1.96x plaintext) -- at short context
the design is now within 2x. The residual is the long-context tail: at 90-118K the KV decode is 3.7-4.1x
plaintext, and that is the decoder's instruction cost (491 GB/s decode vs the ~1.9 TB/s at which plaintext
attention streams the KV), which no systems trick addresses -- only a cheaper mixer (K1) or fusing the decode
into the attention kernel (saves the scratch write + re-read, i.e. at most the memcpy share of the decode
time, 1/3.1 = 32 % of the overhead).

**Pass criterion (<= 1.8x at B=8, security constraints respected): not met at tau=1 (2.42x with sealing +
cascade at (3,4,3); 2.31x at (2,6,4)). Met only in the speculative-decoding column: 1.73x against a
plaintext server that speculates equally well (upper bound: every drafted token accepted, no drafter
cost), 1.15x against a non-speculating plaintext server.** With the recommended 64 KB page (n=2048) add
+2 % to the encoded rows (item 5).
