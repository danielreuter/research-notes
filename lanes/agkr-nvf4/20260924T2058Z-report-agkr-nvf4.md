---
lane: agkr-nvf4
kind: report
created: 2026-09-24T20:58Z
status: open
---

CHECKPOINT 95343488 (00:35Z) [open] dev 0.1689s (sha 091fecad unchanged): leaf buffers, keep qvals, fused leaf level, pad closed form, scatter/gate_eval grid order (L2 reuse), pinned t_ext. tip 024f1cfc+. Next: opening wq host (open_w_qc_eval 13ms), phase1 per-round.
CHECKPOINT c3982dd5 (00:21Z) [open] dev 0.1828s (sha 091fecad same): e1bcf472 pinned H2D, 0b7dbb3a leaves into graph buffers, c3982dd5 keep query tuples on 32GB. ff98 0.1905s PRESERVED. Next: LogUp tree deinterleave/T4_big copies (tree 8.4ms).
CHECKPOINT 57038af (00:05Z) [open] ff98 @716ea008 recorded+PRESERVED: t.total 0.1905s, 2^-130.19, arts 49757870/78b3aadf, verify-po handoff 0005Z. e1bcf472 pinned H2D -> 0.1885 dev. Next: lookup pad closed form, phase-1 host work.
CHECKPOINT 716ea008 (00:03Z) [open] recorded r20260924-235457-ff98 @716ea008 t.total 0.1905s (5 reps) art:49757870 result art:78b3aadf run-files, same proof bytes as 1b1d; verify-po handoff 0005Z; adopted agkr-fp8 prover commits + compiled witness step; next: phase-1 pinned H2D
CHECKPOINT 2b25df7f (23:42Z) [open] recorded r20260924-233405-1b1d @2b25df7f t.total 0.245s art:5adf62eb result art:d6673af2 run-files PRESERVED (thread caps fixed); verify-po handoff 2350Z supersedes; next: torch.compile'd chain step (witness 28.7->12.1ms) + re-record
CHECKPOINT ab57df0a (23:18Z) [open] recorded r20260924-223922-5cff @ab57df0a t.total 0.314s art:ad8f92b9 result art:82f70cb9 run-files PRESERVED, verify-po handoff 2305Z; found record script lacked env.sh thread caps (+40ms; fixed, kb ops-tools); next: fused input claims, re-record ~0.27s
CHECKPOINT ab57df0a (22:40Z) [open] recording ab57df0a (depth-1 flatten, merged LK, eq_rows_dot, leaf_q, gate_eval qvals) dev t.total 0.274s; prior recorded c20d 0.529s + 3b51 1.044s preserved; verify-po handoff for 3b51 filed; next: register, new handoff, hill-climb
CHECKPOINT 18ab232e (22:17Z) [open] recorded c20d t.total 0.529s (eq_rows_dot kernel, a8d471ba) art:202f23f1 result art:6aff989d run-files PRESERVED; merged LogUp tables 18ab232e dev 0.378s; negatives on merged circuit running; verify-po handoff for 3b51 written
CHECKPOINT 3c769c6d (21:52Z) [open] cell r20260924-213637-3b51 t.total 1.044s 2^-130.19 art:fe57e68b result, art:30c5bdf7 run-files PRESERVED; next: verify-po handoff, recorded negatives, hill-climb
CHECKPOINT 3e34d97e (21:11Z) [open] fp4-nvf4 A-GKR end-to-end at 64 VUs on 5090: py+rust accept, 2^-130.19, 0.27s; running 4096 dev; next: negatives, recorded research run, register
CHECKPOINT ab9573fd (20:58Z) [open] pod vy-agkr-nvf4 up (5090); bf16 smoke rc=0; gpu/nvf4/circuit.py compiles (418 cols,587 wires,depth3); multi-public chain in prover.py WIP; next: run.py/Rust multi-public, nvf4 witness, bench_result fp4-nvf4
# agkr-nvf4: A-GKR on the RTX 5090 NVFP4 row

## Design (commits 679697a4, 3e34d97e, 3c769c6d on lane/agkr-nvf4)

- `backends/gkr/gpu/nvf4/circuit.py`: the fp4-nvf4 unit = B-Ligero's `relation.compile_fp4_unit(chain=True)` line for
  line, compiled on `GkrCtx` (a `LigeroCtx` subclass): rng -> R<b> LogUp queries (16-bit limb split above 16 bits),
  boolean -> R1, lookups -> native row-listed tables (E2M1X2 256 rows: pair code 16a+b -> (na nb, nz); UE4M3X2 127^2 rows:
  scale pair 128sa+sb -> (ma mb, X, nz); POW19/POW24/RLO/RHI), shifter digits = committed R12 columns + one assertion,
  products = product wires (depth <= 3), every linear constraint keeps LigeroCtx's integer audit.  B-Ligero's pins (the
  verifier's decode) become in-circuit decode from committed operand codes (`_decode`: lookups, `any` via inverse hint,
  `part = any * nz_scale`, `G` = max by a one-hot selector over 5 candidates with range checks).
  Unit: 418 columns, 587 wires, 169 products, 93 assertions, 241 queries.  Epilogue: (s, t, f) + `s` boolean + `t` R8.
- Statement: as agkr-table's BF16 cells, the chain endpoints only (c_0 = 0 via init 0 links, final word public); the
  operand codes are witness.  The final FP32 word is 3 public columns (sign, exponent field, fraction; a 32-bit word is
  not a BabyBear element): new optional `public s t f` line in chain.txt (prover.py Chain.epi_pub, run.py read_chain,
  Rust main.rs/verify.rs; absent -> [y16], unchanged).
- `gpu/nvf4/witness.py`: B-Ligero's device hints (`fp4/hints_device.unit_hints_torch`) step by step over the VUs, the
  decode hints, then the unit's `System.program` over all 24 N units in exact int64 (inverses in the field); CUDA-graphed.
  `check_rows` = every assertion/quadratic on the rows (28 VUs: 0 failures).
- `bench_result.py --relation fp4-nvf4`: frozen NVFP4 set via `fp4/chain.instances_fp4` (digest = contract.NVFP4_INSTANCES_DIGEST
  at 4096), profile NVFP4_SM120, K = 1536 passed to soundness.budget.
- `packed/kernels_triton.py`: Triton 3.4 (5090 pod) rejects `X: tl.constexpr = v` globals -> `X = tl.constexpr(v)`.

## Evidence so far
- dev 4096 VUs on the 5090 (1 rep): t.total 1.087 s, Rust accept 0.19 s, 2^-130.19, contract clean, peak 8.5 GB.
- negatives (14 VUs, all 14 families): 115/115 rejected (54 at the verifier: Rust 54/54 too; 61 at the prover: lookup
  miss / nonzero sum); Rust `mutate` on the honest control 148/148.  4 wrong-rule variants reach the model's word on the
  512 variant VUs (frac26, frac28, negzero, participate-zero-scale: no chain-level negative, as in B-Ligero's gate).
- recorded cells (4096 VUs, 3 reps, 5090, Rust 3/3, 2^-130.19 target and achieved, NON_ZK_PROOF_DIAGNOSTIC, PRESERVED):
  - r20260924-213637-3b51 @ 3c769c6d: t.total 1.044 s; result art:fe57e68b…, run-files art:30c5bdf7….
    verify-po handoff `lanes/verify-po/20260924T2200Z-handoff-from-agkr-nvf4.md`.
  - r20260924-220423-c20d @ a8d471ba (eq_rows_dot: phase-2 vf = Σ_c eq(c) rows[c] as a split-row Triton dot, 110 ms ->
    2.5 ms per layer; same proof bytes as 3b51): t.total 0.529 s; result art:202f23f1…, run-files art:6aff989d….
- hill-climb after c20d (dev, 4096 VUs, warm Triton; t.total):
  - 18ab232e merged LogUp tables (all row-listed tables except E2M1X2 into one tagged table LK, key + tag·2^20): 0.378 s.
  - 285c32cc query values via the gate_eval kernel (CSR over the query lins): 0.356 s.
  - 605b1bbb leaf_q kernel (q-leaves z − Σ β^k v_k in one pass): 0.347 s (build_leaves 22 -> 2.8 ms).
  - ab57df0a `_flatten`: products deeper than MAX_DEPTH commit their deep operand as a column (scope "flat");
    depth 1 -> 485 columns, 654 wires, 2 GKR layers: 0.274 s (depth 2: 0.298 s).  Negatives 115/115 (Rust 54/54,
    mutate 148/148) on the merged and on the depth-1 circuits.
  - r20260924-223922-5cff @ ab57df0a (depth-1 flatten + merged LK + gate_eval + leaf_q): t.total 0.314 s (0.314 / 0.312 /
    0.320); result art:ad8f92b9…, run-files art:82f70cb9…; proofs 9491200 B, sha b6cf5f09….  verify-po handoff
    `lanes/verify-po/20260924T2305Z-handoff-from-agkr-nvf4.md`.  This record is ~40 ms slow for an environmental reason:
    `research run` doesn't source env.sh, so without its thread caps the pools size to nproc 32 under a 13.6-core quota.
    Same tree, same proof sha: 0.314 s by hand without caps, 0.273 s with only the caps exported (Rust 0.19 -> 0.164 s).
    Fixed in `04_record.sh` from 23:20Z; kb ops-tools.md.
- hill-climb after 5cff (dev):
  - fcc9a1e0 add_input_claims (the two input claims of a segment in one rank-1 pass; same bytes): 0.274 -> 0.262 s.
  - e7ffeafe E2M1X2 into LK too (one 2^25 LogUp tree instead of 2^24 + 2^23): 0.262 -> 0.254 s; negatives 115/115 (Rust 54/54,
    mutate 148/148).
  - 2b25df7f numpy serialization (Proof.to_bytes, absorb_exts, Merkle.path; same bytes): 0.254 -> 0.249 s.
- recorded r20260924-233405-1b1d @ 2b25df7f (thread caps on): t.total 0.245 s (0.245 / 0.240 / 0.278), Rust 3/3, 2^-130.19;
  result art:5adf62eb…, run-files art:d6673af2…, PRESERVED; proofs 9467080 B sha 091fecad… (= dev).  verify-po handoff
  `lanes/verify-po/20260924T2350Z-handoff-from-agkr-nvf4.md` (supersedes 2200Z and 2305Z).
  - 1839946c torch.compile'd chain step + one-shot operand decode in `nvf4/witness.py` (graphed witness 28.7 -> 12.1 ms,
    same rows, same sha): 0.249 -> 0.232 s.  Cold compile adds ~200 s to the untimed warm-up (7.5 s warm).
  - 05904fbb..716ea008: agkr-fp8's 12 shared-file prover commits cherry-picked (eq_table_vars, numpy serialization, lookup
    plan, py_ext tolist, incremental eq_points, wire plans, host phase-2 sumchecks, fused input claims, int8 fold skip,
    int32 Acc). Conflicts resolved toward theirs, except that my one-launch gate_eval query path stays first, with their
    planned gather as the fallback.
  - tried and dropped: vectorizing add_lookup_claim's per-query term loop (09_terms.py: only 1.5 ms of its 20 ms is Python).
- recorded r20260925-*-ff98 @ 716ea008 (5 reps, thread caps on): t.total 0.1905 s (0.192 / 0.190 / 0.191 / 0.190 / 0.190),
  Rust 5/5 (0.164 s), 2^-130.19; result art:49757870c9720787…, run-files art:78b3aadf21aabd37…, PRESERVED; proofs 9467080 B
  sha 091fecad… (same bytes as 1b1d).  verify-po handoff `lanes/verify-po/20260925T0005Z-handoff-from-agkr-nvf4.md`.
  - e1bcf472 phase-1 round operands in one pinned non-blocking H2D copy (gkr_packed._inputs; sumcheck_packed.to_dev pinned):
    same sha, t_arith 54.5 -> 51.8 ms, t.total 0.1905 -> 0.1885 s (dev).
- stray runs (not cells): 480e/dbe3/077c/4a1f killed during setup; d2f9 superseded.
- BF16 hopper smoke at 4096 OOMs on the 32 GB part (7.3 GB cupy in the opening; agkr-fp8's 07a8edd6 addresses it); not needed here.
