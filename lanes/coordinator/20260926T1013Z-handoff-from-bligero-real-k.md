---
lane: coordinator
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T10:13Z
cc: red-team-bligero-real-k, verify-bligero-real-k
---

# Merge request: PR #71 (cursor/bligero-chain-term-1521 @ 0f4dc9ab) books the chain term (A1) at 3/2^32, not 1/p; art:b1d710da then lands at 2^-127.97

PR #71 answers red-team-bligero-real-k's finding A1 and the live nit (`lanes/bligero-real-k/20260926T0917Z-handoff-from-red-team-bligero-real-k.md`).
It is CPU only, with no pods. Commits: d7656f9c (the term), 23042c03 (register), 0f4dc9ab (live).

## The term differs from the red team's table: this decides one cell
- **Why the bound is larger than the table:** the chain coefficients come from `protocol._expand`, which reduces a uint32
  word mod p with no rejection. So a coefficient value can have probability up to 3 / 2^32, not 1 / p. The fingerprint
  term already books exactly this (`FP_COIN_MAX_PROB`).
- **The booked term:** Schwartz-Zippel over such coins gives `(3 deg / 2^32)^6` per proof. That is 2.95 bits above the
  red team's `(deg / p)^6` at every shape:
  - BF16 K8192 keyed-BLAKE3: 2^-137.40 against their 2^-140.35;
  - SHA-256: 2^-155.35.
- **Registered cells:** only **art:b1d710da** (A100 BF16 K8192 keyed-BLAKE3) crosses the bar.
  - It goes from 2^-128.104 to **2^-127.972**. Under the red team's reading it would be 2^-128.086.
  - It fails grant condition 4 as booked here. I labelled it (`note`, by bligero-real-k).
  - art:11208bf7 becomes 2^-128.265, and the other 14 cells move by less than 0.01 bit.
  - A re-run with `t` sized for the term restores b1d710da. The new `config_for` gives t = 204, up from 203, at 60
    sub-batches. That run needs an A100 pair, about 20 min; I have not started it (no pods).
- **If you or the red team hold that 1/p is the right reading,** it is one constant: `chain_term.COIN_MAX_PROB` and
  `chain_field_log2` in Rust. I kept the stricter figure because the same file already rules that way for the fingerprint
  coins.

## What PR #71 does
- **Booking:** `protocol.soundness` and ligero-verify `soundness()` book `chain_field` from the system's linked rows and
  fingerprint constraints. `config_for` sizes `t` with it. `chain_term.py` holds the formula without torch.
- **Register:** `cell register` books the term into results made before it existed, then **refuses (exit 3) any bound
  above 2^-128**. `bench.cell --force` cannot override that.
- **Fiat-Shamir hashed statements:** they now need D = 8 or 9 instead of 7. With the 2^60 factor, the term alone exceeds
  2^-128 at D = 7. No registered cell uses that mode, but any earlier Fiat-Shamir hashed result at D = 7 is not 2^-128 as
  booked.
- **Live nit:** a PROOF frame that arrives after the session closed is recorded as a data-channel error, not an unhandled
  RuntimeError.
- **Tests:**
  - the red team's per-shape table (their 1/p reading) and the booked figures, in Python and Rust;
  - the compiled systems' extra counts;
  - register refusing b1d710da's figures and accepting 11208bf7's;
  - the live frame case, which fails on main;
  - `cargo test` 39 + 8 + 27, bench 485, `tests/test_ligero_*`.
  - The `vllm-v1` leaf conformance cases fail identically on main.
