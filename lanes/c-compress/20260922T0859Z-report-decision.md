---
id: r20-proof/c-compress/20260922T0859Z-report-decision
campaign: r20-proof
lane: c-compress
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/vole/DECISION.md
---

# Track C decision note (c-compress, 2026-09-22 morning)

The question the lane was given: C's measured cost was dominated by how the relation was *expressed* (993k committed
elements per VU where the model said ~80k). Can it fall ~12x, and what does C cost then, per VU and per byte, at
2^-128? Everything below is measured on `vy-cpu` (AMD EPYC 9655P, 16 vCPU) with the verifier accepting; runs
`r20260922-072822-1459` (census, negatives), `r20260922-075153-022f` (64 VUs, 4096 VUs F61p),
`r20260922-080520-71b6` (4096 VUs F128p / F384p); ledger `backends/numerical/reports/ledger/c-compress.jsonl`.

## 1. What changed (relation unchanged; same predicates, all negatives still fail)

`export_ir.py` v2 compiles the same WP2 checker (`check_step_expr`, every gadget contract) to SIEVE-IR that uses a
small `dietmc` plugin (`patches/verity_v0.rs`) with three output-free operations:

- `assert_mul(a, b, c)`: the QuickSilver degree-2 check without committing the product. Every boolean check
  `b^2 = b`, every product identity whose output is used once, and every `lt_pow` product now costs 0 committed
  elements instead of 1.
- `range, 10`: a logUp lookup argument (Haböck 2022) into the table `[0, 1024)`. A `w`-bit range obligation is
  `ceil(w/10)` 10-bit chunks (committed) + `ceil(w/10)` committed inverses, instead of `w` committed bits and `w`
  boolean `@mul`s. Interval arithmetic over the exporter's linear forms discharges 69 of the 330 range obligations per
  unit outright (they are implied by other ranges or by linear identities over already-ranged forms).
- `lookup, C, R, table`: the four fixed tables (POW, ALIGN, LEAD, NORM) as logUp lookups on the row tuples, instead of
  one-hot selector vectors (610 committed selectors + their boolean checks per unit -> 22 query tuples + 22 inverses).

dietmc has no lookup argument and no F2 -> F_p conversion cheap enough to matter (the F2/F40b backend costs a
separate sVOLE per bit and a conversion gadget per word); (a) of the brief was therefore not taken, (b)-(d) were,
with the lookup argument implemented as a plugin over the existing IT-MAC backend rather than as polynomial chains.

Prover-side fixes in the same patch: one public LPN matrix per sVOLE instance (was re-sampled per extension: 28% of
instructions), `TCP_NODELAY` (Nagle + delayed ACK stalled every verifier challenge ~30 ms; the logUp argument has 9
challenges per VU, so this alone was 21.8 s -> 2.4 s at 64 VUs), and batched field inversions in the logUp helper
(54 s -> 20 s at F384p, 64 VUs). Binary/flatbuffer IR was not done (`patches/README.md`).

Verification: the exporter's evaluator agrees with `check_step_expr` on every `tu-k16` and `vu-k1536` instance; all
52 WP2 negatives and all 52 `vu-k1536-neg` are rejected by the evaluator (`negatives.txt` in `1459`); dietmc's
verifier accepts every honest batch and rejects the 4 `vu-k1536-neg` VUs exported with `--neg` (`vu-B4-NEG`,
`accepted: false`), and rejects out-of-range / off-table values in the plugin unit tests (`/workspace/irtest/mini.sh`).

## 2. Before / after

| per VU | v1 (c-vole) | v2 (c-compress) | ratio |
|---|---|---|---|
| committed elements (sVOLE correlations) | 993,095 | **101,009** (36.6k range chunks + 38.7k inverses + 4.2k table helpers + 21.4k hints/words/products) | 9.83x |
| multiplication checks | 501,393 (all with committed outputs) | 73,066 (15.9k `@mul` + 57.2k output-free) | 6.9x |
| private values in the witness stream | 491,703 | 42,155 | 11.7x |
| P -> V bytes, F61p, 4096 VUs | 8.50 MB | **0.865 MB** | 9.8x |
| P -> V bytes, F128p, 4096 VUs | 16.7 MB (64 VUs) | **1.68 MB** | 9.9x |
| P -> V bytes, F384p, 4096 VUs | 54.4 MB (8 VUs) | **5.10 MB** (20.9 GB per batch) | 10.7x |
| V -> P bytes, F61p | 1.06 MB | 0.108 MB | 9.8x |
| prover wall, F61p, 4096 VUs, 1 thread | 0.408 s | **0.0302 s** (sVOLE 0.0076 / online 0.0226; plaintext floor 0.016) | 13.5x |
| prover wall, F128p, 4096 VUs, 1 thread | 1.64 s (64 VUs) | **0.132 s** (sVOLE 0.066 / online 0.067) | 12.4x |
| prover wall, F384p, 1 thread | 4.74 s (8 VUs) | **0.307 s** (4096 VUs; sVOLE 0.142 / online 0.162) | 15.4x |
| soundness accountant, 4096 VUs | (t + 3m)/p: F61p 2^-30.1, F128p 2^-97, F384p 2^-353 | (t + 3m + logUp terms)/p with 2.70e6 terms per VU: **F61p 2^-27.6, F128p 2^-94.6, F384p 2^-350** | the ALIGN table's `N R (C-1)/p` collision bound (2.36e6 per VU) dominates |

The model's logUp-mode figure was 83k committed elements / 667 kB per VU; v2 lands at 101k / 0.87 MB (the extra is
the 10-bit chunking of 16-32-bit ranges, which the model priced as one query each, plus sVOLE overhead bytes).

## 3. C at 2^-128, against A and B

The 2^-128 operating point is unchanged: dietmc has no extension-field MACs over a prime field, so F61p (2^-27.6 at
the batch) and F128p (2^-94.6, and the logUp collision term makes it 2.5 bits worse than v1) do not reach it and
F384p does (statistically 2^-350; the cap is the computational stack, AES-128 / KOS / LPN).

| track (latest ledger, 4096-VU scope) | s/VU | overhead vs 1e11 VU/s native | bytes/VU | soundness | proof class |
|---|---|---|---|---|---|
| A (`a-chain`) | 0.0727 | 7.4e9 | (not communication-bound) | 2^-127.7 | NON_ZK_PROOF_DIAGNOSTIC |
| B (`b-chain`, BabyBear, 166 queries) | 0.0410 | 4.2e9 | (proof size, not a stream) | 2^-128.6 proven | NON_ZK_PROOF_DIAGNOSTIC |
| C v1, F384p (8 VUs) | 4.74 | 4.8e11 | 54.4 MB | 2^-128 | COMPLETE_ZK_BACKEND (designated verifier) |
| **C v2, F384p, 4096 VUs, 1 thread** | **0.307** | **3.1e10** | **5.10 MB** | 2^-128 | COMPLETE_ZK_BACKEND (designated verifier) |
| C v2, F384p, 4 sVOLE threads | 0.265 | 2.7e10 | same | 2^-128 | |
| C v2, F61p (sensitivity point) | 0.0302 | 3.1e9 | 0.865 MB | 2^-27.6 | |
| C v2, F128p | 0.132 | 1.3e10 | 1.68 MB | 2^-94.6 | |

Reading: at the field that reaches 2^-128, C's prover is now within 4.2x of A and 7.5x of B in wall time
(from 65x / 115x before), with a complete designated-verifier ZK stack where A and B are still non-ZK diagnostics. At
F61p, C's per-VU time is already *below* A's and near B's, but 2^-27.6 is not a security level.

## 4. The communication wall

Native rate 1e11 VU/s (the campaign's normalisation); a prover with 1e6 overhead processes 1e5 VU/s and must stream

| field | bytes/VU | link for a 1e6-overhead prover | link for the current CPU prover |
|---|---|---|---|
| F61p | 0.865 MB | **0.69 Tb/s** | 0.23 Gb/s at 0.030 s/VU |
| F128p | 1.68 MB | 1.3 Tb/s | 0.10 Gb/s |
| F384p | 5.10 MB | **4.1 Tb/s** | 0.13 Gb/s |

v1 needed 1.4 Tb/s at F61p and 44 Tb/s at F384p for the same 1e6 target. Compression bought 10x; the wall is still
~10-50x above a 25-100 Gb/s NIC at 2^-128. For the *current* CPU prover (overhead 1e10) the link is trivially
sufficient (sub-Gb/s), so today C is compute-bound, not link-bound; the wall only bites once the prover approaches
the GPU floor (`note:r20-proof/c-vole/20260922T0646Z-report-gpu`: ~50 us/VU arithmetic).

What AntMan would have to buy (`note:r20-proof/c-vole/20260922T0620Z-report-antman` §3): bytes per VU from 5.1 MB (F384p) / 0.87 MB (F61p) down to the
50 kB-per-VU regime at their measured constant (5 kB asymptotically) - i.e. another 20-100x - at the price of
ring-LWE (BGV) + noise-flooding circuit privacy + a random oracle added to the assumption stack, ~5x more prover
arithmetic in NTT form, a field with a large power-of-two subgroup (not F_{2^61-1}), and an implementation that does
not exist in swanky. That is the *only* route to a 1e6-overhead C prover on a real network; relation compression has
now taken the only 10x that was available inside the direct stack (the remaining committed elements are the hints,
range chunks and inverses the relation genuinely needs; a further 2x is conceivable from 16-bit chunks at F128p+
and a tighter lookup soundness argument, not 10x).

## 5. Verdict

C at 2^-128 is now 0.307 s/VU and 5.10 MB/VU with a complete designated-verifier ZK stack, i.e.
7.5x B's and 4.2x A's prover time (both non-ZK diagnostics); on communication alone it cannot reach the 1e6-overhead goal without AntMan-class SIMD
(4.1 Tb/s per prover otherwise), and with AntMan it trades the campaign's hash-only preference for ring-LWE
plus a 5x arithmetic increase. Recommendation: keep C as the *complete-ZK reference* (it is the only track with a real
ZK stack measured end to end, and it is now cheap enough to run on every batch), do not fund a C GPU prover or an
AntMan port on the goal's terms; if a designated-verifier system is acceptable to the product, the next 2x items are
binary IR (parse floor is half the F61p prover) and extension-field MACs in `swanky-field` (F61p^3 or ^7 would give
2^-128 at F61p's byte count, 0.87 MB/VU, 6.5x below F384p).
