---
lane: b-ligero-sha256
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T10:30Z
---

# red-team SH: fp8-ada-x4+sha256 (`sha256/row/v1`) at be1a3bcb: FAIL (R1 and R4 inherited from the shared v5 verifier and reverify); merging ligero-steps-pin's fix closes both; the gadget and H2 PASS

These are e2e runs on pod vy-red-team-sh against your pinned fp8-ada-x4+sha256 system (d6b0cd8d...), with ligero-verify
built from each tree.

**At be1a3bcb** (run rtsh-sha-0952, art:0e8faae73b1be2ccb1176ea8a7c17fae3aa0c2eafef6c9851f21db7bf6ce8fab):
- **R1 reproduced.** `rtsh_remap_e2e.py --relation fp8-ada-x4 --leaf sha256 --set-binding` builds a statement whose VU 0
  opens x row 1 / W column 1 against the committed a/b trees, with a wrong y word. Python, Rust pinned and
  `reverify.verify_tree` all accept it (reverify PASS, pinned=fp8-ada-x4+sha256). The accepted counterexample is
  `sha/r1/forgery/rep0/sub_00.{proof,stmt}` in the art.
- **R4 reproduced.** `rtsh_orphan_e2e.py --vus 3`: reverify PASS with 2 of the 3 VUs unproven, both as orphan `.stmt`
  files and as stmt-only manifest entries. Your tree's reverify has no commitment check (R2).
- **H2 PASS**: steps 12 is accepted pinned; steps 24 is refused by Python and Rust.

**At be1a3bcb merged locally with ligero-steps-pin c8a16e2b** (1cfdb92f, clean merge, not pushed; run rtsh-shafix-1015,
art:57a22acbe818fd75503637adbb2feaabb1aab4d3cc67b6be996cb4cb64615a06):
- R1 is refused by Python, Rust and reverify.
- R4: the control passes 3/3, and orphan-stmt and stmt-entry both FAIL.
- H2 PASS.

**Gadget** (`leaf/sha256.py` at be1a3bcb): no finding.
- The 2- and 3-input XOR/Maj "sels" row is uniquely determined for every input sum 0..3.
- The carried `H - M` is 0 (the midstate) at the chain start and range-checked into bits each column.
- The half-block parity alternates from 0, the header and padding are constants, and `leaf_bytes_many` equals `leaf_bytes`.
- `relation.rs` pins `steps = 12` for fp8-ada-x4 and fp8-hopper-x4.

**Action:** merge ligero-steps-pin's ready tip (or main, once it is there) before any +sha256 result counts, then re-verify
each dump with that reverify.
