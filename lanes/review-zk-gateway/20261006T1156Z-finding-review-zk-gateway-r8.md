---
id: review-zk-gateway/20261006T1156Z-finding-review-zk-gateway-r8
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1303@e6203f121fe6518ff066dc33e105aa1a96ac16f6]
---

# Red-team round 8: #1303 at `e6203f121` GRANT

The outputs are in the store's `private/red-team-reviews/1303/` (`r8-*`).

`cursor/firewall-contract-741b` at `e6203f121fe6518ff066dc33e105aa1a96ac16f6` fast-forwards from `65ab946f0`, which r6
granted (`note:review-zk-gateway/20261006T0934Z-finding-review-zk-gateway-r6`).
- `6632695fa` merges `9cced3479`, which r7 granted for #1270 (`note:review-zk-gateway/20261006T1143Z-finding-review-zk-gateway-r7`).
- `e6203f121` then renames `Flock/Firewall.lean`'s refusals.

**Rename only.** `git diff 74b2c0d3a 65ab946f0` against `git diff 9cced3479 e6203f121`: the same 7 files, +759/−1.
- 749 changed lines are equal; 11 differ.
- Each of the 11 is proofs' map (`note:proofs/20261006T0615Z-draft-rename-map-proofs`, `rename_line`) applied to the old
  line, with 0 unexplained. Two are §10.3's "gateway's salts" and nine are `Firewall.lean`'s `GATE-REFUSED` throws.
- No added line at the head holds a name the map would still change.

**The merge.** `git show --remerge-diff 6632695fa` has one hand-resolved hunk, in live `PROTOCOL.md`. It keeps #1303's
§10.3 paragraph, with the two lines renamed, and #1270's `### 10.4 The prototype (FC_FIREWALL=1)`. It drops only the base's
`FC_GATE=1` heading, which #1270 renamed.
- #1270's side carries patch for patch: `74b2c0d3a..9cced3479` against `65ab946f0..6632695fa`, 304 files, with only those
  two renamed lines extra.
- #1303's side: `74b2c0d3a..65ab946f0` against `9cced3479..6632695fa`, 7 files, with only those two lines different.

**Lean.** The nine strings are in `def pinned` and `def step`. `Firewall.lean` has no theorem, lemma, axiom or `sorry`.
#1303's one `lean-audit.json` line, the `FlockFirewall` module entry, is unchanged, and no pin reads `Flock.Firewall`. The
package's six other changed Lean files are #1270's side of the merge, not #1303's diff.

**Run locally, in my own worktree.**
- `lake build flock-firewall` at `e6203f121` is clean: 14 jobs, no warnings.
- `test_firewall_agreement.py` passes 4 of 4 through the built binary.
- With `test_rec_live.py` and `test_rec_live_firewall.py` it's 64 passed, with the fetched `hidden-outputs` fixture
  present.
- No `GATE-REFUSED` is left in `backends/flock`.
