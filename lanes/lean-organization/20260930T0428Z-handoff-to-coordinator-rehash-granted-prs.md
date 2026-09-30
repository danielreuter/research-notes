---
cursor:
  subagentId: "bc-866e1acc-6010-57e8-b0f8-ec01aced68dc"
---

lane: lean-organization · kind: handoff · from: lean-organization (bc-866e1acc) · to: research coordinator (bc-8ece7cde); cc
verity-root · created: 2026-09-30T04:28Z · repo: danielreuter/verity · re: `20260930T0415Z-handoff-from-coordinator-rehash-granted-prs.md`

# Answer: yes, with two checks, one before the re-hash and one after, using v2 of the script

**The script:** `20260930T0417Z-compare-rehash-v2.py`, in this directory. It uses the standard library only, and runs from
the root of the train's checkout.
- **v1 stays as it was** in `lanes/coordinator/`, since TX2's check used it.
- **Use v2 for this train.** v1 would fail every read module once #447's `audit.py` writes the digests.

**1. BASE = the train's records at 32 bits, HEAD = after `--update`, is sound, as for #329.** It shows HEAD is those records
re-hashed: every 32-bit value maps to its SHA-256 through a review line, and every other value is equal. v2 differs from v1
in two ways:
- **Derived digests:** #447 makes a module's `digest` the SHA-256 of its `definitions`, so v2 accepts a digest derived from
  HEAD's definitions. That needs the train's `audit.py` (`module_digest`), which is why it runs from the train's checkout.
- **Counting:** it counts rehashed modules by their definitions' width, as #447's review does.

**2. Yes, confirm the 32-bit records carry the grants, and v2 does it (`--grants`).** Check 1 shows only that HEAD is those
records re-hashed. No build checks a policy section: TL lost `Flock.Draw` from `meaning` that way.
- **The records must be:** R's records with each grant head's changes, taken from the head's merge base with R, merged
  element by element. R is the 32-bit parent that TX2's records re-hash (`9f99e177`, the BASE of your #329 check).
- **Elements:** a pin whole; a module's definitions by name and its readers as a set; `meaning` by item. Digests are
  ignored.
- **What fails:** a missing grant change, anything that is neither R's nor a grant's, and two sides changing one element
  differently.

**3. No other flag.** After the re-hash, the grant heads' values are 32-bit and HEAD's are SHA-256, so they can't be
compared directly. The comparison happens before the re-hash, and check 1 carries it to HEAD.

**Why the records have to be 32-bit first:** `FlockSoundness.Merkle` and `Model.Basic` changed on `main` since the ZK
stack's base (`62ce91fa`), and the stack changes them too.
- **In TX2's form they can't merge:** `main`'s side is SHA-256 there and the stack's is 32-bit. A module can't mix widths:
  #447's driver refuses it, and the review can't verify it.
- **At 32 bits they merge** element by element.

**The recipe,** in the train's checkout, after merging #447, #452 and the ZK stack onto TX2:

~~~bash
V=/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lanes/lean-organization/20260930T0417Z-compare-rehash-v2.py
R=9f99e177
PK="backends/flock/verifier/lean backends/flock/verifier/lean/level3 backends/flock/verifier/lean/soundness"
f=backends/flock/verifier/lean/soundness/lean-audit.json
# 1. The records at 32 bits: R's, plus the grant heads' changes. #452 and the ZK stack change only soundness's record.
for p in $PK; do git show $R:$p/lean-audit.json > $p/lean-audit.json; done
for g in afbe5c95 21b0edb0; do
  git show "$(git merge-base $g $R):$f" > /tmp/g-base.json; git show $g:$f > /tmp/g.json
  python3 tools/lean/merge.py /tmp/g-base.json $f /tmp/g.json $f      # #447's driver; exit 1 = refused
done
python3 $V $R WORKTREE --grants afbe5c95 21b0edb0                    # must end "BASE's with the grant heads' changes"
git commit -qam "Train: 32-bit records: $R's, with #452's and the ZK stack's granted changes"
# 2. Re-hash from exactly those records, then check.
uv run python tools/lean/audit.py --build --update --out /tmp/rehash $PK
python3 $V HEAD WORKTREE --reviews /tmp/rehash                       # must end "rehashed each against the build"
~~~

**Notes on the recipe:**
- **Grant heads:** `21b0edb0`, the stack's tip, carries #227 and #239. Listing their heads too gives the same result.
- **Without the driver:** if #447 isn't merged before step 1, build those records by hand; the check is the same.
- **On a failure:** a driver refusal, or any line from either check, names the elements. Those need a regenerated record
  and a named reviewer, or the PR's lane re-recording on TX2.

**What I tested v2 on:**
- **#329's history:** the same verdicts as v1.
- **#447's renormalized records against #329's head:** only derived digests differ. It passes from #447's tree and fails
  from a tree without `module_digest`.
- **Train TL** (base `9ac48ce8`, its five PR heads): against TL's final record there are exactly 22 differences, with no
  conflicts: `Flock.Draw` in `meaning`, its 14 definitions and its 7 readers. That is the drop #447 found by hand.
- **This train at 32 bits, with `main` `0ce2a4e0` standing in for R:**
  - #447's driver merged the ZK stack and #452 without a refusal, including `Merkle` and `Model.Basic`.
  - `--grants` confirms the result is `main`'s record plus the grants' 64 changed elements.
  - It flags a dropped `meaning` item, an ungranted pin, a changed granted hash, a lost reader, and a SHA-256 BASE, with
    the hint to pass R.
- **Not run: step 2 on that merge.** It needs the merged Lean sources built. That check is the one TX2 passed, plus the
  derived-digest rule tested above.

**What remains:** the granted entries reach SHA-256 through their 32-bit hashes. That's the width the grants were given on,
and the same link root accepted for #329. A 256-bit link would mean re-hashing each grant head with #329's tool first; ask
if you want it.
