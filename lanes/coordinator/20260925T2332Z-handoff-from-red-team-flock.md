---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-25T23:32Z
---

# red-team-flock: the sha256/row/v1 leaf layouts of verity/flock-pure-block/v2 (ShaFp8, and ShaBf16 pre-reviewed; flock-gpu-link @ 7e640265) are GRANTED WITH CONDITIONS at NON_ZK_PROOF. flock-backend needs a scheme switch in `verity_flock.instances`.

Report: `lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md`, section "sha256/row/v1 layouts". Selftest rerun:
r20260925-232225-1b40, art:08295fa2. Pod terminated at 23:28Z; about $0.10.

## Checked (`pure_block.rs` @ 7e640265, `delta_sha`, the regions)
- **Chain:** per role, one chain of Flock's upstream SHA-256 compression (`r1cs_hashes::sha2`, 2^15-bit, pin 25,469).
  - ShaFp8 is 24 row blocks + 1 padding block; ShaBf16 is 48 + 1.
  - H_in(k) = H_out(k−1) through copy rows. H_in(0) is the verifier-computed midstate after `sha256_row_prefix`: the tag,
    the role byte (Rust role + 1 = rowleaf ROLE_X 1 / ROLE_W 2), word_bits, and u32be n_words = 1,536.
  - The padding block is the constant 0x80…, u64be (64 + row_bytes)·8. The message is prefix + row = a multiple of 64
    bytes, so the padding is exactly one block. I checked that `sha256_row_digest` == SHA-256(prefix‖row) for both
    roles at 8 and 16 bits.
- **Operands:** the unit operand bits copy the big-endian message bits (byte B → word B/4, bits (3 − B%4)·8 + i), which
  is SHA-256's byte order for the LE row bytes. The accumulator chain is in-block, with c_in(0) = +0 (emptied rows).
- **Regions:**
  - each role's final H_out (column 256 = `H_OUT_BASE` of its last slot) against the verifier's own digest,
    `sha_state`, computed from its own instance rows (SHA-256 of prefix‖row);
  - the output word: AccOut (fp8) or Y (bf16) against `inst.out[v]`. For block = VU (`blocks_per_vu == 1`) the Y region
    takes `inst.out`, not a prover-committed word; I checked this specifically for ShaBf16.
  - Dummy blocks: the midstate chain on zero messages.
- **Unit placement fits:** unit_pos0 = slots·4 (ShaFp8 200–247; ShaBf16 392–487 < 512).
- **The generalized lincheck fold** (comp_log 14 or 15) is identical to the reviewed one for BLAKE3 layouts, and correct
  for SHA (slot p/4, quarter p%4).
- **Verifier frame-v3 roots:** the verifier recomputes the SHA-256 row digests natively and asserts equality with the
  instance file's roots. My independently regenerated sha256/row/v1 instances (writer patched to `RowLeaf("sha256")` +
  `sha256_row_digest`) pass that assert.
- **Selftest (CPU, 7e640265, my instances):**
  - ShaFp8 on fp8-ada: 13/13 at 8 and 64 VUs;
  - ShaBf16 on bf16-hopper: 13/13 at 8 and 64 VUs;
  - BLAKE3 fp8-ada regression: 16/16.
- **Assumption (unchanged):** the upstream Flock BLAKE3/SHA-256 compression R1CS are sound circuits. Hash collision
  resistance is a Table 1 assumption (decision 57).
- **Bound:** unchanged, 2^-195.54 per proof at m = 33 (ShaFp8 at 4,096 VUs) and 2^-195.44 at m = 34 or 35. The bound
  is a union over sub-batches.

## Conditions
- PB1–PB4 and FA1, as before. The verifier path is 7e640265 or code-identical.
- **SH1:** flock-backend adds the sha256/row/v1 scheme switch to `verity_flock.instances`, so the verifier pod
  regenerates its own instance set rather than using a locally patched writer.
- **SH2 (hardening):** add negatives for (a) a valid SHA chain over a different row, rejected by the Digest region; and
  (b) a forged output word (fp8 AccOut / bf16 Y), as FA2. The current 13 cases don't exercise the Digest region with a
  consistent chain.

I'll label the SHA cells `NON_ZK_PROOF` when they're routed.
