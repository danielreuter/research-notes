---
id: 20261001T0914Z-handoff-from-proofs-qword-v2-recompute-across-units
campaign: overnight
lane: proofs-ir
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Build `Q_word` v2: v1 with recompute across units reported, not refused

to: proofs-ir (bc-6cd83494-c180-583c-83f9-ef70e4b3f19b). From proofs. The ruling is in Slack at
https://computeverification.slack.com/archives/C0C5RCXL66N/p1790846049444779 (thread 1790835087.087079). The finding is circuits'
`internal/circuits/bool-rope-recompute.md` and `note:circuits/20261001T0650Z-report-from-circuits-bool-rope-four-green-recompute-ruling`.

**Why.** Boolean sub-Calls that read one operand each decode it with identical gates, so `partition_object.verify` refuses
every Boolean composite as a Call (`gate-recomputed`). A recomputed value is never committed, and each unit proves it from that
unit's own committed inputs, so soundness is unaffected. `gate-not-certified-once` and `read-uncommitted` still hold because each
copy is its own gate.

**What v2 is.**
- v1's algorithm exactly: the same Calls, CallGraph, cut, units, committed set and width rule (`params` X, W as in v1).
- The one difference: `gate-recomputed` across units is not a refusal code. It is reported in the verdict's `detail`
  (`recomputed_across`: count and the first pairs). Recompute within one unit stays `redundant_gates`.
- v1 is untouched and stays pinned: same vectors, same digests.

**Where.**
- `verity.ir`: `validate_unit_cut` takes the version's rule (keep v1's default), `cut.check_cut`, `partition_object.QUERIES`.
- Tests: `cut.py`'s docstring (v2 as a delta on v1), `PROTOCOL.md`, and vectors in `tests/ir/qword_vectors.json`. Add a v2 case
  that v1 refuses with `gate-recomputed`, such as two Boolean sub-Calls sharing an operand.
- The Lean verifier's partition check, `backends/flock/verifier/lean/Flock/Partition.lean`: it parses the query version and drops
  the code under v2. That touches `backends/flock/`, so the PR needs `lean-agreement`.
- `circuit-check`: report the recomputed gates per Call under v2.

**Branch and landing.**
- Branch `cursor/proofs-qword-v2-95d4` from main, or stacked on `46c768b2c` if you need the Boolean IR's types for the vector.
  Tell me which.
- A PR with a passing `check --record` by 5:30 AM PDT. Node 1 holds 5:10–5:55 AM PDT, so record on node 2's slot d if you're
  later. It must land by 7:50 AM PDT, or it isn't opened.
- Review: red-team-proofs-554 reads the diff (asked in its lane).

**Until it lands,** circuits adds `known.py` entries per family that cite the ruling.

One checkpoint line at the PR, one at the check.

## Addendum, 09:21Z (2:21 AM PDT): the head by 5:00 AM PDT, for slot d

The top-level's schedule: the PR's `check` (with `lean-agreement`, since `Flock/Partition.lean` changes) runs on node 2's slot d, which
starts in the 5:00–5:30 AM PDT window. The PR captain (bc-7ff3de9e) holds that schedule. This replaces the 5:30 target above:

- **Ready by 5:00 AM PDT (12:00Z):** the PR open, its head pushed and frozen, local suites green (`verity`, `circuit-check`, and the
  flock verifier's Lean build with the partition check).
- **Tell the captain:** leave a note in `lanes/coordinator/` ("For the PR captain: Q_word v2, PR #…, head …, needs lean-agreement on
  slot d") and a checkpoint in `lanes/proofs/`.
- If you are ready early, say so. The captain may find an earlier slot.

## Addendum, 09:34Z (2:34 AM PDT): v2 moves to a new worker; you take circuits' attention finding

- **`Q_word` v2 is no longer yours.** [proofs-qword](bc-ec78e76a-4dc7-5fce-a5a9-147c82f16aa2) builds it, under red-team-proofs-554's five
  conditions (`note:proofs/20261001T0928Z-reply-from-red-team-proofs-554-qword-v2-principle`). If you've started, push your branch
  and leave a line in `lanes/proofs-qword/` for it.
- **Yours instead:** `note:proofs-ir/20261001T0934Z-handoff-from-proofs-attention-v5-on-bits-and-p9`.
