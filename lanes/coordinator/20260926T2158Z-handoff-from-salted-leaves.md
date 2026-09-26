lane: coordinator · kind: handoff · from: salted-leaves · created: 2026-09-26T21:58Z

# PR #88 red-team conditions C1 and C2 fixed: merge `cursor/hm96-sha256-leaves-18a8` @ a53900df as hm96-sha256/v1

- **Tip:** `a53900df` (base main@2431e3c1), [PR #88](https://github.com/danielreuter/verity/pull/88).
- **C1, finding 1 (b8132bdf): hm96 fails closed on the leaf path actually taken.**
  - The context digest binds hm96 only for a salted step, and every step root is bound through it: host path,
    `commit_block_offline`, and the native collector's native and windowed roots.
  - Overridden step paths and the GPU tree are refused at construction; that covers `NativeCollectCommitter` with `native_worker`
    on or off.
  - `verify` and `verify_range` reject unsalted steps, and `finalize` refuses a run that has one.
  - There are 5 new negatives, and all fail on f1df809f.
- **C2, findings 2–4 (a53900df):**
  - the pinned-key bound with its condition in hm96 §8, the docstrings and the README;
  - `verity.claims` gains `statistical-hiding` and `common-reference-string`;
  - vllm-v1 §4 documents the `/leaf=` suffix (injectivity checked by a test), and §5 and §9 document the hm96 rule;
  - "statistical given uniform salts" throughout;
  - finding 6 is a spec rule (hm96 §5): the key is never a witness.
- **Default path:** unchanged. ctx is byte-identical with hm96 off.
- **Tests:**
  - core, protocols, repository, bench views and vLLM lints: 1,209 passed;
  - vLLM commit and acquire tests with CPU torch: pass except `test_compiled_source::test_renumber_…`, which is pre-existing on
    f1df809f and depends on the torch version.
- **Next:** E4 (Daniel: SHA-512 on every data commitment) is a stacked follow-up PR on this branch: `hm96-sha512/v1`, plus SHA-512
  variants of the frame-v3 and vllm-v1 tree framing, all opt-in.
