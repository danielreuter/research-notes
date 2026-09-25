---
lane: verify-night-2
kind: handoff
from: coordinator
created: 2026-09-25T07:45Z
---

# red-team SH FAIL (R1/R2) on B-Ligero included-hash statements: strengthen your check, re-verify the published column

See lanes/coordinator/20260925T0735Z-handoff-from-red-team-standard-hash.md. For EVERY B-Ligero included-hash (v5/v6: +hash
Poseidon2, +blake3, +ajtai, sha256 rows) verification from now on, in addition to what you already do (you recompute the roots
from the instance set with the core, good):
1. check each statement's (vu_index, x_index, w_index) triple against the set's layout (unshared: x = W = vu) and the sub-batches'
   vu coverage of the claimed range;
2. recompute the trees' `binding` (hashauth.binding_digest(...)) and `count`, not just the roots;
3. say in each verdict that R1/R2 were checked this way.
Then re-verify, with that check, the five currently published "B-Ligero + in-proof hash" Table 2 cells (the column-2 artifacts in
the latest render: `~/.research/notes/campaigns/afternoon/render/0345Z-tables.md`, footnotes [4] [8] [12] [16] [20] or thereabouts)
and your 0715Z hash-commit verdicts. Report per cell: PASS (keeps its label) or FAIL (tell me at once: the cell gets pulled).

ADDENDUM 07:55Z (user decision): the five published cells are now marked in the scoreboard by a `finding` label
("UNDER RE-VERIFICATION: ...", by coordinator). When you finish each one, record the outcome as a new label on the same result
artifact: `research data label art:<id> finding "CLEARED R1/R2: <one line, verdict art>" --by verify-night-2` (the mark goes away),
or `... finding "PULLED R1/R2: <reason, evidence art>" --by verify-night-2` and a handoff to me (I then pull the cell).
