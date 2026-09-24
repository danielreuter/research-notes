---
lane: fp4-decode
kind: report
created: 2026-09-23T17:00Z
status: superseded
---

CHECKPOINT none (00:03Z) [superseded] by fp4-decode-2 (coordinator)
CHECKPOINT none (17:40Z) worktree ~/projects/verity-main-wt/fp4-decode on lane/fp4-decode from main e0cf2cd; pod vy-fp4-decode (13kdcc7jhlyxlg, RTX 5090 32 GiB, $0.99/h, community cloud -- SECURE had no 5090 stock; created 17:08Z) bootstrapping (evidence/bootstrap.sh); design settled (below), coding the decode gadget.

# fp4-decode — the in-circuit FP4 decode layer: `fp4-nvf4+poseidon2` (alias `+hash`)

## 0. Design (settled 17:35Z)

The NVFP4 unit (`fp4/relation.py`) takes 141 verifier-side pins per unit: `a[i].n`, `b[i].n` (64 + 64 signed E2M1
numerators in halves), `g[g].sm` (scale-mantissa products), `g[g].X` (group weight exponents), `g[g].part` (participates),
`anc.G` (the anchor: max over participating groups).  The hashed relation converts every one of them into a hint row and
re-derives it from the committed operand bits:

* **E2M1 code** (4 bit rows `s e1 e0 m`): `p = e0 e1`, `q = m (1 + e1 + p)`, `mag = 2 e0 + 4 e1 + 2 p + q`
  (= NUMERATOR[code & 7] in halves), `n = (1 - 2 s) mag` -- 3 product rows per code, no lookup.
* **UE4M3 scale byte** (8 bit rows): `b7 = 0` (PTX: padding bit clear), `e = b3..b6`, `m = b0..b2`; `nz_e = [e != 0]`
  (inverse pair), `mant = m + 8 nz_e`, `exp = e - 9 - nz_e`; finite: `inverse_nonzero(127 - low7)` (the 0x7F NaN);
  `nz_mant = [low7 != 0]` (inverse pair).
* **Group** g: `sm = mant_a mant_b`, `X = -2 + exp_a + exp_b`, `any = [sum_i mag_a[i] mag_b[i] != 0]` (16 products +
  inverse pair; magnitudes are >= 0 so the sum is 0 iff every product is), `part = any nz_mant_a nz_mant_b`,
  `cand = GRID_FLOOR + part (X - FRAC_BITS - GRID_FLOOR)`.
* **Anchor**: `G - cand_g in [0, 256)` for every g (8 bit rows each) and `prod_g (G - cand_g) = 0` (3 product rows):
  G is the max.
* **Lanes**: the 64 codes + 4 scale bytes of one operand per step are 72 nibbles = 288 bits -> 12 lanes of 24 bits
  (6 nibbles each; < 2^24 < p, injective), one Poseidon2 permutation per operand per unit as for BF16 / E4M3; rate
  lanes 12..15 are 0.  IV = (role, word_bits = 4, n_words = 24 * 72): a different domain from the 16-bit-lane rows.

Not leaf-agnostic yet: the `LeafScheme` interface (leaf-iface, D0 at 0d7d716, not landed on main at 17:35Z) packs
`LANE_BITS // word_bits` words per lane; the FP4 row needs 24-bit lanes (or two permutations).  The seam is one
parameter (`lane_bits`) of the Poseidon2 leaf's packing; noted in §FINAL.

## Discrepancies

(none yet)

## 17:58Z — pod 1 was defective; replaced

`vy-fp4-decode` (13kdcc7jhlyxlg, community cloud, 149.36.1.31) came up with **no usable GPU**: `nvidia-smi` → `Failed to initialize
NVML: Unknown Error`, `torch.cuda.is_available()` → False, though `/dev/nvidia0` existed. The source shipment was also crawling (1.4 MB
after 8 min). Terminated at 17:58Z (~50 min ≈ $0.83 wasted). Creating `vy-fp4-decode-2` (5090, `--require-reference-part`).

CHECKPOINT 53b0b46 — Python composition + 15 laptop tests landed (see 17:40Z entry); pod work not yet started.

## 18:30Z — pod up (4090), bootstrap OK, GATE PASSED at 2048 VUs

* Pod 2 (`vy-fp4-decode-2`, ent204xmid8lw2, 5090) never got a public IP in 15 min (terminated 18:08Z); 5090 stock then `None`. Fell back
  to **`vy-fp4-decode-3` = k39j0s2bvhlljf, RTX 4090 24 GiB reference part** (`--require-reference-part` verdict `reference`, host Ryzen 9
  7950X, driver 570.195.03, $0.74/h, created 18:13Z). Consequence: the bench is on a 4090, not the 5090 — I run the bare `fp4-nvf4`
  control on the same 4090 so the hashed/bare ratio is apples to apples; the 0.0714 s 5090 cell is quoted alongside.
* Bootstrap r20260923-182325-f860: torch 2.8.0+cu128, numpy 2.5.3, cupy, blake3, rustc 1.98.1, `ligero-verify` release build
  sha256 71465c20…, NVRTC ok, fp4 smoke ok (`evidence/bootstrap.sh`).
* Smoke gate r20260923-182618-9e35 (64 VUs, l=2048): 1/1 honest, 92/92 negatives rejected.
* **Gate r20260923-182818-c9bc (`--relation fp4-nvf4+poseidon2 gate-vu --vus 2048 --batch 16384`, LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1):
  4/4 honest sub-batches accepted (3 × 682 VUs at l=16384 + the 2-VU tail at l=256), 92/92 negatives REJECTED, 0 failures**
  (`evidence/gate_2048.{log,json}`). The negative family: claimed word bits, accumulator link / fraction bit, the off-domain 0x7F
  (hint generator refuses), then the FP4 family with the prover FORCED on (`FP4HashedRelation.extra_negatives`, domain check off):
  UE4M3 NaN 0x7F → quadratic, padding bit 0x80 → linear, 0xFF → linear, E2M1 code word 16 → chain (sum over H), code 0xFF → chain,
  **wrong scale (committed 0x3c proved as valid 0x44, chain recomputed consistently) → `auth: a: multiproof rejected`**; then the
  hashed family (digest lanes, swapped digests, is_end moved, multiproof corruptions/truncations/missing, root swap, binding change,
  VU claiming another VU's row, index out of range, sponge capacity link broken, 60 witness-row mutations across hash.* rows).
* Composed system on the pod = the laptop's: 4442 rows/unit (1583 base + 1122 private-operand decode + 1720 sponge + 17 digest pins;
  **+2859 rows/unit**, 28 linear + 2863 quadratic), 19 linked rows, 24-bit lanes × 12 rate lanes, 2 permutations/unit.
* Hashed prover per 682-VU sub-batch at l=16384 on the 4090: 0.09 s steady (2.89 s first = NVRTC + graph capture).

CHECKPOINT 3b05f3f (18:30Z) — bench r20260923-182920-9002 running (4096 VUs, l=16384, --zk --mode interactive, local coins, dump rep 1).
