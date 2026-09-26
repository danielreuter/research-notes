lane: coordinator · kind: handoff · from: salted-leaves · created: 2026-09-26T23:20Z

# PR #93 red-team conditions fixed: merge `cursor/sha512-commitments-18a8` @ 6338450b after #88 (@ a53900df)

- **Tip:** `6338450b` (base a53900df), [PR #93](https://github.com/danielreuter/verity/pull/93). Merge PR #88 first, then retarget
  #93 to main.
- **Fixed, per `lanes/coordinator/20260926T2256Z-handoff-from-red-team-hm96.md`:**
  - **C1:** frame-v3 §6 and vllm-v1 §10 name what rests on `cr/sha-512` (everything the scheme computes) and what still rests on
    SHA-256. Table 1 cites `cr/sha-256` beside `cr/sha-512` until the re-baseline.
  - **Findings 1 and 5, and the root's domain-digest ask:**
    - the new `identity_digest_sha512` covers every identity digest a SHA-512 scheme computes: vllm-v1's `domain_digest`,
      frame-v3's positions identity and hm96-sha512's scheme digest;
    - the committer's leaf rule takes the instance's salt size.
  - **Finding 2:** `validate_commitment` checks the root's width.
  - **Finding 3:** the claims wording is fixed.
  - **Finding 4:** the schemas `hm96-sha256/row/v1` and `hm96-sha512/row/v1` are named.
- **The remaining SHA-256 dependency** (E4, extended to the identity and domain digests at the re-baseline), for the prerequisites list:
  1. the IR identity digests `program`, `ctx` (context), `geo` (geometry) and `layout`, and the integration's `template` and `names`;
  2. frame-v3's `binding`.

  They move to 64-byte SHA-512 all at once: a fixed-width change with new vectors. A mixed width would break the one-way parsing.
- **Vectors:** only the three SHA-512 files changed; no SHA-256 vector did.
- **Tests:**
  - core: 1,119 passed;
  - vLLM commit tests, lints and the dead-code census: pass;
  - `test_evaluation::test_every_registered_kernel_is_self_checked_here` fails only when collected together with the vLLM tests, and
    fails the same way on cd00f704.
