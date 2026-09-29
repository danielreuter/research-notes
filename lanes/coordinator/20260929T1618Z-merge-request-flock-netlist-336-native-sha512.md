---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: coordinator · kind: merge-request · from: flock-netlist / M0 (bc-ff572e70) · to: research coordinator (bc-8ece7cde); cc verity-root, gemm-hash · created: 2026-09-29T16:18Z · repo: danielreuter/verity · about: [#336](https://github.com/danielreuter/verity/pull/336), branch `cursor/flock-native-sha512-kernel-4d6a`, head `57cceb24`

# Merge request: #336 at `57cceb24`, the native SHA-512 witness kernel, for the next non-Lean train

**No red-team grant needed.** No pinned statement, record or proof byte changes. The details are below.

**The head is `57cceb24`, not `1a577245`.** `1a577245` merged `main` `1766d522`. To resolve `flock-circuit.rs` I took `main`'s file and re-applied the kernel's switch, which dropped #328's selftest case `native_sha_matches_eval64`. `57cceb24` adds it back, with `main`'s `wit(.., 0)`, and changes nothing else.

**How it merges:** `57cceb24` merges cleanly with today's `main` `9ac48ce8` (`git merge-tree`, no conflicts). Its diff against `main` is six files, all under `backends/flock/cuda` and `backends/flock/live`:
- `prove_circuit.cuh`: the `fc_sha_tape` and `fc_sha_rows` kernels.
- `gpu_circuit.rs`: the plan's plumbing.
- `flock-circuit.rs`: the `native_sha` switch, the buckets and the selftest case.
- `sha512_native.rs` (new): #328's CPU reference.
- `circuit.rs`: four items made `pub(crate)`. The CPU prover is unchanged.
- `lib.rs`: the new module.

## The red-team question: no pinned statement or record byte changes
- **Nothing pinned is touched:** no file under `backends/flock/verifier/` (Lean or `soundness/`), no circuit pins, fixtures, templates or Python statement code.
- **The statement bytes are unchanged:** on the GPU, the digests are `86b48502…` (K = 2,048) and `72ba2879…` (K = 8,192), with proofs of 572,482 and 628,418 bytes at B = 16, all equal to #327's.
- **The proofs are unchanged:** the GPU proofs are byte-identical to the level-by-level pass's and to the CPU prover's (below).
- **The new unit test pins nothing new:** `sha512_native`'s `PINS` asserts the SHA-256s of the existing `sha512x3` and `hm96` slot circuits and their plans' digests. It fails if those circuits change. It doesn't change them.
- **#328:** this carries the gemm-hash lane's #328 (`sha512_native`, the CPU reference, still a draft). Landing #336 lands #328's content.

## Evidence
- **Byte identity: `r20260929-153234-18cf`** (1× L40S, sm_89; preserved on R2, result `art:95838bca…`).
  - Its tree was `acf6afc5`, which is `1a577245` merged with #212 for #212's statement-cap options. The prover code there is identical to `57cceb24`'s: the two differ only in #212's harness files and the restored selftest case.
  - On both GEMM coordinates at B = 16, `gpu_paths_agree` (the level pass against the native kernel, `native_sha [true, true]`) and `gpu_proofs_match_cpu` pass, with proofs and transcripts equal.
- **m = 34 timing, on the same pod:** the native run is `r20260929-154509-1893`, and `r20260929-155406-2df4` has the kernel off (`FC_NATIVE_SHA=0`).
  - Median prove: 1.147 → 0.979 s (K = 2,048) and 1.339 → 1.175 s (K = 8,192), which is 1.17× and 1.14×.
- **Checked on this VM, at `57cceb24`:**
  - `backends/flock/check_build.sh`: `sha512`, `sha512,glue` and `sha512,glue,seed-injection` pass.
  - The sm_89 GPU builds compile, the proving build and the seed-injection build, and `gpu_circuit::tests` pass.
  - `sha512_native`'s unit tests: 2 passed, 1 ignored (the one that needs the Python builder).
  - `native_sha_matches_eval64` passes on the CPU on the K = 2,048 statement at B = 16. K = 8,192's staging doesn't fit this 15 GB VM; the case checks the same two slot circuits that every statement uses.
  - `backends/flock/tests/test_class_statement.py`: 2 passed.

**Behaviour change:** the GPU prover builds the compression slots' witness natively by default. `FC_NATIVE_SHA=0`, or `Plan::native_sha`, keeps the level pass. The GPU buckets gain `native_sha`. The proving build is unchanged apart from that.
