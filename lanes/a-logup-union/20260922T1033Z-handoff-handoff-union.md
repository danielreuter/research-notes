---
id: r20-proof/a-logup-union/20260922T1033Z-handoff-handoff-union
campaign: r20-proof
lane: a-logup-union
kind: handoff
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/gkr/gpu/HANDOFF_UNION.md
---

# Batched logUp over the table union: shape hand-off for `a-gpu-v2` and `a-gpu2` (lane a-logup-union, 2026-09-22)

Spec: `backends/gkr/PROTOCOL.md` §15. Reference implementation: `backends/gkr/src/logup.rs` (`union_*`) and
`main.rs` (`start_transcript`, `add_union_claim`), selected by `--logup union` (`VERITY_GKR_LOGUP=union`).
Accounting: `security.accounting.logup_union_error`, `CandidateA(lookup_mode="union")`. Red-team:
`redteam.logup_union`, `fixtures/redteam-3/logup-union/`. This is a **protocol change to the lookup argument only**;
the relation, the export, the committed columns, the chain and the opening are unchanged. The per-table path stays
the default in the Rust crate until the coordinator flips it.

## What it is, in one paragraph

The twelve v2 tables (`T_OP`, `ALIGN4`, `SHIFT`, `SSHIFT_HI`, `SSHIFT_LO`, `LEAD`, `LEADNORM`, `TNORM`, `R12`,
`R4`, plus the epilogue's `R16`, `R15`) are proved by **one** fractional-GKR instance. Every element carries its
table: a query vector \(w\) into table \(t\) and a row \(r\) of \(t\) are both encoded as
\(\phi(w,t)=\sum_k w_k\beta^k+\gamma\cdot\mathrm{tag}(t)\), \(\mathrm{tag}(t)=1+\text{index}\) (1..12), with one
challenge message \((z,\beta,\gamma)\) drawn after the commitment. Leaves: queries \((p,q)=(1,\ z-\phi)\); rows
\((-m_v,\ z-\phi)\); padding \((0,1)\). Soundness: unchanged budget (\(2^{-127.71}\) headline / \(2^{-130.16}\) at
`hash_queries=2^60`, both Goldilocks\(^3\) and BabyBear\(^6\)); the lookup bucket \(2^{-165.2}\) at B = 4096.
z3 verdict: forgery UNSAT outside a finite collision set of \(\gamma\), multiplicity manipulation buys nothing.

## The shape

| | B = 64 | B = 4096 |
|---|---|---|
| query leaves \(N\) = 86·96·B + 5·B | 528 704 | 33 837 056 |
| table leaves \(|T|\) = Σ rows (fixed per proof) | 5 245 624 | 5 245 624 |
| live leaves \(N+|T|\) | 5 774 328 | 39 082 680 |
| tree dimension \(n=\lceil\log_2(N+|T|)\rceil\); leaves \(2^n\) | **23**; 8 388 608 (69 % live) | **26**; 67 108 864 (58 % live) |
| sumcheck rounds Σ levels = n(n−1)/2 | 253 | 325 |
| \(\mu,\lambda\) trips (critical path) = 1 + Σ_{k=1}^{n−1}(k+1) | 276 (per-table deepest: 253) | 351 (per-table deepest: 300) |
| verifier coins for lookups | 3 + 253 | 3 + 325 |
| instances (graphs to build, streams) | 1 (per-table: 12) | 1 (per-table: 12) |

`GraphLogUp.build(Nw, Nt)` wants `Nw` and `Nt` multiples of \(2^{k+1}\) (=16 at k=3). `Nw` = 33 837 056 is a
multiple of 16; `Nt` = 5 245 624 is not (÷16 = 327 851.5) — pad the table side to 5 245 632 with rows of
multiplicity 0 (any \(q\ne0\), e.g. \(\phi\)=0, so \(q=z\)); the padding rows are public and enter the verifier's
table-side evaluation with \(m=0\). At B = 64 pad `Nw` from 528 704 (÷16 = 33 044 exactly — fine) as well if the
epilogue count changes.

Leaf layout (transcript-fixed, `logup.rs::union_fill`): segment 0 (unit circuit) units 0..96B−1, each its 86
lookups in `circuit.txt` order; then the epilogue segment, B units × 5 lookups; then the tables in tag order, each
its rows in materialised/listed order; then padding to \(2^n\).

## What changes on the device

Only the **leaf level**. The tree levels, the per-level sumcheck graphs, the fold, the \(\mu,\lambda\) chain and
the final leaf claim are shape-only (`build(Nw, Nt)` with the numbers above). Concretely:

1. `kg.histogram(w, Nt, mult)` assumes one base-field column with key = value = table index. The union has
   twelve tables: compute the multiplicities **per table** (dense tables `SHIFT`/`SSHIFT_*`/`TNORM`/`R*`: histogram
   of the key column over that table's key range; listed tables `T_OP`/`ALIGN4`/`LEAD`/`LEADNORM`: a device hash or a
   host-side dict — 3120–65 280 rows) and concatenate in tag order. This is the same work as the per-table path;
   the multiplicities are committed in \(X\) exactly as before (layout unchanged).
2. Query-side leaves: \(q_j = z_t - \sum_{k<c_t}\beta^k w_{j,k}\) where \(z_t = z-\gamma\,\mathrm{tag}(t)\) is a
   per-table **extension-field** constant (12 of them) and \(w_{j,k}\) are the \(\le3\) base-field values of the
   query's linear forms (gathers of committed columns; the forms are in `circuit.txt`, `Query.cols`). The current
   `leaf_level(w, z, ...)` does \(z - w\) with one base column and one constant: extend it to
   `leaf_level_union(w_cols[3], ncols_per_leaf, zt_per_leaf_or_per_segment, beta_pows[3])`. Segment the 86
   lookups per unit by table (a static per-unit pattern: the same 86 (table, cols) descriptors for every unit), so
   the kernel reads the descriptor by `j % 86`.
3. Table-side leaves: \(q_v = z_t - \phi(r_v)\) with the row materialised on device from the `itable` parameters
   (14.6: `shift`/`tnorm` are one shift and one multiply per row; \(c_t\) = 2 for `shift` (key, value) — check
   `circuit.rs::materialise` for the exact column layout) and listed rows uploaded once; \(p_v=-m_v\).
4. Nothing else: `T4_tab` / `tab_dst` interleave, `_tree_level_kernel`, `_level_ops`, coins buffer `(n+1, 6)` all
   take `n = 26` (B = 4096) / `23` (B = 64).

Extension-field leaves already exist (the \((p,q)\) pairs are 6-limb rows); the only new ext arithmetic is the
per-table constant subtraction and \(\beta^k\)-scaling of a base value (3 limb multiplies), same as `leaf_level`.

## Transcript (byte-exact with `main.rs::start_transcript`)

1. Preamble: per segment `sha256(circuit text)`, `units` as u64 LE.
2. **Union marker** (only in this mode): `label("preamble: lookup argument = union (PROTOCOL.md 15), table order as tagged")`,
   `absorb(b"logup-union-v1")`, then for each table in tag order `absorb(u64 LE (index+1))`, `absorb(name bytes)`.
3. Clear mode: `sha256` of all committed column values; PCS mode: the Ligero Merkle root.
4. Chain: steps u64 LE, then the public `y16` words.
5. `label("union logup over 12 tables: z, beta, gamma (tag(t) = 1 + table index)")`; `z = challenge()`,
   `beta = challenge()`, `gamma = challenge()` — **γ is derived here, after the root, i.e. after the multiplicities
   are committed** (they are part of \(X\)).
6. Per segment: \(z_0\) (`s_out` coordinates), copy point (\(\log_2\) units coordinates) — unchanged.
7. Then the usual order: multiplicity/root claims, the levels' sumchecks (one chain instead of twelve; the union
   instance goes where table 0's instance went), the checker layers, the opening. `add_union_claim` contributes one
   linear functional to the batched opening in place of the twelve per-table functionals.

The lookup mode is in `result.json` as `lookup_mode` and in the transcript as the marker above: a union proof does
not verify per-table and vice versa (`tampered_proof_is_rejected`).

## Cost model for the H100 (from `note:r20-proof/a-fusion/20260922T0853Z-report-a-kernels-h100-v2`, to be replaced by your measurement)

Per-table v2: 221.6 ms sequential, 84.7 ms on 10 streams, "each instance pays ~14 ms of small-level latency";
modelled 35 ms. The union has one instance: the small-level latency is paid once (~14 ms), the big levels are the
same total work (\(2^{26}\) vs \(2^{24}+2^{23}+\dots\): ~1.4× more leaf work because of the 42 % padding at
B = 4096 — consider \(k\)-packing the top two levels or splitting into two instances of \(2^{25}\) if the padding
shows; at B = 64 the padding is 31 %). Estimate: **25–40 ms** (a-fusion's 25–35 ms plus the padding). The
per-round host trips (`rounds_per_graph = 1`) drop from Σ over 12 instances (~1900 rounds) to 325.

## CPU-measured ratio (vy-cpu, EPYC 9655P, 12 threads, same binary and instances, `LOGUP=both`)

| B | per-table prove / lookup (s) | union prove / lookup (s) | union / per-table | bytes | coins | depth |
|---|---|---|---|---|---|---|
| 64 (r20260922-101533-20c4) | 7.37 / 4.41 | 7.09 / 3.96 | **0.96× / 0.90×** | 0.95× | 2525 → 642 | 257 → 280 |
| 4096 (two runs, r20260922-102013-2931 + -102556-cdcc) | 65.1 / 26.9 (mean) | 70.3 / 29.8 (mean) | **1.08× / 1.11×** | 0.995× | 3393 → 761 | 304 → 355 |

So on the CPU the union is a wash: the one \(2^{26}\) tree (67.1M leaves, 39.1M live) does ~1.25× the leaf work of
the twelve padded per-table trees (53.7M leaves in total) and there is no per-instance fixed cost to amortise on a
CPU. **Expect the GPU picture to be the opposite of the CPU one only if your per-instance latency (~14 ms × 12 on
the H100) exceeds the extra 13.4M leaves' worth of tree work (~0.2 ms at H100 bandwidth).** If the padding hurts,
k-pack the top levels or split the union into two trees of \(2^{25}\) (queries | tables) with the same challenges —
that is still one instance for the transcript if both trees' root claims are absorbed together (needs a §15 amendment;
not implemented).

## Open for the GPU lanes

* Whether the 12-way per-table streams or the one padded union tree wins on the H100 is the measurement this
  hand-off asks for; the soundness side is settled (§15.2), so the decision is purely time/bytes.
* The union's depth is +51 trips at B = 4096 (one tree of 26 levels vs the deepest per-table tree of 24): if the
  latency lane's `--rtt-ms` axis matters more than prover time, per-table stays.
* BabyBear\(^6\): `char F = 2^31 − 2^27 + 1 > N = 3.4·10^7` holds, so the union is admissible there too
  (`logup_union_error` checks it).
