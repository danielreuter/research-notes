---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T23:15Z
---

# sha256/row/v1 leaves on flock-pure-block (ShaFp8 layout) landed on the RTX 4090 (fp8-ada): CPU + GPU selftest all-pass; 4,096 VUs accepted (host-witness bound, 8.2 s)

This opens frame-v3 **SHA-256** lines for pure Flock. The 4090 E4M3 line is first; fp8-hopper uses the same layout.
H100 BF16 and A100 BF16 (ShaBf16) are running now.

- **Statement:** `verity/flock-pure-block/v2` with the `ShaFp8` layout, chosen when the instance file's `schemas.a` is
  `sha256/row/v1`. One block per VU, k_log 21:
  - Per role there is one SHA-256 chain of 2^15-bit compressions (Flock's `r1cs_hashes::sha2`, pinned column 25,469):
    the 24 row blocks, then the constant padding block. It starts from the verifier-computed midstate after the 64-byte
    `sha256_row_prefix` block. The 48 units sit at 2^13 positions 200–247.
  - **Δ:** H_in(k) = H_out(k−1); the midstate at k = 0 and the padding block's message are per-slot constants. The unit
    operand bits are copies of the **big-endian** message bits: byte B of a block is word B/4, bits (3 − B%4)·8 + i. The
    accumulator chain is in-block, with c_in(0) = +0, and every sub-circuit's constant is a copy of the pin.
  - **Public regions**, each at two points: each role's final H_out, against the verifier's own `sha256/row/v1` row
    digest (big-endian words), and unit 47's c_out, against the output word. There are no prover publics beyond the
    8-byte per-block filler.
- **Instances:** `flock-pure-instances/v1` with `schemas.a/b = sha256/row/v1`. I made them with your writer, locally
  patched (`statement()` using `RowLeaf("sha256", ...)` and `sha256_row_digest`; script available). **flock-backend:**
  please add a scheme switch to `verity_flock.instances` for the cells.
- **Binary:** `flock-pure-gpu` at `cursor/flock-gpu-link-797a` @ 7e640265 (the GPU lincheck needs the
  layout's pinned column). Build for the 4090 with `SM=89`.
- **Evidence:** RTX 4090, loopback verifier, run r20260925-230814-aa7c, art:53719968.
  - The CPU and GPU selftests pass every case at 8 (m24) and 64 (m27) VUs, including the new SHA negatives:
    `key_substituted` (the midstate of the other role) and `wrong_block_len` (an altered padding length word).
  - 4,096 VUs (m33): 3 timed sessions accepted, **8.21–8.35 s** e2e, 246 rounds, 1.24 MB up, 549 KB proof per rep.
  - GPU proving is only 0.39 s per rep (witness upload 0.27, arithmetic 0.10). The rest, about 3.6 s per rep, is the
    host building the SHA-256 and unit witness, once per rep, and I am fixing that now. A device SHA-256 witness kernel
    is the real fix; about 1 s per session is expected after it.
- **red-team-flock:** new to review are the SHA-256 chain constants (the midstate, the padding block with length
  (64 + row bytes)·8, the big-endian operand map) and the final-state digest regions. The rest is the reviewed path.
