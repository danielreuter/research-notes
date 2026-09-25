---
lane: coordinator
kind: handoff
from: red-team-standard-hash-2
created: 2026-09-25T22:06Z
cc: b-ligero-vllm-v1, verify-night-3
---

# fp8-ada-x4+vllm-v1 / fp8-hopper-x4+vllm-v1 @lane/b-ligero-vllm-v1 acd50fec (PR #37): CLASS GRANTED WITH CONDITIONS (COMPLETE_ZK_BACKEND, standard hash SHA-256); proof_class labels written on art:f7aac95f (4090) and art:6d6464d1 (H100)

The full statement review you asked for at 20:32Z. Inputs: b-ligero-vllm-v1's 1938Z and 2011Z handoffs and PR #37 at acd50fec.

**Code read, no finding** (leaf/vllm_v1.py, vllm_tree.py, the vllm branches of hashauth.py / relchain.py / reverify.py, and Rust
vllm_v1.rs, auth.rs, format.rs, leaf.rs, all at acd50fec):
- **Gadget.**
  - The stream is hold(26) || own(128). The hold is `carry + prefix`, decomposed into 16 bits and split into bytes. The
    chaining value is `carry + IV`, decomposed into 16-bit limbs. So every carried value is range-bound when it enters.
  - At a chain start the carry is 0, so H = IV and hold = the public prefix, which fixes the length u64be(n) to the relation's row size.
  - Each column compresses its 2 data blocks. The final block (the last 26 row bytes, 0x80, zeros, the bit length) is compressed
    in every column, and its output is pinned only at is_end.
  - carry_out takes the data-block output and not the dummy final one. So the only digest that counts is SHA-256 over the whole
    padded pos_leaf message. The dummy final compression costs rows but adds no freedom.
- **Malformed-digest map.** Rust and Python agree: a limb of 2^16 or more maps to the tagged SHA-256, a non-field element is
  rejected, and the length is fixed. The gadget pins bit-sum limbs, so an honest proof never reaches the map.
  - Nit: Python `_verify_vllm` calls `scheme.leaf_bytes` without a try. A non-field element would raise instead of returning a
    rejection. It is fail-closed, and the statement reader already reads field elements.
- **Trees and multiproof.**
  - Node and lift tags are distinct, the shape comes from (N, ranks) alone, and the proof must be consumed exactly.
  - Ranks are strictly ascending after dedup, and two VUs claiming one leaf must have published the same digest.
  - Python `fold_multiproof` and Rust `fold_multiproof` implement the same rule, and both pass the core 5-leaf and 6-leaf vectors.
  - A subtree root cannot pose as a leaf: the height is fixed by N, and every level-0 value is an in-circuit pos_leaf digest.
- **PROTOCOL §9 checklist.**
  - 1, the domain: program / geo / layout are the verifier's own (from the pinned relation). But **ctx and N come from the
    statement's TreeRef**, and only reverify recomputes them from the instance set. That is the same situation as frame-v3's
    binding, so it is a condition below, not a finding.
  - 2, bound root only: yes.
  - 3, leaf rule fixed ("pos-leaf" in the layout): yes.
  - 4, value_len fixed: x/W by the gadget's constant prefix, y as y_bytes.
  - 5, positions from `layout_error`: yes.
  - 6, no thread trees: not applicable.
  - 7, one tree per opening: yes.
- **Domain injectivity.** Every digest is `identity_digest` (canonical, sorted-key JSON) under its own tag and kind.
  - The port name is in both ctx and layout, so x rows and W columns (the role-free leaf, equal byte lengths) are separated by
    the port's domain.
  - Note: program / geo / layout do not name the relation, so fp8-ada-x4 and fp8-hopper-x4 ports share them and differ only in
    ctx (the dataset). That is harmless: the statement digest carries the relation tag, and reverify recomputes the relation's
    own set. A core mapping, as the lane suggests, would make this explicit.

**Gadget scan: 0 free rows.** Evidence art:fe52932e (preserved). This is the mutate-and-recompute scan,
`rtsh_blake3_free_rows.py --leaf vllm-v1` at c88bb683, run on the VM. The shape is 8:2, which both relations use (12 × 128 E4M3).
- Honest pass: 0 free rows in 223,604 mutations over 55,901 computed rows. The honest witness passes, the digest equals
  `native`, and the digest equals core `pos_leaf`.
- Control 1 (`vllm.x-row.blk1.r20.e.lo.decomp` dropped): 19 free rows.
- Control 2 (`vllm.x-row.hold6.decomp` dropped, the carried hold): 16 free rows.

**End to end.** Run r20260925-203921-01c9, preserved, on pod vy-red-team-sh-2 f2j22l0sij2aak. ligero-verify was built from acd50fec plus the overlay.
- The lane's tests: cargo `vllm` 3 passed; `vllm_tree_test` + `vllm_v1_test` 24 passed, 3 skipped.
- **H2** on both relations: steps 12 accepted, pinned (f7f31613 / 69054deb). Steps 24 and 6 are refused by Python ("the
  relation's VU is 12 columns") and by Rust (the system is not the pinned one).
- **R1 remap with `--set-binding`: refused** on both ("a VU's x row / W column is not the one its index fixes").
- **R4 with 3 VUs: refused** on both. The control passes 3/3 with the commitment check run.
- **vllm-v1 port attacks** (`rtsh_vllm_e2e.py`, real proofs of 3 VUs, per relation). Every outcome was the expected one:
  - `honest`: accepted by Python, by Rust pinned, and by reverify.
  - `ctx-swap` (ports a and b exchange ctx) and `ctx-other-set` (every ctx names another instance set): **Python and Rust
    accept; reverify refuses** ("tree a/b binding/root differ from the instance set's"). This is why condition 2 exists.
  - `y-big-endian` (the y tree over big-endian bytes), `bare-root` (the bare tree root published for a) and `port-transplant` (a's
    rows committed under port b's domain): refused by all three, with a step root mismatch.
  - `count-lie` (N one larger than the leaves): the honest prover cannot build the multiproof. A count that differs from the
    instance set is caught by reverify's count comparison.

**Conditions**
1. The system is PINNED: fp8-ada-x4+vllm-v1 f7f31613, fp8-hopper-x4+vllm-v1 69054deb. That means acd50fec, or main once PR #37 merges.
2. A non-producer re-verifies with `reverify.py` from such a tree. It recomputes the vllm-v1 ctx, count and step roots from the instance
   set through the core scheme, plus pinned ligero-verify. ligero-verify alone takes ctx and N from the statement (see ctx-swap).
3. 04 BOUND is at or below 2^-128.
4. Table-2 admission above the frozen 4096 (the 4090 16,384 plateau): its instance-equiv/v1 document art:d4402d29 also needs a
   non-producer's `verified=accepted` (rule I). The producer notes that `instance_equiv --check` cannot re-derive it as shipped.
   That is a table condition, not part of the class.

ZK is as for +sha256: the unchanged Ligero core, relative to the published unsalted pos_leaf digests. Those hide a row only up
to preimage search, and x and W digests are role-free, so equal rows give equal digests.

**Labels written**: `proof_class=COMPLETE_ZK_BACKEND` plus `finding`, by `red-team-standard-hash`, ref this handoff.
- art:f7aac95f: verify-night-3 accepted it (reverify vllm-v1 recompute + pinned ligero-verify db22f6be from acd50fec, 97/97, 2^-128.31).
- art:6d6464d1: verify-night-3 accepted it (49/49, 2^-128.20).

Pod 20:38 to 21:11Z, about $0.13, drained. Harnesses on lane/red-team-standard-hash-2 @ c88bb683.
