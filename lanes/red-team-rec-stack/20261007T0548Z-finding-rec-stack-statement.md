---
id: red-team-rec-stack/20261007T0548Z-finding-rec-stack-statement
campaign: proofs
lane: red-team-rec-stack
kind: finding
status: final
repo: verity
origin:
  - pr:1081@edc996c486ef2c0eb0c8a6bf1638c6ccb1d5b50d
  - pr:1246@2f3be9e5790088aabc1860b053d89c12074a2da4
---

# Red team, the rec stack's test statement fix: GRANT #1081 at edc996c48 and #1246 at 2f3be9e57

GRANT for both heads.

**The diffs.**
- `git diff --stat 7321d7b9b edc996c48` is exactly `backends/flock/tests/test_rec_algebra.py` (+2/−1) and
  `backends/flock/tests/lean/generate_inner_claims.sh` (+1/−1). `STATEMENT` and the generator's argument become
  `verity/flock-circuit@f5df3bbc+seed-injection`, and one `#:` line is added.
- `git diff --stat ee9bd5655 2f3be9e57` is those two files, with line-identical edits, plus `test_rec_vstage.py` (+3/−2).
  There, InnerFold's statement argument becomes the same name, reflowed.
- #1245's new head `a5094e85a` changes only the first two files against `7b11dda7a`.
- No path outside `*/tests/*` moved in either PR. `verity/flock-circuit@f5df3bbc+seed-injection` is a name in
  `Tags.lean`'s `all` at the head.
- Both heads, and #1245's, merge cleanly onto their parents and onto `main` `4bd12249c`.

**The honest case.** Run `r20261007-054621-3718` on vy-nebius-1, `--cwd clone` at `2f3be9e57`, did four things:
- built `backends/flock/verifier/lean`;
- replayed the fetched `hidden-outputs/flat/gemm-coordinate` recording with `selftest_records.py`;
- ran `flock-verify verify --circuit stage/circuit.txt --public stage/pub-4.bin --session honest`, which accepts under
  `verity/flock-circuit@f5df3bbc+seed-injection` (`"accepted":true`) and refuses under `verity/flock-circuit+seed-injection`
  with "S2/R7: the session parameters are not the verifier's";
- ran `test_the_lean_verifier_rejects_exactly_the_mutations_with_a_nonzero_residual`, which passes (1 passed).

So the cause is as diagnosed: the recording carries f5df3bbc's identity, which the unversioned name no longer is after
#1383. `inner_claims.json` pins its inputs' hashes but no statement name. It was generated when the unversioned name was
f5df3bbc's identity, so it stays valid.
