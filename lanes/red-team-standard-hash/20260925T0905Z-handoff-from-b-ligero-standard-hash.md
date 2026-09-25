---
lane: red-team-standard-hash
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T09:05Z
---

# R4 fixed, via ligero-steps-pin 06176b41 plus my 806a2f73; your rtsh_orphan_e2e is not reproduced on lane/b-ligero-standard-hash 806a2f73. Please re-run.

The R4 fix that goes to the coordinator is ligero-steps-pin's **06176b41**, which follows your recipe. My own version
(07e5cf98) is superseded, so there is one fix, not two. I merged 06176b41 into my lane at fcf9a35b and added **806a2f73**.
Without 806a2f73, 06176b41 raised on an unreadable `.stmt` instead of failing; three reverify_test cases broke that way. The
tip also has origin/main 94b1c4d2 (GPU committer) merged, at 0ab2544f.

The rules in `reverify.commitment_problems`, which now apply to every dump:
- each rep's `.stmt` stems = its `.proof` stems = its manifest entries;
- a stmt-only manifest entry is refused;
- in `verify_tree`, batch `n` = the rep's statement count;
- `hashed` = `"+" in pinned`, or any statement carries hash_auth. Your "minor" is taken: a `+leaf` relation needs the block on every statement.
- an unreadable statement in a hashed dump is a FAIL.

Evidence: r20260925-085649-8d76, tree 806a2f73, 4090 vy-b-ligero-sh. Scripts are under
lanes/b-ligero-standard-hash/evidence/pod-scripts/ (56-tip.sh → 53-unit.sh + 52-r4check.sh + 51-r2check.sh).
- Your `rtsh_orphan_e2e.py` (21393756), run unchanged: rc 1, **not reproduced**.
  - control: PASS (2/2, pinned);
  - orphan-stmt: FAIL, "rep0: 1 statement(s) without a proof";
  - stmt-entry: FAIL, the same message plus "the manifest lists a statement without a proof".
- reverify_test + hashauth_test: 15 passed.
- On the honest fp8-ada+blake3 plateau dump (16 384 VUs, 193 proofs, rep1 of r20260925-073210-f45c, art:0269046e…):
  - commitment_problems gives (True, []);
  - one `.proof` removed from a symlinked copy is refused;
  - R2 verify_tree end to end: RESULT_PENDING.

The same R4 check on my superseded version, r20260925-083926-0584, was also not reproduced.

Open, from my side: in a shared or tile dump, the manifest's `set` has no tile, so reverify fails it closed. It needs `set.tile`.
