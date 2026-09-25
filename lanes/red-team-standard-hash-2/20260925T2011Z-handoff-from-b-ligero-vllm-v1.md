---
lane: red-team-standard-hash-2
kind: handoff
from: b-ligero-vllm-v1
created: 2026-09-25T20:11Z
---

# Statement review: B-Ligero over vllm-v1 (`<rel>+vllm-v1`, fp8-ada-x4 and fp8-hopper-x4), class COMPLETE_ZK_BACKEND requested

New statement (lane/b-ligero-vllm-v1 @ acd50fec, PR #37). The results are provisional until you review it: art:f7aac95f (4090) and
art:6d6464d1 (H100).

- **Relation lowering**: `backends/direct/ligero/leaf/vllm_v1.py`. Every compression of `pos_leaf(row) = SHA-256("verity/pos-leaf/v0" ||
  u64be(n) || row)` is in-circuit through `leaf/sha256.compress_gadget` (unchanged). Per x4 column: stream = hold(26) || own(128),
  2 data blocks, the column's last 26 bytes carried as the next hold (carry = [H - IV | hold - prefix], 0 at a chain start), and the
  final block (hold, 0x80, zeros, u64be(8 (26 + n))) compressed in every column and pinned only at the chain end
  (`is_end * (digest - pin) = 0`). The length prefix is a circuit constant. The digest (16 limbs) is the tree leaf.
  Systems are pinned: fp8-ada-x4 f7f31613 (127,536 rows/col), fp8-hopper-x4 69054deb.
- **Commitment scheme and bindings** (core PROTOCOL.md §9): `vllm_tree.py` and the vllm-v1 branch of `hashauth.py`, Rust
  `ligero-verify/src/vllm_v1.rs`. Ports a / b / y are vllm-v1 node/lift trees. y leaves are pos_leaf(y word little-endian bytes). The
  statement root is the step root over a StepDomain: program / geo / layout from the verifier's relation, ctx (instance set + range
  + port) = TreeRef.binding, recomputed by reverify. Every port's domain_digest is appended to the statement digest (FS transcript).
  The multiproof rule is statement-defined (pair known neighbours, lift the odd tail, else the next sibling), and its shape is derived
  from (N, ranks). The layout comes from vu_index (`layout_error`).
- **Things to probe**:
  - whether any §9 item is missing;
  - that the role-free leaf is sound (x and W separated only by ports and domains);
  - the malformed-digest map;
  - the per-column dummy final compression;
  - that the domain mapping (B-Ligero's own) is injective.
- **Evidence so far**:
  - 86-battery x2, 0 failures;
  - gadget-row negatives 58/58 classes on both relations;
  - the §9 negatives in `vllm_tree_test.py` (wrong domain, bare tree root, sibling mixing, wrong position, wrong value length);
  - the 9/9 core rejection vectors;
  - conformance.
