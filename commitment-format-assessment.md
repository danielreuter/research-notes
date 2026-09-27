---
cursor:
  subagentId: "bc-ba6cec03-e2aa-5a7e-9db3-6bc124a205aa"
---

# Commitment format: vLLM's production framing vs core frame-v3 (decision 1)

This is a read-only assessment at `main` `cc7842a0`, 2026-09-24 9:40 PM PT. No plan or code was changed; decision 1 is on hold for the owner. Sources: `packages/verity/src/verity/commitments/merkle.py`; `integrations/vllm/verity_vllm/commit/{hashing,semantic_layout,hidden_stream}.py`; `acquire/native_host.py`; `backends/sp1/common/src/{packed,kernel/openings}.rs`; `backends/ligero-verify/src/{hash,auth}.rs`; SYNTHESIS §2 D2, §5.3, §6 C1 and §7; lane f1's notes on the leaf layout. Where a claim rests on the surveys rather than my own reading, it says so.

## 1. Is vLLM's production framing sound and fully specifiable?

**What production actually uses.** It isn't one scheme but four layers, spread over about eight copies. By the survey's count four of them are CUDA SHA-256 implementations (S1 §4.4). None has a written spec or conformance vectors.

| layer | rule | position and context binding |
|---|---|---|
| base hash | `H(tag, parts) = SHA-256(u32be(len tag) ‖ tag ‖ (u64be(len p) ‖ p)*)`, with tags `verity-vllm/{leaf,node,lift,ids,empty,json,challenge}/v1` | tag-separated and length-prefixed: an injective encoding |
| host position leaf | `pos_leaf = SHA-256("verity/pos-leaf/v0" ‖ u64 nbytes ‖ value)` | no id and no index in the leaf |
| GPU chunk leaf (`fa2h`) | `SHA-256(64-byte header ‖ chunk)`. The header starts with the `fa2h` tag word, version and kind, then launch tag, chunk index, chunk words and layout geometry. Thread leaves computed inside the FA kernel use a similar 16-word header (block, thread, sequence lengths) | the index is in the header |
| nodes | `H(node/v1, left, right)`; an odd trailing child becomes `H(lift/v1, child)` and is never duplicated | not bound to level or index |
| roots | semantic root `SHA-256("verity/semantic-root/v0" ‖ program_digest ‖ query_id ‖ template_digest ‖ ctx_digest ‖ u64 epoch ‖ u64 N ‖ merkle_root)`; run root `SHA-256("verity/cmt-integ/run-root/v0" ‖ program_digest ‖ geo_digest ‖ u64 n_steps ‖ fold(step_roots))` | N or the step count is bound, along with program, template and geometry digests |

**Soundness.** I found no break.
- **Domain separation.** A leaf can't be confused with a node, because the leaf and node messages start with different bytes: the `verity/` ASCII prefix, the `fa2h` word, or a u32 length.
- **Parseable roots.** Every field in both root bindings is fixed-length except `query_id`. With only one variable-length field, the concatenation still parses one way.
- **Checked by inspection only.** This is an argument from reading the code. No spec or test pins it.

**Is `pos_leaf` without an id or position a weakness? No, not by itself.**
- It is the standard design; RFC 6962 leaves carry no index either.
- A leaf's position is fixed by its authentication path. The path's shape follows from (index, N), and N is bound in the root.
- The leaf's meaning (id, dtype, shape) comes from the template, whose digest is also bound in the root (`unrank(i)`).
- The requirement lands on the verifier. It must derive the path shape from (index, N) rather than accept whatever path the prover sends, and it must check the root's program, query, template and epoch fields against its own expectations. Today that is true of the code (`merkle.range_path_shape` / `fold_range`, and `verify` re-folds the run root), but nothing specifies it.

**Are the lift nodes unbound to level or index a weakness? No, not for these fixed-size trees.**
- `lift` has its own tag, so an odd lifted child can't be confused with a leaf or a pair node.
- The tree's shape is fixed by N, so a node's level and index are implied by its position in the path.
- Binding level and index matters for what core does and vLLM doesn't: variable-size or verifier-derived domains, compressed multiproofs, and mixing subtrees from different trees. Reusing a subtree across two vLLM trees is harmless, because both then commit to the same values.

**Real weaknesses, apart from "core can't verify it" (D2):**
1. **No single spec.** There are about eight framing copies (SYNTHESIS §5.3) and no conformance vectors, so a divergence between a CUDA copy and the Python verifier would go unnoticed. The fix is the one-module-plus-vectors step the plan already has.
2. **A layout label that doesn't match its leaves.** Host (non-GPU-tree) committers label their binding map `chunk-leaf-v1`, but their leaves are host position leaves. A verifier that trusts the label would apply the wrong leaf rule. Lane f3 found this and left it unfixed, because changing the label changes map digests.
3. **Three framing styles.** They are the tagged `H`, the raw-prefix `pos_leaf`, and the binary `fa2h` header. Each is unambiguous as far as I checked, but only by inspection.
4. **No verifier-derived context.** Session, phase and owner binding comes from fields the prover supplies (program digest, query id, epoch). Core instead derives the domain on the verifier side, and the prover never describes it. That doesn't make the framing unsound, but it puts every check of those fields on the verifier, and the spec must say so.
5. **Layout chosen by environment variable (D3).** This is fixed in f3, now merged.

So the framing is fully specifiable: a spec plus vectors could be written today from the table above, without changing any roots.

## 2. What depends on frame-v3, and what each direction costs

**Depends on frame-v3.** The frame is `veritor/protocol/merkle/frame/v3\0`, with short tags `leaf`, `pad`, `node` and `empty`. Leaves and nodes are bound to a verifier-derived `CommitmentDomain`, and nodes to (level, index).
- **Core:** `commitments.merkle`, `multiproof`, `indexed`, `rowleaf` and `identity`, and the verification lowering and `packed.py`.
- **SP1:** the kernel's frame-v3 openings are its typed obligation format 1 (`kernel/openings.rs`), and the kernel mirrors the frame constants.
- **`ligero-verify`:** the Rust crate hashes leaves, nodes and domain identities under frame-v3 (`auth.rs`).
- **Direct Ligero:** `auth.py`, `hashauth.py`, `vu.py`, `serialize.py` and `leaf/`.
- **Also:** `backends/shared/hash_gpu` and three `verity_numerical` modules.
- **Recorded evidence:** core's docstring says every recorded root depends on the frame constants, so the research campaign's recorded proofs and verifier sessions do. I didn't count them.

**Depends on vLLM's framing:**
- the 13 frozen regression rows' commitment roots, and every vLLM Commit record;
- the CUDA commit paths, including leaves computed inside the FA2/FA3 tap kernels;
- the openings and binding-map code.

SP1 also implements the proof-of-concept vLLM leaf `verity-vllm/leaf/v1` (`packed.rs`, schema string `packed/v1:verity-vllm/leaf/v1:…`), which core's `leaves.py` also names. No backend implements the production `pos_leaf`, `fa2h` or `lift` rules.

**Cost in each direction:**

| option | work | roots and evidence | risk |
|---|---|---|---|
| **(a) production moves to frame-v3.** Core ships the spec, reference and vectors, and vLLM changes its CUDA to match | M–L (SYNTHESIS C1): the Python fold and leaf rules, four CUDA SHA copies and the in-kernel thread leaves; a GPU-pod throughput measurement before and after | all 13 regression rows re-baselined in one Phase 3 epoch; research evidence untouched | commit throughput. frame-v3 adds a 33-byte prefix and domain, level and index parts per hash. For 256-byte chunk leaves that is small; for node hashing it may add about one SHA block per node. Not measured yet |
| **(b-named) vLLM's current framing becomes a second named scheme** in `verity.commitments` (spec, Python reference verifier, conformance vectors); vLLM's CUDA and Python must pass them byte for byte | S–M: a few hundred lines in core, plus vLLM consolidating its copies behind one module (planned anyway) | none; roots unchanged | none now. Core can then verify production openings, but core statements and multiproofs still can't address production positions (no `CommitmentDomain`) |
| **vLLM's framing replaces frame-v3 as the core standard** | L–XL: rewrite core `merkle`, `multiproof` and `indexed`, the SP1 kernel's openings, `ligero-verify`, the direct Ligero authentication and hash relation, and `hash_gpu` | all frame-v3 research evidence re-recorded | it drops core's verifier-derived domain binding, a protocol property. Adding it back would make it no longer "vLLM's existing framing" |

## 3. Do proof backends care?

Yes, wherever they check openings inside a proof. Core has no `CommitmentScheme` interface. Each backend compiles a framing's exact byte layout into its guest or circuit: SP1's kernel openings, `ligero-verify`'s `auth.rs`, and the direct Ligero hash relation. SP1's `packed/v1:<framing>` schema string is the beginnings of a dispatch, but every framing behind it is still separate kernel code. So each named scheme a backend must prove over is one implementation per (backend × scheme). That is the per-format fork the owner wants to avoid, and it only arises for backends that actually prove over production openings. None does today.

## 4. Recommendation

1. **Now:** define vLLM's existing production framing in `verity.commitments` as a named scheme (spec, reference verifier, conformance vectors). vLLM's CUDA and Python must pass the vectors byte for byte, and the host layout label gets fixed with the next re-baseline. This closes D2's "core can't verify production roots" with no root changes, and it's the consolidation Phase 1 plans anyway.
2. **Keep frame-v3 as the only framing proof backends implement.** Don't add production `pos_leaf`, `fa2h` or `lift` to SP1 or Ligero.
3. **Move production to frame-v3 (a) when a proof backend first has to prove statements over production openings.** Do it then as the single Phase 3 re-baseline, with the throughput measurement as the performance check (if slower, optimize vLLM's CUDA, not the format). That is the point where (b-named) would otherwise force the backend fork.
