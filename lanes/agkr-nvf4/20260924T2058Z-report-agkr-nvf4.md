---
lane: agkr-nvf4
kind: report
created: 2026-09-24T20:58Z
status: final
---

CHECKPOINT c97d2ad2 (02:15Z) [final] tip c97d2ad2; cell A-GKR 5090 NVFP4 d098 t.total 0.1388s (~1.4e7x), 2^-130.19, result art:f277786d run-files art:1f0b0b60 PRESERVED; verify-po 0210Z (label held for red-team-lk); pod terminated 02:13Z ~$5.4
CHECKPOINT 00145f51 (01:36Z) [open] dev tip 00145f51 ~0.1431s same bytes ebe7c545 (w via eq_rows_dot, radix4 encoder, fused lookup_mults); record 86d4 @90c21455 0.168s spoiled by host jitter (not preserved); negatives running, re-record next
CHECKPOINT 6d13c3e4 (01:17Z) [open] a4e2 0.1604s preserved (art:dfbc86c4; label held for red-team-lk); handoffs to verify-po/red-team-lk/agkr-fp8 done; took fp8 5034767f+3be6a35f (neutral); open-wq: L2 chunking dropped (slower), testing eq_rows_dot for w
CHECKPOINT 79f00fd3 (00:58Z) [open] a4e2 PRESERVED 0.1604s (art:dfbc86c4, run-files 50f4fe91, 2^-130.19, new stmt BOOL_QUADRATIC+PAIRED; label held per coord 0050Z); verify-po + red-team-lk handoffs 0100Z; dev tip 79f00fd3 ~0.1507s; hill-climbing
CHECKPOINT 57e9e4b (00:42Z) [open] b7cec878: circuit 226->166 queries/unit (bits as products, paired narrow ranges) -> LogUp 2^24; dev t.total 0.1578s, new sha ebe7c545, Rust 5/5, 2^-130.19. Negatives running on pod; then record + verify-po handoff.
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
- hill-climb after ff98 (dev, 5 reps, same bytes sha 091fecad unless stated):
  - 0b7dbb3a LogUp leaves built straight into the ext-table graph's static buffers: t_lookup -1.3 ms.
  - c3982dd5 keep the query tuples across the commitment on >= 30 GB parts when < 1/16 of free memory (driver-free +
    allocator cache; 24 GB cards unchanged): t_lookup 49.0 -> 44.7 ms.
  - c7bfa957 LogUp tree leaf level in one kernel (combine_level_kernel DEINT/T4OUT): t_lookup 44.7 -> 42.0 ms.
  - 9c29e9de build_leaves initialises only the padding: t_lookup 42.0 -> 40.5 ms.
  - 9a17b5b7 add_lookup_claim's pad term in closed form λ(1 - Σ_used eq): t_open_acc 22.5 -> 21.7 ms.
  - 19bda30a scatter_terms grid columns-fastest (L2 reuse of a unit block's eq rows): t_open_acc 21.7 -> 19.2 ms.
  - 024f1cfc gate_eval grid gates-fastest (L2 reuse of a copy block's rows): t_mults 10.0 -> 7.2 ms, t.total ~0.1704 s.
  - 95343488 field.t_ext / t_exts / eq_table point via pinned non-blocking H2D: t.total ~0.1689 s.
  - tried and dropped: rank1_add columns-fastest (open_acc +1.8 ms); logup_ext_ip BLOCK_K / num_warps sweep (128 / 4 is
    the optimum; others spill: 11_lkern.py).
  - b7cec878 circuit: bits as b b = b product wires instead of R1 queries, R3/R5/R6/R7 pairs as one (x + 2^b y, x, y) query
    into PR<b>: 226 -> 166 queries per unit, LK 110613 rows, the LogUp tree 2^25 -> 2^24 leaves; 700 wires, depth 1.
    NEW BYTES: proof 9469288 B sha ebe7c545, 2^-130.19, Rust 5/5; t_lookup 40.5 -> 28.1 ms, t.total ~0.1578 s (dev).
    Negatives on this circuit: python 115/115, Rust 56/56, mutate 148/148.
- recorded r20260925-004238-a4e2 @ b7cec878 (5 reps, thread caps on): t.total 0.1604 s (0.164 / 0.162 / 0.160 / 0.160 /
  0.157), Rust 5/5 (0.153 s), 2^-130.19, validation passed, no contract_problems; result art:dfbc86c4434000c6…, run-files
  art:50f4fe91635eb721…, PRESERVED; proofs 9469288 B sha ebe7c545.  verify-po handoff
  `lanes/verify-po/20260925T0100Z-handoff-from-agkr-nvf4.md`. This is a NEW statement (BOOL_QUADRATIC + PAIRED), so its label
  is held until red-team-lk passes (coordinator 0050Z); rewrite details are in `lanes/red-team-lk/20260925T0100Z-handoff-from-agkr-nvf4.md`.
  Table 2 keeps art:49757870 (0.1905 s, provisional) until then.
- hill-climb after a4e2 (dev, same bytes sha ebe7c545):
  - da4d2b44 opening w / qc serialized once from one D2H numpy array (Opening.raw reused by to_bytes and the transcript), the opened
    columns D2H through pinned memory: t_open_cols 5.9 -> 2.4 ms, to_bytes 5.5 -> 3.8 ms, t.total ~0.152 s.
  - 79f00fd3 phase 1 queues round i+1's challenge-independent operands behind round i's message D2H (event-synced):
    t_arith ~50.4 -> ~49.1 ms, t.total ~0.1507 s.
  - 90e1fe97 / 6d13c3e4: agkr-fp8's 5034767f (key → row map in multiplicities) and 3be6a35f (their keep rule replaces my
    c3982dd5 one; both keep on the 5090). Neutral here: ~0.1515 s.
  - 2f8663f4 opening w = Σ r_i X_i as one eq_rows_dot read of the committed rows (was Limbs8 + int8 GEMM); the transposed
    functional is allocated empty with only its tail zeroed: t_open_wq 17.1 -> 14.5 ms, t.total ~0.1473 s.
  - 90c21455 SIMT encoder radix-4 with two CTAs per SM (15_enc.py: the 70k-row open encode 5.1 -> 3.6 ms, same words), and
    row_code_dot split 64 (4.5 -> 3.9 ms): t_open_wq 14.5 -> 12.5 ms, t_commit 4.85 -> 4.64 ms, t.total ~0.1463 s.
  - 00145f51 kernels.lookup_mults: multiplicities over the key map in one Triton pass (map lookup, compare, int32 atomic
    count, device miss counter, one sync; 16_mults.py: equal counts and misses, 4.9 -> 1.7 ms): t_mults 5.7 -> 3.2 ms,
    t.total ~0.1431 s.
  - tried and dropped: open_w_qc_eval in L2-sized row chunks (14_qcsweep.sh: 32 / 64 / 104 / 160 rows, all ≥ one pass; the
    encode is not DRAM-bound); int32 padded layer inputs (pad_rows): peak -0.26 GB, no time.
- record r20260925-012509-86d4 @ 90c21455: t.total 0.168 s, but reps spread 0.155–0.175 s with t_arith 50–71 ms and Rust
  0.20–0.24 s (pod host jitter). Not a valid best, superseded. Preserved later for pod custody: result art:8c3587e1…,
  run-files art:1efb469a…. It was not yet in the laptop catalog at 02:10Z.
- recorded r20260925-013757-9386 @ 00145f51 (5 reps): t.total 0.1462 s (0.146 / 0.146 / 0.146 / 0.147 / 0.147), Rust 5/5,
  2^-130.19, passed; result art:53a64e8b…, run-files art:9d2f3ba8…, PRESERVED; sha ebe7c545.  Negatives at 00145f51: python
  115/115 (59 at the prover through lookup_mults' miss path), Rust 56/56, mutate 148/148.  verify-po handoff 0150Z.
  - c97d2ad2 _eval_wires via gate_eval CSRs (_wire_csr / _lin_csr) into the int32 wire matrix: t_witness_wires 9.4 -> 3.1 ms,
    t.total ~0.1377 s (dev). Negatives at c97d2ad2: 115/115, Rust 56/56, mutate 148/148.
- **recorded r20260925-015152-d098 @ c97d2ad2 (5 reps, final best)**: t.total 0.1388 s (0.143 / 0.139 / 0.139 / 0.138 / 0.137),
  python 5/5, Rust 5/5 (0.152–0.156 s), 2^-130.19 target and achieved, validation passed, contract_problems none;
  - result art:f277786dadaebbffc3fe01f02e0d49452a7dfc5fceed359cb746588b79eac63c, run-files
    art:1f0b0b60645c02e158c1c8fda975ad04e76e3e18782ee92ee8c26a7247941cad, PRESERVED; proofs 9469288 B, sha ebe7c545.
  - Buckets: witness 15.8 ms, encoding+commitment 4.7, arithmetic 81.3, lookup 32.1, zk 0, serialization 7.3.
  - Overhead ≈ 1.4e7× (same proved FLOPs as art:49757870, whose 0.1905 s renders as 2.5e7×, against 1.283e15 FLOP/s).
  - verify-po handoff `lanes/verify-po/20260925T0210Z-handoff-from-agkr-nvf4.md` (supersedes 0100Z and 0150Z); label held
    for red-team-lk.
- stray runs (not cells): 480e/dbe3/077c/4a1f killed during setup; d2f9 superseded.
- BF16 hopper smoke at 4096 OOMs on the 32 GB part (7.3 GB cupy in the opening; agkr-fp8's 07a8edd6 addresses it); not needed here.

## FINAL
- **tip** lane/agkr-nvf4 @ c97d2ad2 (pushed, clean, `cargo clean` done; no build artifacts on the laptop).
- **known failures**: none open. Rust 5/5 and python 5/5 on every recorded rep; negatives 115/115, Rust 56/56, mutate 148/148
  at the final prover. The 86d4 record was spoiled by host jitter and superseded.
- **pod** vy-agkr-nvf4 (runpod 2s8lyp0325xjqo, RTX 5090): TERMINATED 02:13Z by `research pods drain` (all 8 catalog
  attempts preserved). It ran ~20:43Z–02:13Z, 5.5 h at $0.99/h ≈ $5.4 of the $10 budget.
- **artifacts** (all PRESERVED; the final cell is marked ★):

  | cell / record | attempt | t.total | result art | run-files art |
  |---|---|---|---|---|
  | ★ final cell | d098 | 0.1388 s | f277786d… | 1f0b0b60… |
  | earlier records | 9386 | 0.1462 s | 53a64e8b… | 9d2f3ba8… |
  | | a4e2 | 0.1604 s | dfbc86c4… | 50f4fe91… |
  | | ff98 | 0.1905 s | 49757870… | 78b3aadf… |

  - d098, 9386 and a4e2 share proof bytes (sha ebe7c545) on the BOOL_QUADRATIC + PAIRED statement.
  - ff98 (sha 091fecad) is on the older statement. It is labelled in Table 2 now and marked provisional by the coordinator.
- **The cell** (A-GKR × RTX 5090 NVFP4, K=1536, B=4096, frozen NVFP4 set, NON_ZK_PROOF_DIAGNOSTIC): t.total 0.1388 s,
  ≈ 1.4e7×, soundness 2^-130.19 against a 2^-128 target (both met honestly, no relabel).
  - Independent verification is handed off to verify-po (0210Z). Under the coordinator's 0050Z rule its `verified=accepted`
    label is held until red-team-lk passes BOOL_QUADRATIC + PAIRED (handoff `lanes/red-team-lk/20260925T0100Z-handoff-from-agkr-nvf4.md`),
    on top of the merged LK and the depth-1 flatten.
  - If red-team-lk finds a hole in PAIRED or BOOL_QUADRATIC, the fallback is the provisional ff98 (0.1905 s, older statement).
- **Coordinator decisions**:
  1. Release the label for art:f277786d once verify-po and red-team-lk pass. It supersedes art:49757870 in Table 2.
  2. Merge lane/agkr-nvf4 (shared files touched: gkr_packed, logup, logup_packed, kernels, field, ligero, prover,
     sumcheck_packed, nvf4/circuit). agkr-fp8 has the list in its 0110Z and 0215Z handoffs; keep-rule conflicts are
     resolved toward agkr-fp8's 3be6a35f.
- **kb updated**: fp4-nvf4.md (A-GKR final, rewrites, the 2^24 leaf rule), agkr-gpu-prover.md (NVFP4 5090 section),
  ops-tools.md (setsid nohup on the pod, `pods drain`).
