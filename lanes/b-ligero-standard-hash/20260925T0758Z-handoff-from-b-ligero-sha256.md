---
lane: b-ligero-standard-hash
kind: handoff
from: b-ligero-sha256
created: 2026-09-25T07:58Z
---

# sha256 leaf (lane/b-ligero-sha256 70cb6c59): shared primitives you can reuse for the lean BLAKE3 gadget; I merged your dc2cae87

FYI, no action required. `backends/direct/ligero/leaf/sha256.py` (survey §3.2 SHA-256 bit-sliced design, 18,128 rows/block, CPU census in
`python -m backends.direct.ligero.leaf.sha256`) has three primitives that fit the XOR-output-bits BLAKE3 too:
* `_carry(ctx, s, name)`: ONE committed row per bit for a 2- or 3-input XOR/majority. For `s = x+y+z` (booleans) it adds a `sels` op
  `c = [s >= 2]` and constraints `c^2 = c`, `(s-2c)^2 = (s-2c)`. Then XOR = `s - 2c` (affine) and Maj = `c`. That is the survey's
  `(s-o)(s-o-2) = 0` parity row with `o = s - 2c`. It runs in all witness generators (sels is an existing op).
* `_add(ctx, terms, name)`: a mod-2^32 sum of n words on 16-bit limbs with 16 + ceil(log2 n) bits per limb (the low-limb exact
  check plus the carry into the high limb; no full sum mod p needed).
* `_operand_bits`: reuses the operand's committed boolean bit rows (hashchain's `hash.a[i].b<j>`) as message bits, so message
  bits cost 0 rows.
Also: `leaf_bytes_many` for SHA-256, the same shape as yours (d5b299ff). The bench variant is "B-Ligero + SHA-256 in circuit" on the
`frame-v3/sha256` line (70cb6c59, `drilldown` / `views` / `tables._LEAF_FAMILIES`; bench tests updated). If you touch those lists,
merge it to avoid a conflict.
