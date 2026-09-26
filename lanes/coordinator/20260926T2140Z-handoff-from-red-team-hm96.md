---
cursor:
  subagentId: "bc-6d082f2c-9c48-534c-9ae6-46bf3724b4a7"
---

lane: coordinator · kind: handoff · from: red-team-hm96 · created: 2026-09-26T21:40Z · status: final · repo: danielreuter/verity ·
origin: PR #88 @ f1df809f (base main@2431e3c1)

# red-team-hm96: hm96-sha256/v1 (PR #88 @ f1df809f) is GRANTED WITH CONDITIONS; merge after C1 (fail closed off the host path) and C2 (doc fixes)

**Verdict: GRANT WITH CONDITIONS.** The scheme holds as specified: statistically hiding, and binding from SHA-256 collision
resistance alone. The off-by-default path is byte-identical to today's. There is one real defect: the opt-in switch doesn't fail
closed. It is latent today, but it would let a root that binds hm96 sit over unsalted leaves.

- **C1, before merge:** fix F1. It is about 10 lines plus a negative test; the probe below serves as that test.
- **C2, before merge (doc):** reword F2's text, and add F3's paragraph to the vllm-v1 spec.
- **C3, before hm96 hiding is claimed for the rows of record or cited in Table 1:**
  - F2: a setup claim for the pinned key;
  - F5: the GPU hm96 kernel and padding under hm96;
  - F6: forward to flock-netlist before their gadget lands.

## Findings

1. **F1: the hm96 switch doesn't fail closed off the host path. Medium, open.** The refusal keys on the `gpu_tree` flag, not on the
   leaf path actually taken.
   - **`NativeCollectCommitter`.** This is `native_collect_v2b`, the rows-of-record committer. It hashes chunk leaves in C++
     (`_commit_step_native`, `_commit_step_windowed`) whatever `gpu_tree` is, and never calls `_salted`. So
     `NativeCollectCommitter(gpu_tree=False, native_worker=True, leaf_scheme="hm96-sha256/v1")` is accepted and commits
     unsalted leaves. Unless `chunk=256` is also passed, those leaves don't open either.
     - Its step roots still bind the hm96 scheme digest, and `extra.leaf_scheme` says hm96.
     - Its `name` override drops the `+hm96` suffix.
   - **`NativeHostCommitter.commit_block_offline`** does the same. I reproduced it with CPU torch: an hm96 committer gets unsalted
     chunk leaves under an hm96-bound step root, and its openings verify with no salt and with a garbage salt (`failopen.json`).
   - **The verifiers skip the hiding layer there.** `verify` and `_range_leaves` never consult it in their `_gpu_blocks` and
     padding branches.
   - **Not reachable today.** No CLI passes `leaf_scheme`, and `NativeCollectCommitter`'s default `gpu_tree=True` is refused.
   - **Fix:**
     - refuse hm96 in `NativeCollectCommitter.__init__` and in `commit_block_offline`;
     - under hm96, make `verify` and `verify_range` return False for any step without salts;
     - in `finalize`, assert `len(_salts[s]) == 128 · n_leaves` for every step.
2. **F2: hiding with the pinned key is conditional but stated unconditionally. Low, open.**
   - vLLM only ever uses `DEFAULT_KEY`; `HidingLeaves()` has no per-run key knob.
   - With that key the bound is N·2^-192 except for a 2^-64 fraction of keys: the common-reference-string step PROTOCOL §3 names.
   - PROTOCOL §8 ("Hiding is statistical and rests on no hash property") states it without that condition, and so do the module
     docstring and the README glossary ("statistically hides").
   - `verity.claims` has no hiding or setup entry.
   - Fix: qualify §8 and the docstring now, and add a setup claim before Table 1 cites hiding.
3. **F3: vllm-v1 `PROTOCOL.md` doesn't mention hm96. Low, open, doc only.**
   - **§4 context digest.** §4 still gives native-host `ctx` as `run_id/step=s`. Under hm96 it is
     `run_id/step=s ‖ "/leaf=" ‖ scheme_digest`, with the digest as 32 raw bytes. It is still injective: the suffix is fixed-length,
     and the default digest contains neither `/step=` nor `/leaf=` (checked).
   - **Leaf rule.** §5's table and §9 item 3 don't list the hm96 leaf rule.
   - **The §5 argument still holds under hm96.**
     - The first bytes separate every preimage: `verity/h…` (hm96 leaf), `verity/p…` (position leaf), `00 00 00 13` (node, lift)
       and `fa2h`.
     - Position is bound by shape(N, i) and N by the step root.
     - Context is bound by program, ctx, geo and layout, plus the scheme digest.
4. **F4: the OS generator versus a seeded stream. Info.**
   - The spec calls salts from the OS generator statistical, and salts from a seeded ChaCha20 stream computational (§3, §7 and the
     flock-netlist handoff).
   - On Linux, `os.urandom` is itself a ChaCha20-based CSPRNG, so this is a modelling convention, not a different assumption.
   - Word both as "statistical given uniform salts".
5. **F5: scope. Info.**
   - **Covered:** only `NativeHostCommitter`'s host path, per-tensor and packed.
   - **Not covered:** the rows of record. They run `native_collect_v2b --gpu-tree` (`row_stages.py:502`, and the `tp/commit.py`
     default), where hm96 is refused.
   - **Still unsalted:** padding, the fa2h stream and thread trees, C0 semantic trees and capture-v1 trees. The weights are public.
   - **Replay openings (R17-5)** can't regenerate salts. An hm96 leaf opens only from the original committer's retained salts;
     today a replay fails closed.
6. **F6: a circuit's key must be the statement's key. Low, for backends, open.**
   - **The attack.** Suppose a gadget took the key as a witness. A prover can then solve M_k'·y = b ⊕ x' for a key k': that is 256
     linear equations in 1,279 unknowns. The committed `b ‖ c` then opens to any x'. My demo solves it (`recompute.out`).
   - **The leaf's key digest** stops this only where the verifier recomputes the leaf with the key the circuit used.
   - **For Flock:** `reserved_key_bytes`, a per-leaf reservation in their circuit, must be a circuit constant or a public input
     bound to `scheme_digest`. Please forward this to flock-netlist.

## What holds

- **Parameters:**
  - the salt y is 1,024 bits from `os.urandom`;
  - the family is `y ↦ M_k·y ⊕ b`, with M_k the 256 × 1,024 Hankel matrix over GF(2);
  - the key is 1,279 bits, with bit 1279 zero so every matrix has one encoding;
  - the inner digest x, the commit string's two halves b and c, and the leaf are 256 bits each.
- **Checked:**
  - the family is universal: rank 256 for adversarial nonzero d;
  - `DEFAULT_KEY` and the vectors' second key both give matrices of rank 256.
- **Hiding bound, as instantiated:**
  - uniform key: 2^-257 per leaf against the ideal, and N·2^-256 between any two digest vectors, key-dependent values included
    (δ(k) doesn't depend on x);
  - pinned key: N·2^-192 outside a 2^-64 fraction of keys, so 2^-128 at N = 2^64 and 2^-152 at N = 2^40;
  - for comparison, HM96 Theorem 1's generic bound gives k = 127.
- **Binding:**
  - the three-case reduction to `cr/sha-256` holds for any key;
  - the key digest in the leaf prefix rules out choosing the key after commitment;
  - no random oracle is used anywhere.
- **Randomness:**
  - one `os.urandom` call per step, and the retained salts are those bytes verbatim;
  - salts are distinct within a run, and fresh on a re-commit or in another committer with the same run_id;
  - nothing is derived from values: equal values get different leaves.
- **Openings: 359 checks, all passed.** Rejected:
  - a wrong nonce: bit flips, a fresh salt or a zero salt;
  - swapped leaves, or another position's or another step's salt;
  - a salt, value or path that is truncated or too long;
  - length extension (`value ‖ pad ‖ ext`), and bytes shifted across the value/salt boundary;
  - mixed-rule openings, cross-run openings (same run_id or another) and another key;
  - range openings with salts swapped, rotated, short, missing, extra or shifted.

  The packed and `hash_threads=2` paths are salted too.
- **Default path:** byte-identical between base and head in 6 configurations. Roots, levels, ctx, every opening and range,
  `persistent_bytes` and the name all match. Only `run.extra` gains `leaf_scheme` and `salt_bytes`, and no root reads them.
- **Vectors:** recomputed from the spec text alone (`recompute_hm96.py`, 128 checks), covering:
  - the key, both prefixes and the scheme digest;
  - the row weights and the XOR count;
  - the masks, by matrix product and by bit loops;
  - the leaves, and the trees with their bound roots.

  Negatives: a salt shifted by a vector in the kernel of M keeps b but is rejected through c. Length extension is refused on the
  inner digest, the salt digest and the leaf.
- **Tests:**
  - core commitments, boundaries and repository tests: 222 passed;
  - `integrations/vllm/tests/commit`: exit 0 on both head and base, with CPU torch.

## Evidence

- **Artifact:** `art:6f13f90a1df4df8f587b98851b957414bfccd275de6ef0896b22b9321856f43d` (redteam-findings/v1, target
  `art:b3a08e21`), preserved.
- **Scripts:** `lanes/red-team-hm96/evidence/`.
- **Labels:** `finding` by red-team-hm96 on `r20260926-204634-0958` and `art:b3a08e21`, both with ref `art:6f13f90a`.
- **Cost:** CPU only, $0.
