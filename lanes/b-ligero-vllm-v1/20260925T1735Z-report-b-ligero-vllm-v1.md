---
lane: b-ligero-vllm-v1
kind: report
created: 2026-09-25T17:35Z
status: open
---

CHECKPOINT f8419291 (18:12Z) [open] fp8-ada-x4+vllm-v1 gate 13 honest+86 neg 0 fail (r..180400-c457), Rust fixture ACCEPT; PINS f7f31613; 4090 pin-check+gadget negs+screen r20260925-181058-a012; H100 y5puhmozi3wh9r setup+gate r20260925-181202-65f3; code push blocked (verity token 401)
CHECKPOINT 5f22dcde (18:02Z) [open] tip 5f22dcde: vllm-v1 pos-leaf gadget (3 compressions/col x4), port trees+step roots+domain digests (Py+Rust, core vectors), bench variant; 4090 fxm6q6vt6doyh4 fixture+gate r20260925-180031-cadb running
CHECKPOINT cd963fd4 (17:35Z) [open] lane opened on cloud VM; branch lane/b-ligero-vllm-v1 from origin/main cd963fd4; reading contract, PROTOCOL.md s8-9, b-ligero sha256 gadget; agent bc-00554250-ebd7-5ace-b76e-296ea0be65e9

# b-ligero-vllm-v1: the first B-Ligero Table 2 cells whose statement commits under vllm-v1

Launch (root, 17:34Z): both schemes first-class; B-Ligero has frame-v3 keyed-BLAKE3 cells (4090 FP8 1.9e7x, H100 2.8e8x).
Produce B-Ligero cells over `vllm-v1` (core spec `verity/commitments/vllm_v1/PROTOCOL.md` §8-9): reuse the SHA-256
gadget (`leaf/sha256.py`, lane b-ligero-sha256) and the x4 fold; add the vllm-v1 leaf / node / lift circuit and the §9
bindings with the core vectors as golden tests; negatives (wrong domain, bare tree root, sibling mixing across trees,
wrong position, wrong value length); 4090 then H100 under the v1 protocol with commitment timed; instance-equiv if
re-packed; hand verified results to verify-night via the coordinator; request a red-team review. Budget $40.
Agent bc-00554250-ebd7-5ace-b76e-296ea0be65e9 (cloud). Branch lane/b-ligero-vllm-v1 from origin/main cd963fd4.

## Design (commits c3a73a9d, 966808cb, 5f22dcde, f8419291)

Relation string `<rel>+vllm-v1` (leaf scheme `vllm-v1`, schema `vllm-v1/pos-leaf/v0`, `leaf/vllm_v1.py`; Rust
`leaf::VLLM_V1`, `vllm_v1.rs`).

* **Leaf in-circuit.** `pos_leaf(row) = SHA-256("verity/pos-leaf/v0" || u64be(n) || row)`. The 26-byte prefix is not block
  aligned, so every compression is proved: 25 for E4M3 (1536 B), 49 for BF16. Per x4 column the stream is
  `hold(26) || own(128|256)`: c/64 data blocks, the column's last 26 bytes carried as the next hold (carry = `[H - IV | hold -
  prefix]`, 0 at a chain start = IV + prefix), and the final block (hold, 0x80, zeros, u64be(8(26+n))) compressed in every
  column and pinned only at the chain end. 3 compressions per operand per column (FP8 x4) against frame-v3 SHA-256's 2:
  127,536 rows/col against 90,848 (1.40x). The digest published (16 limbs) IS the vllm-v1 tree leaf; no native padding.
  The compression gadget is `leaf/sha256.py`'s `compress_gadget`, unchanged.
* **Nodes / lifts / roots: verifier-native** (as frame-v3's trees). Ports a / b / y are vllm-v1 node/lift trees (y leaves =
  `pos_leaf(y word LE bytes)`), each published root the **step-root binding** over a StepDomain.
* **§9 bindings.** (1) domain: program (K, scheme, "gemm-coordinate"), geo (K, row bytes, word bits, y bytes) and layout
  (port, leaf rule, value, value_len, word bits) are derived by the verifier from its relation; ctx (instance set,
  range, port) is the TreeRef binding, recomputed from the set by `reverify.py` (core `VllmV1` only); `domain_digest` of
  every port is absorbed into the statement digest / FS transcript (`hashauth.digest_bytes`, Rust `hash_digest_bytes`).
  (2) the statement root is the step root; a bare tree root is rejected. (3) leaf rule fixed by the relation suffix and
  in the layout digest. (4) value length is a circuit constant (prefix) and in the layout digest. (5) positions from the
  VU index (`layout_error`), multiproof shape from (N, ranks). (6) no thread trees. (7) one multiproof per port, leaves
  from their own port only.
* **Multiproof** (statement-defined; vllm-v1 has none): level by level, known nodes ascending; pair a known even node with
  a known right neighbour, lift the last node of an odd level, else take the next sibling. One leaf = the §3 path without
  its nulls (tested against every core opening path).
* Domain mapping is B-Ligero's provisional one (tags `verity/ligero-b/vllm-v1/{program,ctx,geo,layout}/v1`); SP1 and
  A-GKR each have their own (unmerged lanes). A shared core mapping would let one serving commitment serve every backend.

Tests: `vllm_tree_test.py` (core trees + every opening path, step openings + domain digests, all 9 core rejections,
random multiproofs, the §9 negatives), `leaf/vllm_v1_test.py` (layout prefixes, pos_leaf, a chain of column gadgets
evaluated from its witness program = pos_leaf, tampered hold / start / length), Rust `vllm_v1::tests` (core 5-leaf tree
and paths, the step opening vector and its domain digest, the Python port domains), conformance suite (role-free leaf).
