---
lane: b-ligero-sha256
kind: report
created: 2026-09-25T07:00Z
status: open
---

CHECKPOINT 00ffe398 (07:08Z) [open] started 07:00Z; merged b-ligero-standard-hash ad4c3440; design: publish CV after last data block, padding compression native; x4 folds (2 blocks/col); survey absent; next: sha256 leaf native+Rust+harness
# b-ligero-sha256: B-Ligero frame-v3 `sha256/row/v1` row leaves (SHA-256 half of the standard-hash track)

Goal (launch message): a SHA-256 compression gadget in B-Ligero's relation proving frame-v3 `sha256/row/v1` row digests of the
x rows and W columns, published and checked natively by `ligero-verify` against the scheme's trees; pinned in Rust; gated
with the 86-negative battery; then the first SHA-256 full-relation cell (frame-v3, then a vllm-v1 variant). Decision doc:
Project store `docs/commitment-scheme-decision.md` §3, §5, §6.2 step 5, §6.3. Worktree `~/projects/verity-main-wt/b-ligero-sha256`,
branch `lane/b-ligero-sha256`, base main 00ffe398. Pod scripts: `evidence/pod-scripts/`.

## 0. Starting state (07:00Z)
* Merged origin/lane/b-ligero-standard-hash ad4c3440 (`--commit-per-rep`, +blake3 pins bf16-ampere / fp8-hopper) -> my tip
  ad4c3440. blake3-leaf-3 820aa6f and the pipelined hashed runner 1cf9178 are already ancestors of main.
* steps pin (red-team H2): Rust `check_vu_shape` + Python `layout_error` already on main (lane steps-pin); ligero-steps-pin's
  236020a6 closes the +shared (v6) Python gap only, which this lane does not use. Merge it when it reaches main.
* Survey `docs/hash-proving-survey.md`: not present at 07:00Z.

## 1. Design (fixed by the core schema, not by the gadget)
`sha256/row/v1` = `SHA-256(prefix64(role, word_bits, n_words) || row_bytes)`: the first block is a public constant, so the
chain starts at a constant midstate; the row is 24 (E4M3) / 48 (BF16) whole blocks; the padding block (0x80, zeros, bit
length) is a public constant.  **In-circuit: the data blocks only.  Published: the chaining value after the last data block
(8 u32 = 16 limbs) plus a constant header (role, word width, n_words).  The verifier runs the padding compression natively**
(`leaf_bytes`), exactly like the BLAKE3 leaf's native parent fold: two rows with the same published CV are a SHA-256
collision (same prefix, same length).  So "one extra block for padding" costs 0 rows.

Columns: the x4 folds (`fp8-ada-x4`, `bf16-*-x4`: 128 bytes = 2 whole blocks per operand per column) -- no half-block
columns, so no discarded compression (the x1 relations would waste half of every SHA-256 compression like BLAKE3's).

## 2. Gadget options (written before the survey; the survey gate decides)
| option | rows / 64 B block (est.) | notes |
|---|---|---|
| (a) bit design as §3 of the decision doc (2-input XOR products, 3-input XOR = 2 products) | ~27 000 + schedule 7 900 | §3's estimate |
| (b) bit design with a carry-bit 3-XOR: for booleans x, y, z one row `c = maj(x,y,z)` with `c^2 = c` and `(s-2c)^2 = (s-2c)`, `s = x+y+z`; XOR = `s - 2c` affine, Maj = `c` itself | ~18 300 (rounds 64 x 204, schedule 48 x 100, H bits, feed-forward) | message bits reused from the operand bit rows (hashchain's `hash.a[i].b<j>`) |
| (c) one-hot lookup tables (`ctx.lookup`) for XOR / Ch / Maj | 66x worse per XOR (blake3-leaf census: 2 112 rows per u32 XOR) | Ligero's lookup here is a one-hot selector, not LogUp |
| (d) LogUp / Lasso-style lookups (Flock, Jolt) | n/a in today's B-Ligero relation | needs a LogUp argument in the Ligero relation (share-logup has one for Poseidon2 sharing only); out of this lane's scope |
| (e) GKR / Binius (binary-field towers) | n/a | a different proof system; not B-Ligero |

Per round (b): Sigma1 32 + Ch 32 + Sigma0 32 + Maj 32 carry rows + the two modular sums a' (7 addends) and e' (6) on 16-bit
limbs, 19 + 19 bit rows each = 204.  Schedule: sigma0 32 + sigma1 32 + 4-addend sum 36 = 100 per W_t, 48 of them.

## Log
* 07:00Z started; read LANE-CONTRACT v2.0, TABLES (+ amendments), decision doc, blake3-leaf-3 / red-team-leaf-3 /
  b-ligero-standard-hash / ligero-steps-pin reports, `leaf/blake3.py`, `leaf/base.py`, `hashchain.compose`, `rowleaf.py`,
  `ligero-verify/src/leaf.rs`; inbox empty.

## Discrepancies
(none yet)

## FINAL
(pending)
