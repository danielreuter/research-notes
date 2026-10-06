---
id: review-zk-gateway/20261006T0813Z-finding-review-zk-gateway-r4
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1270@498f4cf64b4a5404e6d9514506d07d68b2ef7bea]
---

# Red-team round 4: #1270 at `498f4cf64b4a5404e6d9514506d07d68b2ef7bea`: NO-GRANT

Row G3 (firewall-contract's gap 3) is right: `78a2d42da..498f4cf64` is exactly the described change, and at the call
level no Open placement, order or cut reaches the coin server (0 departures from the honest prefix on two-rep and
parent-and-child schedules; nothing added at K = 4096). Tests 64 passed; the new test fails against 78a2d42da; finished
records and `schedule_of` are unchanged on the three schedules.

No grant, because under the calls model the PR now adopts, other refused requests still reach the coin server:

- A stray `Commit` (before Hello, or any after the first) makes a refused `coins.commit` call. Required: the proxy
  refuses it before any call, as `Flock.Firewall.run` does.
- A stray `Link` (before Commit, or a second) makes a refused `coins.y` call. Required: the same pre-check.
- A refused `Finish` reads `coins.record()`. Required: pin Finish from the proxy's own counts, as `Firewall.run` does.
- At K = 4096 these give 1124 inner endings (846 without the read) where §10.5 counts 288, so 12.1 / 80.1 do not hold at
  this head (12.35 / 82.10). With the fix: 284 endings, and both bounds hold as upper bounds.
- Required test: one stray Commit, Link or Finish at every point of a two-rep session gives a prefix of the honest calls,
  and the test fails at 498f4cf64.

A scratch fix of about six lines passes all three test files and closes the probe. The detail, probes and counts are in
the reviewer's private store (`red-team-reviews/1270/review-r4.md`).

The PR body is accurate on G3, gap 3's cases, and the tests. Its lead and its "§10.5's bound stays an upper bound"
sentence are true only once the fix lands.

The r3 grant at 78a2d42da does not carry to this head. The next head needs its own grant, after which the 09:00Z
rename-only restack carries it.
