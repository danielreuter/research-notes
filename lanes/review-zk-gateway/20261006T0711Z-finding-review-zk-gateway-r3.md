---
id: review-zk-gateway/20261006T0711Z-finding-review-zk-gateway-r3
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1270@78a2d42dac462817ec3f435b1194dbb026cae72c]
---

# Red-team round 3: #1270 at `78a2d42dac462817ec3f435b1194dbb026cae72c`: GRANT

This round re-checked only `d828d3ea9..78a2d42da`, one commit by proofs. It follows
`note:review-zk-gateway/20261006T0701Z-finding-review-zk-gateway-r2`, whose condition R1 this commit meets. Everything
else at `d828d3ea9` was cleared in r2. Probes and outputs are in the store's `private/red-team-reviews/1270/` (`r3-*`).

**The diff:**
- `CoinServer.record` lists a stream only once it has a round, with a docstring line.
- §10.3's stream row and §10.5's message-order paragraph say so.
- `test_rec_live_gateway.py` adds a test that a stopped record does not show whether or when an Open was sent.
- Nothing else changes.

**R1 is met:**
- My Open-order probe, against the Python proxy: at the same stop point, the records with and without an Open (sent first
  or last) are now identical, and so are the two-stream ones.
- An exhaustive version on a two-rep schedule shaped like `schedule_for`'s: 528 sessions, covering every placement of both
  Opens and every stop point, give 8 distinct stopped records. That is exactly the stop points of the fixed sequence. At
  `d828d3ea9` the same sessions gave 22.
- So §10.5's count (`s_p + 2` endings for the inner phase) and its bounds (12.1 / 80.1 bits) hold.
- The new test fails against `d828d3ea9`'s `rec_live.py` and passes at the head.

**Tests:** `test_rec_live_gateway.py`, `test_rec_live.py` and `test_rec_vstar.py` give 63 passed.

**Finished records and `schedule_of` are unchanged.** I drove synthetic honest sessions through both `rec_live.py`
versions: the tests' schedule, a parent with a child stream, and `schedule_for`'s K = 4096 schedule (285 requests). All
finish, their records and `schedule_of` are equal under both versions, and `schedule_of` gives back the schedule's streams
and rounds. Every scheduled stream has rounds, because `rep_rounds` always starts with the binding round.

**Not blocking:** `check_schedule` still accepts a stream with 0 rounds, and a session can no longer finish against such a
schedule. That is unreachable through `schedule_for`, and it fails closed. Refusing such a schedule would make it explicit.

**Rename restack:** the grant carries to a restacked head if its diff against `78a2d42da` is only the rename (`gate.rs` →
`firewall.rs`, `FC_GATE` → `FC_FIREWALL`, `GATE-REFUSED` → `FIREWALL-REFUSED`, `gate_*`/`Gate*` → `firewall_*`/`Firewall*`:
identifiers, strings and file names, no logic). Anything else reopens the review of what it touches.

#1303 is not in this round; it waits on lean's rebase onto `78a2d42da` and the same filter in `Firewall.record`.
