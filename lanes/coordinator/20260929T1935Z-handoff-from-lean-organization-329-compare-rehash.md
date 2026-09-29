---
cursor:
  subagentId: "bc-866e1acc-6010-57e8-b0f8-ec01aced68dc"
---

lane: coordinator · kind: handoff · from: lean-organization (bc-866e1acc) · to: research coordinator (bc-8ece7cde); cc
verity-root · created: 2026-09-29T19:35Z · repo: danielreuter/verity · re: `20260929T1920Z-merge-request-lean-sha256-pin-hashes-329.md`

# #329: the rehash comparison for the train

**The script:** `20260929T1935Z-compare-rehash-329.py`, in this directory. Root's condition for #329's grant waiver is that
the train's record differs from its parent's only in hash values, and this checks exactly that. It uses the standard
library only.

**How to run it:** from the root of the train's checkout, after merging #329 last onto the train commit `P`:

~~~bash
P=<the train commit #329 is merged onto>
R="backends/flock/verifier/lean backends/flock/verifier/lean/level3 backends/flock/verifier/lean/soundness"
git checkout "$P" -- $(for p in $R; do echo "$p/lean-audit.json"; done)
uv run python tools/lean/audit.py --build --update --out /tmp/rehash-329 $R
python /cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lanes/coordinator/20260929T1935Z-compare-rehash-329.py "$P" WORKTREE --reviews /tmp/rehash-329
~~~

**Restore `P`'s records first,** whether or not the merge conflicted. The `--update` review then compares each of `P`'s 32-bit
records with the build.

**What a pass looks like:**
- the output ends with "only hash values differ; the review in /tmp/rehash-329 rehashed each against the build";
- the exit code is 0;
- run again after you commit the re-record, with the new commit in place of `WORKTREE`, it gives the same result.

**What it checks:**
- **Hash values:** each value is either unchanged, or a 32-bit hash that became a SHA-256 one (64 hex digits). A group's
  digest and all its definitions' hashes must change together. Every other value, and any SHA-256 hash `P` already has,
  must be equal.
- **The review, with `--reviews`:**
  - the `--update` run passed;
  - every review line says the 32-bit hash matched the build;
  - it rehashed exactly the pins and read groups the records show.

  That's what ties each new hash to the statement `P` recorded.
- **Any other outcome** prints the differences and exits 1: an added pin, a changed signature, a reader list, or a
  "changed" line that needs a reviewer.

**Tested on #329's own history:**
- **Passes:**
  - `main` `33828711` against #329's head `56e6b444`: 173 pins and 116 read groups rehashed, POUS's package unchanged;
  - my TL re-record, with its review.
- **Fails, as it should:**
  - the wrong run's review;
  - a package the review didn't cover;
  - TL's added pins;
  - synthetic changes to a signature, a reader list, one definition's hash, another key, or a SHA-256 value.

**POUS's `protocols/pous/lean`:** it stays on 32-bit records unless you add it to `R`, and the comparison covers it the same
way.
