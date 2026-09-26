---
lane: red-team-flock-2
kind: report
created: 2026-09-26T02:33Z
status: open
---

CHECKPOINT a57628fc (13:35Z) [open] reopened (NOT final): pod 2qmpx34ou36cu5 (vy-red-team-flock-2, cpu5c-8) created 13:35Z after 15 min without a reply to REOPENED 1318Z; elementwise pins review: pins regenerate, IR = units+tail on all 5 lowerings, 37 cell files checked, placement holds; next: selftests + tampers at a8ce768a
CHECKPOINT a57628fc (13:15Z) [open] reopened for flock-l40s-101's six new elementwise pins (1309Z request, branch cursor/flock-elementwise-workloads-a420 @ a8ce768a): NOT final; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241
CHECKPOINT a57628fc (10:55Z) [final] FINAL red-team-flock-2 (bc-089339bc-4846-55b6-96c9-a15fd7a4a241). (1) IR6 MET at 2f55d2d3 and f4cd5d4e: leaf maps, row key and 16-bit words pinned with the netlist and checked at load (runs r20260926-100601-f937, r20260926-102516-ea1e, r20260926-104438-71ff; selftests 82/82; all tampers refused, including [n,32] ports and a widened returned port; LEAVES meaning rests on IR2's pin). (2) L40S #101 elementwise cells art:dc9b92f6 (RoPE), 6dc1f392 (SiLU mul), d1ae527d (RMSNorm fused), 1e7cdc41 (RMSNorm Triton) labelled NON_ZK_PROOF (30 verifier files checked). (3) NVFP4 5090 cells art:2753a371 (Fp4) and db7f48de (ShaFp4): proof_class NON_ZK_PROOF, final (14 files recomputed from the set with core only; red-team-flock placement ruling and verify-flock-pure replay cited). Earlier today: flock-ir-sampling/v1 GRANTED WITH CONDITIONS (S1, IR2), art:a330c568 and 26b5f7d8 labelled. Handoffs 1010Z, 1025Z, 1055Z. No verity commits (review-only). Pods x5f12wbrstpco1 and l5aqabzzjo9g9k terminated; spend about $0.40 today ($0.12 this turn).
CHECKPOINT a57628fc (10:54Z) [final] FINAL red-team-flock-2 (bc-089339bc-4846-55b6-96c9-a15fd7a4a241). (1) IR6 MET at 2f55d2d3 and f4cd5d4e: leaf maps, row key and 16-bit words pinned with the netlist and checked at load (runs r20260926-100601-f937, r20260926-102516-ea1e, r20260926-104438-71ff; selftests 82/82; all tampers refused, including [n,32] ports and a widened returned port; LEAVES meaning rests on IR2's pin). (2) L40S #101 elementwise cells art:dc9b92f6 (RoPE), 6dc1f392 (SiLU mul), d1ae527d (RMSNorm fused), 1e7cdc41 (RMSNorm Triton) labelled NON_ZK_PROOF (30 verifier files checked). (3) NVFP4 5090 cells art:2753a371 (Fp4) and db7f48de (ShaFp4): proof_class NON_ZK_PROOF, final (14 files recomputed from the set with core only; red-team-flock placement ruling and verify-flock-pure replay cited). Earlier today: flock-ir-sampling/v1 GRANTED WITH CONDITIONS (S1, IR2), art:a330c568 and 26b5f7d8 labelled. Handoffs 1010Z, 1025Z, 1055Z. Pods x5f12wbrstpco1 and l5aqabzzjo9g9k terminated; spend about $0.40 today ($0.12 this turn).
CHECKPOINT a57628fc (10:26Z) [open] WAITING r20260926-102516-ea1e on vy-red-team-flock-2 (l5aqabzzjo9g9k, cpu3c-8), check after 10:45Z; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241; IR6 at f4cd5d4e + explicit 16-bit tampers; then the same tampers at 2f55d2d3 (SKIP_SELFTEST), addendum handoff, FINAL. L40S cells and NVFP4 5090 cells already labelled NON_ZK_PROOF (NVFP4 finding updated with red-team-flock's placement ruling and verify-flock-pure's replay)
CHECKPOINT a57628fc (10:20Z) [open] IR6 MET at 2f55d2d3 (r20260926-100601-f937); L40S #101 elementwise cells dc9b92f6/6dc1f392/d1ae527d/1e7cdc41 and NVFP4 5090 cells 2753a371/db7f48de labelled NON_ZK_PROOF; flock-ir-sampling/v1 GRANTED WITH CONDITIONS (1010Z). Handoffs 1010Z, 1025Z. Pod x5f12wbrstpco1 terminated (~$0.26). Queue empty; idle until woken
CHECKPOINT a57628fc (10:08Z) [open] flock-ir-sampling/v1 GRANTED WITH CONDITIONS (S1 native check mandatory, IR2) at NON_ZK_PROOF; art:a330c568 + art:26b5f7d8 labelled; handoff lanes/flock-ir-sampling/20260926T1010Z (+coordinator copy). WAITING r20260926-100601-f937 (IR6 confirm at 2f55d2d3) on vy-red-team-flock-2, check after 10:20Z; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241; next: NVFP4 5090 cells statement checks
CHECKPOINT a57628fc (09:55Z) [open] WAITING r20260926-095238-19c8 on vy-red-team-flock-2 (x5f12wbrstpco1), check after 10:12Z; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241; flock-ir-sampling: 32 captured rows clean word-for-word, lane netlist clean on 200k adversarial lanes; verdict drafted (GRANTED WITH CONDITIONS, S1 native check mandatory); next: pod negatives -> labels -> handoff. Queued: flock-backend 0945Z NVFP4 5090 cells, flock-ir-lowering 0922Z attention-head, 0832Z IR6 confirm
CHECKPOINT a57628fc (09:50Z) [open] WAITING r20260926-094944-2a2a on vy-red-team-flock-2 (x5f12wbrstpco1, cpu3c-16), check after 10:15Z; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241; flock-ir-sampling review: all 32 captured rows (both cells' verifier files, byte-identical) recomputed word-for-word from the IR primitives, clean; next: pod negatives, verdict, labels, handoff. Queued: flock-ir-lowering 0922Z attention-head, 0832Z IR6 confirm
CHECKPOINT a57628fc (09:27Z) [open] woken 09:27Z: review GumbelTopPTokenSelect on C-Flock (ir_sampling.rs vs frame v2); cells L40S art:a330c568, H100 art:26b5f7d8; budget $2; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241
CHECKPOINT a57628fc (07:51Z) [open] IR4/IR5 MET; flock-ir-frame/v2 @c53d9148 GRANTED W/ CONDITIONS (IR2 mandatory, IR6 hardening); cells art:dd27fdab 8a07b80f 9563d2c8 63553a6c labelled NON_ZK_PROOF; art:572efe9e; pods terminated; IDLE until woken; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241
CHECKPOINT a57628fc (07:36Z) [open] IR4/IR5 + frame/v2 review: cells' verifier-staged statements check out (wiring/out_leaf = IR leaf maps, 0 diffs; roots recomputed); silu x2 unit 0/1.06M; RMSNorm pins = granted rows + CUT. Pod run next (IR5 tail, IR4 tampers, frame negatives)
CHECKPOINT a57628fc (07:24Z) [open] woken 07:23Z: IR4/IR5 @b4e05b48 + IR3 flock-ir-frame/v2 @c53d9148 (frame-v3 keyed-BLAKE3 binding; cells dd27fdab 8a07b80f 9563d2c8 63553a6c); agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241
CHECKPOINT a57628fc (05:41Z) [open] RMSNorm fused+Triton @34d02ae3 GRANTED W/ CONDITIONS (relation-only); IR1/IR2 MET; new IR4 (cut structure unpinned: eps forgery accepted) + IR5 (tail add/mul 2-NaN); rope/silu v2 byte-identical; art:3591d6ef; labels art:7342c52d/44d7c8d0/a4f38fc0; pods terminated; IDLE until woken; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241
CHECKPOINT a57628fc (05:18Z) [open] RMSNorm review @34d02ae3: rope/silu v2 rows byte-identical (2eaa652f/3b1ed294); fused units 0/7680 lanes vs IR on 240 adversarial rows (VM); tail_program == IR cut words; IR4 candidate (Rust tail not pinned; eps forgery built). Pod run next: tail prims, triton, loadchecks, tampers
CHECKPOINT a57628fc (05:03Z) [open] woken 05:03Z: review RMSNorm (fused CUDA + Triton) + IR1/IR2 fix @34d02ae3 (PR #54); rope/silu v2 byte-identity; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241
CHECKPOINT a57628fc (04:48Z) [open] PR54 rope/silu GRANTED W/ CONDITIONS (IR1 cut tail, IR2 own staging, IR3 no cell) art:f29e8ac5 art:07f51904; NV5 MET, NVFP4 NV1-5 all met art:562868e6 (handoff 0451Z to flock-backend); pod-create.sh fixed; pods terminated ~$0.5 lane total. Next: RMSNorm 0435Z review; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241
CHECKPOINT a57628fc (04:38Z) [open] PR54 rope/silu @366befc4: fidelity 0/2.03M rope + 0/2.16M silu (my evaluator), statement negatives 10/10 refused (r20260926-043318-28bb); rope/silu identical at 76b7cbb2. Next: NV5 confirm @e4f631bd (NVFP4) + 76b7cbb2 regression on qlqy5nyrjkzjer. Inbox: RMSNorm request 0435Z queued
CHECKPOINT a57628fc (04:15Z) [open] started flock-ir-lowering 0407Z review (PR #54 RoPE rope-head + SiLU-mul templates @366befc4); also fixing my pod-create helper (registration failure vs no stock); agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241
CHECKPOINT a57628fc (04:14Z) [open] inbox: flock-ir-lowering 0407Z review request (RoPE rope-head + SiLU-mul C-Flock templates) queued as next item-3 review, not started this turn (turn was the NV re-review); start on wake; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241
CHECKPOINT a57628fc (04:14Z) [open] NV1-NV3 MET @45fdab2d, merge-ready; NVFP4 still GRANTED W/ CONDITIONS + new NV5 (pin y-leaf schema/width; G4 accepted in r20260926-040359-a5da art:ac3dac64); fp8 y<<10 HOLDS; fp4-only schema hash harmless. finding labels art:f1ee8a75 art:24fbc96d. Handoff 0415Z to flock-backend. Pods terminated ~$0.3 total. IDLE
CHECKPOINT a57628fc (04:04Z) [open] re-review NV1-NV3 @45fdab2d: paper OK (admit before coin; fp8 y<<10 = B-Ligero unpack_public, y<2^22; fp4 digest schema = layout constant). Candidate G4: y-tree schema/width unpinned. Run r20260926-040359-a5da on vy-red-team-flock-2 (n3uvndljkccdje A5000; 3 stray CPU pods created+terminated in ~2 min)
CHECKPOINT a57628fc (03:46Z) [open] woken 03:46Z: re-review NV1-NV3 at 45fdab2d (flock-gpu-link 0335Z request); focus fp8 y<<10 check + NVFP4-only schema in statement digest; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241
CHECKPOINT a57628fc (03:08Z) [open] NVFP4 Fp4/ShaFp4 @0bb25e8a GRANTED WITH CONDITIONS NV1-NV3 (+PB1-4, FA1) at NON_ZK_PROOF, handoff 0310Z (art:cf130873, art:206b74f5); wgmma pin 12c3c8d3 pre-checked. Pods terminated, ~$0.08. IDLE: waiting for NV1-NV3 + 5090 cells to label, row-sharing statement, flock-backend statements; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241
CHECKPOINT a57628fc (03:04Z) [open] NVFP4 Fp4/ShaFp4 @7b3ba797 (=0bb25e8a verifier): producer selftest 15/15 + 13/13 at 8/64 on my gen_fp4 files, 12/12 rtf2 negatives refused (art:cf130873); gaps G1 relabel, G2 fp4-netlist-under-Fp8, G3 out!=y ACCEPTED. Now r20260926-030235-8637 (dummy blocks, 12/40 VUs); wgmma pin 12c3c8d3 0/129,571
CHECKPOINT a57628fc (02:54Z) [open] WAITING r20260926-025249-6192 on vy-red-team-flock-2 (pkkkgds4e8unxt, A4000 as CPU box: no CPU stock), check after 03:25Z; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241; next: NVFP4 Fp4/ShaFp4 @7b3ba797 selftests on my gen_fp4 files + 12 rtf2 negatives + 3 gap demos (out!=y, schema relabel, fp4 netlist under Fp8)
CHECKPOINT a57628fc (02:37Z) [open] NVFP4 layout landed unhanded at flock-gpu-link 7b3ba797 (Fp4 blake3-keyed/row-nvfp4/v1 + ShaFp4 sha256/row-nvfp4/v1); starting paper review of diff vs 758a8edf. Also queued: flock-backend bf16-hopper-wgmma pin 12c3c8d3 (a9d13f68) pre-check. No pods.
CHECKPOINT a57628fc (02:33Z) [open] started; agent bc-089339bc-4846-55b6-96c9-a15fd7a4a241; scope: NVFP4 row-nvfp4 layout from flock-gpu-link + new flock-backend statements (incl. future row-sharing); red-team-flock keeps Chunk(n) item 1; reading contract + red-team-flock baseline; inbox: nothing new

# NVFP4 block layouts, Fp4 and ShaFp4 (02:35–03:10Z)

**GRANTED WITH CONDITIONS at NON_ZK_PROOF** for `verity/flock-pure-block/v2` layouts `Fp4` (`blake3-keyed/row-nvfp4/v1`) and
`ShaFp4` (`sha256/row-nvfp4/v1`) at `cursor/flock-gpu-link-797a` @ 0bb25e8a. 0bb25e8a is 7b3ba797 plus a one-line GPU
prover fix in `gpu.rs`, so the verifier and statement are the ones I attacked at 7b3ba797. This closes red-team-flock's FP2.
FP1 is met: PINS["fp4-nvf4"] = fb52a87c on flock-backend c058c33f, and I regenerated the netlist to the pin.

Handoffs acted on: flock-gpu-link's 02:35Z, 02:53Z and 02:58Z notes to `lanes/red-team-flock/` (NVFP4 is this lane's queue
item 2). Verdict: `lanes/coordinator/20260926T0310Z-handoff-from-red-team-flock-2.md`, copied to `lanes/flock-gpu-link/`,
`lanes/flock-backend/` and `lanes/red-team-flock/`.

## Paper review (`pure_block.rs`, `flock-pure-gpu.rs` diff 758a8edf..7b3ba797): HOLDS

- **Fp4 BLAKE3 chain.** Per role, slots 0–13: block 0 takes the role key as a Δ constant; blocks j ≥ 1 copy `out_lo` of
  j − 1; counter 0 and T_HI 0 are constants. Block 13 has block_len 32 and flags KEYED_HASH | CHUNK_END | ROOT, and message
  words 8–15 are constant 0. That is the single-chunk keyed BLAKE3 of 864 bytes, and `out_lo` (column 256 = `OUT_LO_BASE`)
  of slots 13 and 27 is the digest itself. `chunk::tree` returns a lone chaining value unchanged, so ROOT has to be in the
  circuit, and it is.
- **ShaFp4 chain.** H_in(0) is the midstate after `sha_prefix_nvfp4(role, 1536)` = `rowleaf.sha256_row_nvfp4_prefix`.
  Blocks 0–12 are row bytes. In block 13, words 0–7 are row bytes 832–863 (witness), and words 8–15 are constants
  0x80000000, zeros, and 7,424 = 928 × 8.
- **Units.** Unit u at 2^13 position 56 + u (Fp4) or 112 + u (ShaFp4), with no overlap with the compressions. Its code
  operands copy message half-block u % 2 of block u / 2. Its scales (x at bits 544–575, W at 576–607, matching the
  lowering's x, w, c, sx, sw order) copy message word u % 16 of block 12 + u / 16, which is row bytes 768 + 4u to 771 + 4u:
  little-endian bits for BLAKE3 (`M_BASE` + 32w + b) and big-endian for SHA-256. c_in(0) is forced to +0. AccOut is unit
  23's c_out (word 59), opened against `inst.out[v]`.
- **Publics and regions.** `n_cv` = 0; the regions are Digest(x), Digest(y) and AccOut, each at the verifier's own values.
  The two words per block the prover still sends (y16, acc) feed no region.
- **Dummy blocks.** Zero rows under the key, a zero-input unit chain (scale 0x00 makes no group participate, so +0), and
  digests equal to the keyed hash or SHA-256 of 864 zero bytes. Both the witness and `dummy_cv` use the same per-slot
  constants.
- **Statement digest.** It adds an fp4 layout tag, and Δ includes the 64 scale copies per unit. Every other layout's Δ is
  byte-identical to 758a8edf: `blen`/`flags` reduce to the old constants, `last_data_words` is 16 (no-op) for BLAKE3 and 0
  for SHA, and the tail handling in `sha_state` / `sha_compressions` is empty for whole-block rows. **red-team-flock's
  Chunk(n) reviews at 758a8edf carry over to 7b3ba797 / 0bb25e8a unchanged.**
- **Bound.** Fast100 schedules are embedded for m = 22 to 35, and `prover_config_for` is strict. So Fp4 covers up to 32,768
  VUs per proof (m = 20 + nbl) and ShaFp4 up to 16,384 (21 + nbl). The 5090 line (Fp4 at 8,192 VUs, ShaFp4 at 4,096) is
  m = 33: 2^-97.77 per rep, **2^-195.54 per proof** (red-team-flock's per-m reproduction), and the region claims add about
  2^-243. Batches over one proof are a union.

## Evidence

My own instance writer, `evidence/gen_fp4.py`, uses `verity.commitments` (rowleaf NVFP4, merkle) and
`BLACKWELL_SM120_NVF4.step_scaled`, and nothing from the producers' writers. Scales vary per 16-code group, 3% of them
are zero, and VU 0 has three zero-code groups with scale 0x38. My harness, `evidence/rtf2_patch.py`, is prover-side only:
PureVerifier and `pure_block.rs` are untouched. Pod scripts are in `evidence/pod-scripts/10-fp4-layout.sh` and
`20-fp4-dummies.sh`.

- **Run r20260926-025249-6192 (art:cf130873), source 7b3ba797, CPU build:**
  - **The producer's selftest on my files:** Fp4 15/15 at 8 VUs (m 23) and 64 VUs (m 26); ShaFp4 13/13 at 8 (m 24) and 64
    (m 27). The honest proofs verify against roots computed by the reference, not by the Rust code. So the Rust NVFP4
    prefix, digests and trees match the reference, and the wiring matches the model on inputs where a permuted scale
    would change the output.
  - **My 12 negatives: all refused, both reps.**

| case | layout | refused by |
|---|---|---|
| `fp4_root_flag_dropped` (block 13 without ROOT) | Fp4 | lincheck |
| `fp4_tail_word_nonzero` (block 13 word 8 = 1) | Fp4 | lincheck |
| `fp4_scale_block_forged_digest_only` (block 12 scale bit flipped, chain recomputed, unit reads it; output unchanged) | Fp4 | Digest region claim (`RingSwitch(ClaimMismatch)`) |
| `fp4_x_scale_operand_free_u5` / `_u20` / `fp4_w_scale_operand_free_u7` (a scale operand flipped without the row; the unit's c_out is unchanged, checked) | Fp4 | lincheck (the Δ scale copy) |
| the same three | ShaFp4 | lincheck |
| `sha_fp4_pad_marker_dropped` (block 13 word 8 without 0x80) | ShaFp4 | lincheck |
| `sha_fp4_last_block_data_forged` (block 13 word 3, unit 19's scales) | ShaFp4 | lincheck |
| `sha_fp4_scale_block_forged` (block 12 scale byte, chain recomputed) | ShaFp4 | lincheck |

- **Run r20260926-030235-8637 (art:206b74f5), source 0bb25e8a:** at 12 VUs (16 blocks, 4 of them dummy) and 40 VUs (64 blocks, 24 dummy), Fp4 passes 15/15 (m 24, 26) and ShaFp4 13/13 (m 25, 27). A forged dummy-block message is refused on both reps in both layouts (`fp4_dummy_block_forged`, `sha_fp4_dummy_block_forged`, both by lincheck).
- **bf16-hopper-wgmma (flock-backend a9d13f68, pre-review, not yet handed to me):** the netlist regenerates to
  12c3c8d3, and its rows are byte-identical to bf16-hopper's da1bbe2c; only the relation name in the header differs. My
  `evidence/diff_wgmma.py` found 129,571 finite units with 0 mismatches between tc_dot_total(HOPPER_BF16_WGMMA_K16) and
  HOPPER_BF16_M16N8K16. Separately, 1.2 M finite f32 words showed 0 mismatches between F2fpBf16 and f32_to_bf16. So an H100
  wgmma Chunk(n) statement inherits the bf16-hopper unit's grant.

## Gaps (each demonstrated by an accepted proof; none can be reached by a cheating prover against an honest verifier file)

- **G3: `out` is not tied to the y root (all flock-pure-block layouts, not only NVFP4).** The AccOut and Y regions open
  `inst.out[v]`, while `commit()` builds the y root from `inst.y[v]`, and nothing compares the two. With y[0] ^= 1 and the
  y root recomputed, an honest proof is **accepted** on Fp4 and on ShaFp4. So the committed output isn't the verified one.
  red-team-flock's grants checked the output against `inst.out` only (flock-vllm-v1's verifier does check its y root).
- **G2: an fp4 netlist under a non-fp4 layout leaves the scales free.** `Layout::of` looks only at (row_bytes, units), and
  nothing ties `net.n_in == 608` to `Layout::is_fp4()`. A file with relation fp4-nvf4, 1536-byte rows and 48 units builds
  Layout::Fp8. Unit rows 544–607 stay unconstrained input rows. I built two files with identical a and b roots and outputs
  434fc000 and 444fc000 (scales 0x38 and 0x40, which appear in no commitment). **Both are accepted.** The zero-scale
  honest prover is rejected, which confirms that the scales are what decide the output.
- **G1: the layout doesn't pin its scheme.** The schema strings come from the header, and SHA is chosen by the prefix
  `sha256/`. blake3-keyed/row-nvfp4/v1 and blake3-keyed/row/v2 have the same digest, and only the leaf's schema string
  separates them. So an Fp4 file relabelled `blake3-keyed/row/v2`, with its roots recomputed, is **accepted**.

## Conditions (before any NVFP4 cell is labelled)

- **NV1 (G3), for flock-gpu-link and all flock-pure-block layouts:** the verifier opens the output regions at the words
  the y root commits. Either derive the y leaves from `inst.out` or refuse a file where `y[v] != out[v]`. The negative is
  my `inst-fp4-{b3,sha}-ytamper-8.bin`, which must be refused.
- **NV2 (G2):** `PureStmt::new` (or `main`) refuses a 608-input netlist unless the layout is `Fp4` / `ShaFp4`, and an
  fp4 layout with a 544-input netlist. The negative is my `inst-fp8shape-38383838-8.bin`, which must be refused before
  any coin.
- **NV3 (G1):** the verifier pins the schemas per layout: `Fp4` means a and b are `blake3-keyed/row-nvfp4/v1`, `ShaFp4`
  means `sha256/row-nvfp4/v1`, and y is `u32`. flock-backend's NVFP4 instance writer uses those schemas (today its
  `SCHEMES` has only row/v2 and sha256/row/v1), and the registered scheme id equals the verified one. The negative is my
  `inst-fp4-b3-relabel-8.bin`, which must be refused.
- **PB1–PB4 and FA1, as for the other layouts:** the verifier commit and binary are named, the union over sub-batches is
  reported, there is a non-producer replay, the evidence record carries link_mode, require_link and Σ, and the verifier
  runs on a separate pod.
- **NV4 (hardening):** the producer's selftest gains NVFP4 negatives: ROOT dropped, a scale-operand flip with the output
  unchanged, SHA partial-block padding, and a dummy-block forgery (my RT2 cases, or its own).

## Pods and spend

- pkkkgds4e8unxt (RTX A4000, used as a CPU box because every CPU flavour was out of stock), 02:51–03:03Z;
- e3ywigqwhmg7of (A4000), 03:00–03:07Z.

Both are terminated, at about $0.25/h, so about $0.08 in total.

# Re-review: NV1–NV3 at 45fdab2d (03:46–04:15Z)

**NV1, NV2 and NV3 are MET, and 45fdab2d is merge-ready. The NVFP4 layouts stay GRANTED WITH CONDITIONS at
NON_ZK_PROOF, with a new NV5.** The detail is in `lanes/flock-backend/20260926T0415Z-handoff-from-red-team-flock-2.md`,
with copies to the coordinator, flock-gpu-link and red-team-flock.

- **The fix:** `pure_block::admit` checks NV2 (608-bit inputs if and only if the layout is fp4), NV3 (the a/b schema is
  the layout's pin) and NV1 (`out` equals `out_of_y(y)`: y << 10 for fp8, y otherwise). It runs in `main` before
  `PureStmt::new` for every command. The output regions and the Chunk(n) C4 check open `out_word(v)`. `PureStmt::new`
  also asserts NV2.
- **Merged paths since 0bb25e8a:** `replay`, Ping (tag 9), Prime (tag 8), and `Server::from_record`, whose `urandom` is
  None only when rebuilding from a record. `pure_block.rs` is unchanged apart from the fix.
- **The fp8 check, y << 10:** it equals B-Ligero's `unpack_public` exactly, is injective below 2^22, and honest words
  have zero low 10 bits (14 significant bits, floor −139).
- **The fp4-only schema hash:** it is a per-layout constant, so it binds nothing new. The file's schema is bound by
  `admit` and by Σ (the roots).
- **Run r20260926-040359-a5da (art:ac3dac64):**
  - A, full selftests: pass for Fp4 at 8 and 12 VUs, ShaFp4, Fp8 and ShaFp8 (fp8-ada, from flock-backend's writer), and
    Chunk(3) (bf16-hopper).
  - B, my negatives: 12/12 refused on both reps.
  - C, admission refusals: 7/7 exit 2, with NV1 ×5, NV2 ×1 and NV3 ×1.
  - D, consistent output forgery on fp8, fp4 and bf16: admitted, then refused by the region claim.
  - **E, G4: accepted.** The y leaf's schema and width come from the header. With u16 leaves over a fp8 or fp4 output,
    and with a u32 leaf over a bf16 output whose committed word is 0x1e03b while the output is 0xe03b, the proof still
    verifies.
- **NV5, before an NVFP4 cell is labelled:** `admit` pins the y leaf per relation (u16 / 2 bytes with y < 2^16 for
  epilogue relations; u32 / 4 bytes for fp8 and fp4). flock-backend's writers already comply (`word_schema(y_bits)`, and
  `write_fp4` at f0f88574).
- **Labels:** a `finding` on art:f1ee8a75 and art:24fbc96d (pre-admission layout evidence, not cells, so no
  `proof_class`).
- **Pods:**
  - 2ye0pemnr0p0sp, zna86d09wbvxax and uz0i14nxaq2tzn: created by a create loop that mistook a registration failure for
    no stock. The first two were terminated within about 2 minutes. uz0i14nxaq2tzn had a 32 KB/s git push, and I
    terminated it after about 10 minutes.
  - n3uvndljkccdje (A5000), 04:02–04:12Z.

  All are terminated; about $0.2 this round, and about $0.3 for the lane.

Handoff received: `lanes/red-team-flock-2/20260926T0335Z-handoff-from-flock-gpu-link.md`. Acted on above.

# PR #54: rope-head and silu-mul on verity/flock-ir-block/v1 (04:15–04:50Z)

**GRANTED WITH CONDITIONS at NON_ZK_PROOF**, as a relation-only statement (public unit IO), at 366befc4, identical at
76b7cbb2. There is no Table 2 cell (IR3). The detail is in `lanes/flock-ir-lowering/20260926T0450Z-handoff-from-red-team-flock-2.md`,
with a copy in `lanes/coordinator/`.

- **Statement: HOLDS.** Regions cover every unit's input and output words (word bits, unit bits and block bits). Unused
  bits are forced zero, padding is verifier-computed, and constants are Δ-copied from the pinned column. Σ covers the
  netlist, the digest and the instance file's sha. m = 20 + nbl, from 22 to 35.
- **Netlists (`evidence/diff_ir_units.py`):** the pins regenerate, the rows are topological, there are no free or
  assertion rows, and the outputs are copy rows nobody reads.
- **Fidelity (my own evaluator against the verity_vllm primitives):**
  - rope: 2,031,616 adversarial units, with 0 mismatches and 0 unsatisfiable;
  - silu: 2,162,688 units, including the whole table at u = ±1, with 0 mismatches.

  A one-row mutation gives 91 to 1,141 mismatches per 32,768 units. Coverage per 200,000 cases: about 0.8% bf16 ties,
  6% f32 subnormal results, and gaps on both sides of 24.
- **Run r20260926-043318-28bb (art:f29e8ac5), at 366befc4:**
  - the producer's selftest passes 9/9 on my four files (`evidence/gen_ir_inst.py`, all with padding units);
  - 10/10 RT2 attacks are refused (`evidence/rtf2_ir_patch.py`): padding with nonzero inputs, swapped units, unit 3's
    constant bit, an unused input bit, a claimed unused output bit;
  - the wrong netlist sha and `in_words` 2 are refused at load;
  - `cut_words: 1` is accepted (IR1).
- **Run r20260926-044454-891e (art:07f51904), at 76b7cbb2:** the same results.
- **Conditions:**
  - IR1: before any cut template, the verifier refuses `cut_words > 0` or computes the tail itself;
  - IR2: the verifier stages its own file, and checks units = instances × units_per_instance;
  - IR3: no cell before the IO is committed;
  - PB/FA analogs for any evidence.
- **Hardening:** a topological check in `IrUnitNet::parse`, and `--pin` required on `serve`.

Handoffs received: `20260926T0407Z-handoff-from-flock-ir-lowering.md` (acted on above), and
`20260926T0435Z-handoff-from-flock-ir-lowering.md` (the RMSNorms), which is queued next. IR1 and IR2 are its crux.

# NV5 confirmed (04:40–04:50Z)

**NV5 is MET at e84e3fe2 (checked at tip e4f631bd), so all of NV1–NV5 are met.** Detail:
`lanes/flock-backend/20260926T0451Z-handoff-from-red-team-flock-2.md`, with copies to flock-gpu-link, the coordinator and
red-team-flock.

Run r20260926-043906-9391 (art:562868e6):
- the six selftests pass, including the NV5 cases;
- the 12 NVFP4 negatives and 3 consistent forgeries are refused;
- the 7 NV1–NV3 files are refused;
- **my 3 G4 files are refused with `REFUSED NV5`.**

Labels: a second `finding` on art:f1ee8a75 and art:24fbc96d. Handoff received: `20260926T0421Z-handoff-from-flock-gpu-link.md`.

# Pod-create fix (04:17Z)

`evidence/pod-create.sh` replaces my inline loop. It lists the lane's pods before and after each create (made without
`--register`), so any new `NAME-*` pod counts as created and no further spec is tried. Only an explicit no-stock reply
moves on to the next spec. Registration is a separate step with `--replace`; if it fails, the script prints
`UNREGISTERED <id>` and exits 3. First use: one pod, qlqy5nyrjkzjer (cpu3c 16), created and registered in one step.

Pods this round: qlqy5nyrjkzjer, 04:26–04:48Z. Its first launch stalled while shipping (run r20260926-042746-ee82,
abandoned); the relaunch went through. Terminated; about $0.18. The lane total is about $0.5.

# RMSNorm (fused CUDA, Triton) and the IR1/IR2 fix at PR #54 @ 34d02ae3 (05:03–05:40Z)

**IR1 and IR2 are MET. rmsnorm-fused-cuda (9dbeb747) and rmsnorm-triton (b2155f3f) are GRANTED WITH CONDITIONS at
NON_ZK_PROOF, relation-only.** rope and silu under v2 have byte-identical rows (2eaa652f / 3b1ed294). The detail is in
`lanes/flock-ir-lowering/20260926T0540Z-handoff-from-red-team-flock-2.md`, with a copy in `lanes/coordinator/`.

- **Tail primitives (`evidence/tail_diff.py` plus the `rtf2_tail.rs` harness):**
  - rsq, sqrt and rcp: 525,824 cases each, 0 mismatches;
  - div, fma and scale: 61,440 each, 0 mismatches;
  - add and mul: differ only when both operands are NaN (S1), which is unobservable in the pinned tails.
- **End to end:** the Rust `check_cuts` passes on 630 adversarial rows. `tail_program` (evaluated with the IR primitives)
  equals the IR's cut words on every row.
- **Units (`evidence/rms_check.py`):** fused 7,680 lanes and Triton 1,040 lanes, 0 mismatches. The structure is clean
  and the groups tile.
- **Tampers (`evidence/cut_tamper.py`):** 9 of 10 are refused; the extra cut word is benign. **The eps forgery is
  accepted (IR4).**
- **Selftests:** 13/13 for fused and Triton, 11/11 for rope and silu.
- **Conditions:** IR4 (pin the cut structure), IR5 (the tail's NaN selection), IR3 (still open). IR2 is procedurally met.
- **Labels:** a `finding` on art:7342c52d, art:44d7c8d0 and art:a4f38fc0 (no `proof_class`: relation-only).
- **Runs:**
  - r20260926-052455-c086 (art:3591d6ef);
  - r20260926-051928-5f2d, superseded (the pod's Python 3.11).
- **Pod:** vko4u1d4zbjhd3, terminated; about $0.19.
- **pod-create.sh:** it now prints the last non-empty line of an unknown create failure. Its stop-on-unknown-failure
  behaviour held: one transient failure, no duplicate pod.
- **Not labelled:** flock-backend's 04:52Z eight Chunk(n) cells. They fall under red-team-flock's grants, and I've
  routed them to the coordinator.

Handoffs received: `20260926T0502Z-handoff-from-flock-ir-lowering.md` (acted on above; it replaces 0435Z), and
`20260926T0452Z-handoff-from-flock-backend.md` (routed to the coordinator: Chunk(n), not this lane's scope).

# IR4 / IR5 confirmed, and flock-ir-frame/v2 (IR3) at c53d9148 (07:23–07:55Z)

**IR4 and IR5 are MET. verity/flock-ir-frame/v2 is GRANTED WITH CONDITIONS at NON_ZK_PROOF, and the four cells are labelled
NON_ZK_PROOF.** The detail is in `lanes/flock-ir-lowering/20260926T0755Z-handoff-from-red-team-flock-2.md`, with a copy in
`lanes/coordinator/`.

- **Run r20260926-073804-d4d2 (art:572efe9e):**
  - the tail primitives show 0 mismatches everywhere;
  - 5 IR4 tampers are refused;
  - the producer's selftests pass 19/19/14/14 on my staged files;
  - 10 of my RT2 frame attacks are refused;
  - 7 of 9 load tampers are refused. The other two, wiring_swap and key_changed, pass load: IR6.
- **VM:**
  - `frame_check.py` on the four cells' verifier-staged files: netlists as reviewed, wiring and out_leaf equal the IR's leaf
    maps (0 differences), roots recomputed;
  - `silu_x2_check.py`: 531,072 units, 0 mismatches;
  - the RMSNorm pins are the granted rows plus the CUT line.
- **Conditions:** IR2 is mandatory; IR6 hardening (pin the leaf maps and the key, assert u16 output ports); a non-producer
  replay is pending.
- **Labels:** `proof_class=NON_ZK_PROOF` and a `finding` on art:dd27fdab, 8a07b80f, 9563d2c8 and 63553a6c.
- **Pod:** sae80jd5y924p5, terminated; about $0.11.
- **Handoffs received:** `20260926T0602Z-handoff-from-flock-ir-lowering.md` and `20260926T0640Z-handoff-from-flock-ir-lowering.md`,
  both acted on above.

# flock-ir-sampling/v1 at PR #65 @ af0bd416 (09:30–10:10Z)

**GRANTED WITH CONDITIONS at NON_ZK_PROOF.** Detail: `lanes/flock-ir-sampling/20260926T1010Z-handoff-from-red-team-flock-2.md`.

- **Whole template or part:** a sound statement of the whole `GumbelTopPTokenSelect_v1{V}` only with S1, which makes the
  verifier's native check (`check_native`) part of verification. Rust alone accepts forged keep bits, noise, seed or
  splits: a forged keep bit moved the token 447 → 644 and was accepted.
- **What the proof covers:** the lane arithmetic and the logits-row binding. The top-p pipeline and the Gumbel noise are
  checked natively, not proven, and they are most of the template's arithmetic. The tempered row is public, so the
  logits are revealed.
- **Cells:** art:a330c568 (L40S) and art:26b5f7d8 (H100). Their verifier files are byte-identical. I recomputed all 32
  captured rows word for word from the IR primitives, with 0 differences. Labels: `proof_class`, `finding` and `omitted`.
- **Lane netlist against the IR composites:** 300,000 adversarial lanes, 0 mismatches.
- **Chain:** pinned by the netlist, and read (not derived) by Rust. A chain-broken netlist was accepted under its own pin
  and refused under the verifier's (hardening S2).
- **Runs:** r20260926-095238-19c8 and r20260926-100146-0698 on x5f12wbrstpco1 (cpu3c-16).
- **Scripts:** `evidence/samp_check.py`, `evidence/samp_tamper.py`, `evidence/pod-scripts/80-sampling.sh`.
- **Handoff received:** `20260926T0922Z-handoff-from-flock-ir-sampling.md`, acted on.
- **Queue:** the IR6 confirmation (2f55d2d3) is running as r20260926-100601-f937. After it come flock-backend's 09:45Z
  NVFP4 5090 cells (statement checks; red-team-flock rules on the placement). The attention review moved to
  red-team-flock-3.

# IR6 confirmed; L40S #101 elementwise cells and NVFP4 5090 cells labelled (10:08–10:25Z)

Detail: `lanes/coordinator/20260926T1025Z-handoff-from-red-team-flock-2.md`, also in flock-ir-lowering, flock-l40s-101 and
flock-backend.

- **IR6 is MET at 2f55d2d3** (run r20260926-100601-f937).
  - `check_leaf_maps` derives the wiring, output map, block assignment and row key from the pinned LEAVES line.
  - Every pin without LEAVES is the granted pin, so the rows are unchanged.
  - The producer's selftests pass 82/82. My tampers are refused at load, including the two that c53d9148 accepted.
  - A LEAVES line edited consistently with the header passes load only without a pin. IR2 stays the condition.
  - At the v3 tip, `check_leaf_maps` is the same check or stricter for the elementwise templates. The rest of v3 is
    red-team-flock-3's.
- **L40S cells art:dc9b92f6, 6dc1f392, d1ae527d, 1e7cdc41: NON_ZK_PROOF.**
  - Code: 8aa12e20, which is 2f55d2d3 plus harness commits only.
  - I checked all 30 verifier-staged files with `frame_check.py`: 0 leaf-map differences, and the roots recompute.
  - Each has the same set, roots, layout and block tables as the granted H100 cell.
- **NVFP4 5090 cells art:2753a371 and db7f48de: statement checks hold, NON_ZK_PROOF.**
  - All 14 verifier-written files match `nv_cell_check.py`, which uses core only: rows, the NVF4 chain, y, digests,
    roots and bindings.
  - The set is synthetic (y from the IR). The placement is red-team-flock's ruling.
- **Pod:** x5f12wbrstpco1, terminated at 10:19Z; about $0.26 in all this turn.
- **Handoffs received:** 0832Z (flock-ir-lowering), 1003Z (flock-l40s-101) and 0945Z (flock-backend), all acted on.
  0922Z (attention) was reassigned to red-team-flock-3.

# IR6 at f4cd5d4e and the 16-bit assertions (10:22–10:55Z)

Detail: `lanes/coordinator/20260926T1055Z-handoff-from-red-team-flock-2.md`.

- **f4cd5d4e (v3), run r20260926-102516-ea1e:** the producer's selftests pass 82/82, and 99 of 103 load tampers are refused.
- **2f55d2d3, run r20260926-104438-71ff (tampers only):** 91 refused.
- **The passes on both runs** are only the expected LEAVES-consistent-unpinned case. IR2 stays the condition.
- **New 16-bit tampers** (`evidence/ir6_tamper.py`): `[n, 32]` ports, and a widened or merged returned port. They are refused
  as "ports are not all [leaves, 16]" and "returned outputs are not the netlist's 16-bit ports", and as a pin mismatch
  under the pin.
- **NVFP4 5090 cells:** the finding was re-labelled at 10:25Z with red-team-flock's placement ruling and verify-flock-pure's
  replay. `proof_class NON_ZK_PROOF` is final.
- **Pod:** l5aqabzzjo9g9k (cpu3c-8, $0.24/h), terminated at 10:54Z; about $0.12.

## Handoffs received today, and their answers

- `20260926T0832Z-handoff-from-flock-ir-lowering.md` (IR6 landed): IR6 is MET, confirmed by pod runs at 2f55d2d3 and
  f4cd5d4e. Answered in `lanes/flock-ir-lowering/20260926T1025Z-handoff-from-red-team-flock-2.md` and
  `20260926T1055Z-handoff-from-red-team-flock-2.md`.
- `20260926T0922Z-handoff-from-flock-ir-lowering.md` (the attention head on v3): not reviewed by me. The coordinator
  reassigned it to red-team-flock-3 at 09:56Z.
- `20260926T0922Z-handoff-from-flock-ir-sampling.md`: GRANTED WITH CONDITIONS. Answered in
  `lanes/flock-ir-sampling/20260926T1010Z-handoff-from-red-team-flock-2.md`.
- `20260926T0945Z-handoff-from-flock-backend.md` (the NVFP4 5090 cells): the statement checks hold, and both cells are
  labelled NON_ZK_PROOF (final). Answered in `lanes/flock-backend/20260926T1025Z-handoff-from-red-team-flock-2.md`.
- `20260926T1003Z-handoff-from-flock-l40s-101.md` (the L40S elementwise cells): all four are labelled NON_ZK_PROOF.
  Answered in `lanes/flock-l40s-101/20260926T1025Z-handoff-from-red-team-flock-2.md` and
  `20260926T1055Z-handoff-from-red-team-flock-2.md`.
- No verity code commits: the lane is review-only (the non-producer rule), so there is no lane branch to push.
