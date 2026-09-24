# Device-wave inputs (coordinator scratch; collected as lanes finish)

## v3-scout-2 (FINAL 22:47Z; snapshot art:98198cab, 51 cells, all Rust-pinned ACCEPT; pods gone)
- H100/A100: v3 is SLOWER than v1 at each relation's best depth (+22 % fp8-hopper, +15 % bf16-hopper, +9 % bf16-ampere; v3 hint gen
  dominates). 4090 fp8-ada: v3 faster (0.155 vs 0.180 s, open-fixes). Both v1 and v3 are private-operand-safe.
- => Headline per cell = the faster private-safe relation MEASURED IN THE WAVE: run v1 and v3 (and hints-fused-2's fused v3/v3x4 if it
  lands and is byte-identical), >= 3 rounds, alternate order (H100 host noise up to 64 % between rounds).
- Local-coin references (l=16384): H100 fp8 v1 0.119 s @d4 / v3 0.145 @d4; H100 bf16 v1 0.186 @d8 / v3 0.214 @d8;
  A100 bf16-ampere v1 0.309 @d8 / v3 0.337 @d4; 4090 fp8-ada v3 0.155 @d4 / v1 0.180.
- A100: use the chain runner (`run.py --relation bf16-ampere[-v3] bench-vu --pipeline N`), not vu.py (v1-only, sequential, 0.622 s).
- No --batch 32768 (3.2-7.6x slower). Depth 8 allowed where it wins (Table 2 policy said depth <= 2 in the morning; revisit: say depth).

## live-2c (partial 22:38Z)
- tax same-DC 1.07x fp8-ada / 1.13x bf16-hopper; CZ 30 ms 2.6x / 2.95x -> provision verifier in the prover's DC per device.

## hints-fused-2 (partial 22:44Z)
- fused fp8-ada-v3x4 p8 l=4096 0.1103 s / p4 0.1210 s vs fp8-ada-v3 p4 0.155 (4090).

## share-logup-3 (partial 22:44Z)
- fp8-ada 4090 p4: bare 0.158 / +hash 0.373 / +shared 0.253-0.309 (target 1.3x not yet met).

## Open soundness
- H1 (red-team-leaf-3): Rust never binds statement.steps to the relation; Ajtai steps>n collisions accepted by the pinned verifier ->
  ajtai-leaf-3 fixing; red team scoping bare relations. Nothing Ajtai goes in the wave until fixed.

## live-2c FINAL 22:55Z (lane/live-2c 54e748f; $0.94; 44 artifacts on R2; RUNBOOK = its report §6)
- KEPT VERIFIER: vy-live2b-verifier-ro-veritor-campaign pitmqu0zrycw5i, EU-RO-1, tcp://213.173.105.92:56412 (ssh 56411),
  serving live-verifier@80547525ac60. CZ, prover and temp US verifier terminated.
- Tax (bbr, depth 4, 4090): same-DC 1.07x fp8-ada / 1.13x bf16-hopper; 30 ms 2.6x / 2.95x (depth 8: 2.2x / 2.05x); 111 ms 8.4x / 8.8x.
- Rebuild: `research pods sync vy-live2b-verifier-ro --dest /workspace/lv-src-<sha>` + `research pods ssh ... -- 'bash
  /workspace/lv-src-<sha>/backends/direct/ligero/live_serve.sh'` (~80 s). MERGE lane/live-2c (live_serve.sh) into integration first.
  Do not restart under ligerito-relation-2's sessions (~23:00-23:20Z).
- POLICY for the wave (user decision 05:39Z = live verifier, interactive ZK): provision provers in EU-RO-1 where the GPU type exists
  (same-DC tax ~1.1x) and headline t.total_live from a live same-DC run, with the local-coins t.total of the same pod/tree beside it as
  the prover-only number; where the GPU is only available cross-region, add a CPU verifier pod in that DC (live_serve.sh on a bare pod
  is tested) rather than quoting a 2.6-8.8x cross-region number. Record RTT + both DCs per cell.

## red-team-leaf-3 FINAL 22:55Z (lane/red-team-leaf-3 89cd6cf7; fixtures in its evidence/, 42 MB)
- H1 BREAK (Ajtai n64/n128 steps > n collisions, accepted pinned, also on ajtai-leaf-3 47d191e2) + H2 BLOCKING (no pin fixes steps
  for ANY relation) -> ajtai-leaf-3 owns the generic shared fix (handoff 2258Z). BEFORE THE WAVE: integration must contain it, and
  every Table 2 cell is re-verified with the steps-pinned binary (no re-measurement needed if honest proofs still accept).
- G1 FIXED on ajtai-leaf-3; F5/F7/F8 FIXED; G3 PARTIAL (share-logup-3 owns); BLAKE3 framing, share pair negatives, leaf-iface OK.
- Table 1 lines (Poseidon2 / BLAKE3 / Ajtai) in its report.

## blake3-leaf-3 FINAL 22:59Z (lane/blake3-leaf-3 820aa6f = 1db0008 + cherry-pick 1cf9178 + level-scheduled interpreter; $0.50)
- 4090 4096 VUs local: fp8-ada bare 0.170 / +hash 0.421 / +blake3 5.22 s p4 (best 4.70 l=4096 p2); bf16-hopper 0.261 / 0.805 / 10.70.
  Rows/unit 3769 / 6210 / 35370. BLAKE3 = ~12x Poseidon2 in-circuit -> DRILL-DOWN ONLY (one 4090 fp8-ada cell), not a wave column.
- l=16384 does not fit +blake3 on 24 GB; next bottleneck constraint tests 2.74 s of 4.70.
- 820aa6f level-scheduled witness interpreter (LIGERO_INTERP_LEVELS=0 = old path; byte-identical): CHECK at integration whether
  +hash / +ajtai use the same interpreter path -> if so re-measure them, it may cut their commit time too.
- +shared: share-logup-3 accepts only Poseidon2.
- H2 canonical steps for +blake3 relations not listed (lane finished 1 min after the handoff) -> take from the relation specs at integration.

## ajtai-leaf-3 FINAL 23:05Z (lane/ajtai-leaf-3 47d191e, $0.59, pod gone) -- did NOT do H1/H2 (missed both handoffs)
- G1 fixed (Rust 8768997 + Python/fixture 62e3fde; verifier-only, no re-pin). Gates 0 failures; Rust pinned 13/13, 25/25.
- 4090 l=16384 local: fp8-ada p4 bare 0.215 / +hash 0.448 / +ajtai-n64 0.447; bf16-hopper p3 bare 0.329 / +hash 0.823 / +ajtai-n128
  1.407 (p4 OOM: hash_hints, ~10 GB per-stream graph pools). Ajtai = Poseidon2 on fp8; 1.7x on bf16. Artifacts art:a0dc1a4b, b6b526d4,
  355f5334, c1f6c5e7, 2f731699 (file trees, not attempts: `research fetch --all` copied 4 KB of a 1.2 GB run).
- H1/H2 -> NEW lane steps-pin bd486635 (base 47d191e; FINAL 00:45Z): audit all statement fields, bind in shared pin table, negatives,
  honest re-accepts, entries for other branches. INTEGRATION WAITS FOR IT; Ajtai stays out of the wave until merged.

## hints-fused-2 FINAL 23:05Z (lane/hints-fused-2 4287a92, code = e57637f; $0.58; 10 artifacts on R2; pod gone)
- Fused hint kernel is the DEFAULT on this branch (`LIGERO_FUSED_HINTS=0` = old torch CUDA-graph path); byte-identical 82/82 across
  all 16 v2/v3 relations; no system/statement/transcript/pin change. Bench knob `LIGERO_REFERENCE_HINTS=0` skips warm-up reference check.
- 4090, 4096 VUs, local coins: fp8-ada-v3x4 p4 l=4096 0.114 s (4.12 GiB) vs fp8-ada-v3 p4 l=16384 0.1715 (torch) / 0.1405 (fused);
  bf16-hopper-v3x4 p4 l=4096 0.2014 vs bf16-hopper-v3 fused 0.2248; fp8-hopper-v3x4 p4 l=4096 0.1043 vs v3 fused 0.1511.
- => DEVICE WAVE candidates per cell (all private-safe): v1 @ best depth (l=16384), v3 fused (l=16384), v3x4 fused (l=4096, p4 and p8).
  v3-scout-2's "v3 slower than v1 on H100/A100" used the torch hint path -> superseded; re-measure there.
- Next bottleneck: witness-program kernel 30 % (serial per column, 7090 rows) -> row-parallel / fold hints into it; then Merkle BLAKE3
  13 %, quadratic test 12 %, RS 10 %. The 820aa6f level-scheduled interpreter (blake3-leaf-3) is the same idea -> check overlap.
- CHECKED 23:12Z: 820aa6f changes the GENERIC witness interpreter in backends/direct/ligero/witness_device.py (level-scheduled, default
  on, falls back to sequential unless every row has one writer and no read-before-write). That is very likely the "witness-program
  kernel, serial per column" hints-fused-2 names as the 30 % bottleneck. merge-val-3 MUST A/B v3x4-fused l=4096 p4 and v1 p4 with
  LIGERO_INTERP_LEVELS=1 vs 0 on the integrated tree (and report whether the level path is actually taken for bare relations).

## share-logup-3 FINAL 23:11Z (lane/share-logup-3 453d7cf4; $0.68; 23 arts remote=1; pod gone)
- 4090, 4096 VUs, l=16384, p4, interactive NON-ZK local coins: shared/bare fp8-ada 0.268/0.159 = 1.69x (target 1.3x missed;
  device floor 0.213 s/pass > 0.205 needed); fp8-hopper 0.308/0.136 = 2.27x (noisy 3 reps); bf16-hopper 0.512/0.256 = 2.0x;
  bf16-ampere 0.480/0.262 = 1.83x. Unshared +hash same pod: 0.373 / 0.355 / 0.774 / 0.744 -> shared beats +hash by 14-38 %.
- Rust pins for all four +shared relations accept every dump; gates 0 failures. bf16 graph re-capture fix (2.84 -> 0.51 s).
- NOT WAVE-READY: no ZK run, and G3 (coins_h prover-sampled) blocks a live verifier. Launched `shared-live` 297f7c16 at 23:15Z
  (base 453d7cf4; G3 fix + --zk + local/live bare-vs-shared table; FINAL 00:45Z). Column 2 headline = +shared if shared-live lands
  with live accepts, else +hash (unshared Poseidon2) as tonight.

## fp4-decode-3 FINAL 23:17Z (lane/fp4-decode-3 6ffa035; ~$1.2; 68 arts remote=1; both pods gone)
- 5090 COLUMN 2 EXISTS NOW: fp4-nvf4+poseidon2 (pins as fp4-nvf4+hash sys 8c6d260c). 4096 VUs, l=16384, --zk interactive, LOCAL
  coins, p4: bare 0.0576 s / hashed 0.2038 s (3.54x; 6-run spread 0.058-0.067 / 0.204-0.234). 4090 p4: 0.0532 / 0.2617 (4.92x).
  Pinned Rust batch 7/7 on all 18 dumps (2^-128.54), gates 0 failures, cargo 48/48.
- 6ffa035: sm_120 cold compile of the fused witness kernel 449.6 s -> 46.2 s via sm_89 PTX JIT (bit-identical differential test;
  LIGERO_WITNESS_PTX_ARCH=native restores). Needed on every fresh 5090 in the wave.
- Table 2 5090 cells come from the device wave (same-DC live, p4), not from these local-coin runs; 0.0576 is the expectation.
- Integration: needs 6ffa035; steps-pin writes the fp4-nvf4+poseidon2 steps entry from this branch.

## 01:00Z bench-summary (935b8eb9): phase-sum contract vs pipelined runs
- `lane/bench-summary @ fd2971e8` adds `python -m verity_numerical.bench.summary PATH...`, one row per result with a `contract`
  column from `tables.phases`. Merge it at integration; the wave brief names it for every lane.
- It flagged ajtai-leaf-3's `r20260923-223427-9bab` (`p4/bench/bare`, fp8-ada 4090, `--pipeline 4`, t.total 0.2153 s): the
  phase buckets add up to 2.2 % more than t.total, so the canonical tables would reject the row. Overlapping phases under
  pipelining are the likely cause. BEFORE the wave: run the helper over one pipelined cell per relation and confirm headline
  cells pass the contract. If they don't, fix the bucket rule for pipelined runs at merge-val-3, not per lane.

- 05:00Z REVERSED: the frozen table contract (tables.py, backends/AGENTS.md "Canonical tables", user-frozen 2026-09-22) says
  buckets are disjoint and sum to t.total within tolerance, and the renderer rejects such rows (art:7e796fb9 rejected). A
  flagged row is drill-down, not a Table 2 cell, until the fused path's phase attribution is fixed. Also contract-invalid for
  Table 2: `included-hash-shared` (not a column; the column is Poseidon2 included-hash, sharing none), l=4096 v3x4 runs
  whose instance manifest differs from the frozen set (art:fb4934af), and t.total_live as the headline (the cell is t.total).
  Headline tables = `python -m verity_numerical.bench.tables --root ~/.research/store` output ONLY; never hand-built.
- 05:05Z USER DECISION: keep the frozen "B-Ligero + in-proof hash" column (Poseidon2, sharing none). Shared 64x64 tile =
  drill-down only. Supersedes the 01:05Z "column 2 = +shared tile64" entry below.
- (superseded) 04:40Z DECISION (wave-4090-2 handoff 0410Z, wave-h100-2 r1): a phase-sum "1 problem" does NOT disqualify a row when it is
  the only problem. Pipelined runs report t.total = the pass wall clock (`relchain._pipelined` returns `wall`), and a
  sub-batch's clock stops only after its openings reach the host (protocol.py ~1704-1718), so no GPU work falls outside
  t.total; the buckets add per-sub-batch stages that overlap at depth >= 4 (seen only on fused v3/v3x4: 1.3-3.8 % on the
  4090, 8 % on one H100 round). Table 2: headline = median round as measured, flag footnoted ("phase buckets overlap under
  pipelining; wall clock unaffected"), contract-clean alternative beside it (4090 v3x4 p4 live 0.1020; H100 v3x4 p4 0.1174).
  POST-WAVE fix: the contract skips or rescales the phase-sum check when the result records pipeline depth > 1.

## 01:05Z shared-live-2 FINAL (432ea740): column 2 = +shared tile64
- `lane/shared-live @ e2a3b27e` (share-logup-3 + live-2c + G3 fix fe0c4f48): merge as one unit. 4090, `--zk --mode interactive
  --pipeline 4`, 4096 VUs, l=16384, 5 reps: fp8-ada local 0.246 / 0.389 s (1.58x), live 0.380 / 0.669 (1.76x); bf16-hopper local
  0.371 / 0.695 (1.87x), live 1.065 / 1.326 (1.25x). 30/30 campaign sessions + 12/12 dumps accepted (pinned Rust), G3 negative
  rejected 0/13, 23 artifacts preserved (finish check ok).
- Caveat: live verifier was on the SAME pod (localhost, CPU contention), so live ratios are not the wave's same-DC numbers.
- DECISION: Table 2 column 2 = `--auth included-hash-shared --tile 64x64`; unshared +hash = drill-down.

## 01:15Z ligerito-relation-3 FINAL (9ef1073b): Ligerito = diagnostic column, not a ZK headline
- `lane/ligerito-relation-2 @ 498f9014` (pushed). `--zk` emits LGSC0004; ZK keys pinned by derivation (verify-rs-4 `0e4ef1d1`
  accepts all dumps without --allow-any-key); R3-7 / R3-10 / R3-2 / R3-8 closed; gates 10/10, 0 failures.
- LABEL stays NON_ZK_PROOF_DIAGNOSTIC: no PCS ZK argument yet for the V1 zero claims and LGSC0004's sparse claims (red-team
  checklist item 5). So Table 2 gets Ligerito only as a labelled drill-down / proof-size column, not as a ZK cell.
- 4090 fp8-ada 4096 VUs, one batch (12-coin schedule, 6dda159a): local non-ZK 0.594 s / 701,728 B; local "ZK" 0.823 s /
  916,527 B; FS ZK 0.846 s; live ZK on RO 3.365 s (54 ms RTT x 42 rounds), session 2^-128.43; Rust verify 0.43-0.49 s.
  Compare Ligero bare ZK 0.246 s / 66.1 MB on the same GPU class: Ligerito is ~72x smaller proofs, ~3.3x slower prover.
- LIGERITO SECOND PASS (after integration ff main, ~03:00Z): new lane merges `lane/ligerito-relation-2 @ 498f9014` +
  `lane/ligerito-sumcheck-3 @ 58e76e5d` (11-coin default; merge-tree with 6dda159a reported clean) + `lane/verify-rs-3` @
  verify-rs-5's tip onto main; GPU gate rerun at 11 coins; Rust tests; one fp8-ada 4096 bench. Also retarget
  `redteam_live_labels.py` (it tests a helper verify-session no longer uses; prints "1 accepted" spuriously).
