---
id: review-zk-gateway/20261006T0701Z-finding-review-zk-gateway-r2
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1270@d828d3ea999e6ab657b666e3f6cba9c08d40d0d0, pr:1303@6336c6a7dc62d7c87fa8a69db2b00cbc1c0104ed]
---

# Red-team round 2: #1270 at `d828d3ea9`: NO-GRANT; #1303 at `6336c6a7d`: NO-GRANT

Both verdicts rest on one shared condition, R1. Everything else asked of both PRs checks out. Detail, probes, logs and a
scratch fix: the store's `private/red-team-reviews/1270/review-r2.md` and `private/red-team-reviews/1303/review.md`.

**#1270 (the gateway, `cursor/zk-gateway-95d4`)**
- Round 1's items 1–6: each fix's tests fail with `rec_live.py` taken from its parent and pass at the commit, as in the PR's
  table.
- Item 7 (§10.5), S1, S2, S3 and the remaining panics: confirmed by reading.
- `backends/flock/tests -k 'rec or live or pod or gate'`: 116 passed, 5 skipped.
- §10.5's message counts (2326 at K = 4096) match `r20261006-054828-66ea` (art:c239c372).
- "Not in this PR" is not blocking once R1 holds.

**#1303 (the firewall contract in Lean, `cursor/firewall-contract-741b`)**
- The agreement test bites: one mutation of `Proxy` and one of `Flock.Firewall.run` each fail it.
- It adds no `partial def`, `sorry` or axiom; the Lean audit passes (5812 declarations, 7 guarantees unchanged); and
  `lean-audit.json` adds only the entry-point exemption.
- The outer phase is out of scope, as stated.
- On what `run` sends, it matches §10.3 except for R1.

**Condition (both PRs)**
- R1: a stopped inner session's public record must depend only on where the session stopped. Today it also reflects a choice
  the worker makes that the schedule does not fix. Fix it in `rec_live` and in `Flock.Firewall.run` together, with a test
  each. A one-line fix exists, and the private detail has it. Until then, §10.5's stated bound (12.1 / 80.1 bits) slightly
  understates what holds today.

**What a re-review needs (the 09:00Z rename restack)**
- #1270 can be granted if its new head's diff against `d828d3ea9` is only the rename (identifiers, strings and file names,
  no logic), the R1 fix and its test.
- #1303 can be granted if its diff against `6336c6a7d` is only the rebase onto that head, plus the matching R1 fix in
  `Firewall.lean` and its agreement cases.
- Anything else in either diff reopens the review of what it touches.

No labels were written (no grant).
