---
id: review-zk-gateway/20261006T0728Z-finding-review-zk-gateway-r3-1303
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1303@56abe283cb5d90a7ddfb9960b1eced452574c4e5]
---

# Red-team round 3: #1303 at `56abe283cb5d90a7ddfb9960b1eced452574c4e5`: GRANT

This round re-checked only `6336c6a7d..56abe283c`. It follows
`note:review-zk-gateway/20261006T0701Z-finding-review-zk-gateway-r2`, whose condition R1 this head meets on the Lean side.
#1270's half was granted in `note:review-zk-gateway/20261006T0711Z-finding-review-zk-gateway-r3`. Probes, logs and mutation
outputs are in the store's `private/red-team-reviews/1303/` (`r3-*`).

**The diff is the three parts lean named, and nothing else:**
- The merge `694c34a97` (parents `6336c6a7d` and `78a2d42da`) changes the same lines as `d828d3ea9..78a2d42da`, which I
  granted. The merged tree minus `78a2d42da` is #1303's reviewed diff.
- `56abe283c` touches only `Flock.Firewall.record` (the filter) and `test_firewall_agreement.py` (six cases and one test).

**The filter matches the proxy's rule.** `named` keeps a stream only if it has an entry in `counts`, and `counts` gets one
only at the stream's first `.round`. That is the proxy's `if self.streams[s]["rounds"]`.

**The open-order probe, through `flock-firewall`:**
- The r2 cases now give `streams=[]` for every stop before a stream's first round, with and without an early Open, and Lean
  agrees with the proxy.
- Exhaustively, on a two-rep schedule shaped like `schedule_for`'s: 528 sessions, covering every placement of both Opens and
  every stop point, give 8 distinct stopped records in Lean and in the proxy. That is exactly the fixed sequence's stop
  points, and the two agree on all 528.

**The mutations bite:**
- With the Lean filter reverted, the agreement test and the new test fail, as lean says.
- With only the proxy's filter reverted, the agreement test fails.

**Reruns:**
- `test_firewall_agreement.py`, `test_rec_live.py`, `test_rec_live_gateway.py` and `test_rec_vstar.py`: 66 passed.
- `tools/lean/audit.py --build backends/flock/verifier/lean`: PASS, 5813 declarations in 48 modules, axioms `propext`,
  `Classical.choice`, `Quot.sound`, 7 guarantees.
- Both ran on CPU in a fresh checkout with its own `.lake`.

**The PR body's two should-fix sentences are accurate:**
- "The contract is `run` … the type alone admits any value in those fields".
- "`commit` draws salts in the order the worker's `Commit` lists its tables". Both `Firewall.lean` and `rec_live` draw them in
  the worker's order.

**Not blocking, for lean's next round:**
- PROTOCOL.md §10.3 still says "Its message type is the contract", which the PR body now corrects. It is a one-sentence doc
  fix after the restack.
- State the planned theorem over `record (run …)`, not over `run`'s `Sent` sequence. That sequence still holds each
  `openStream` where the worker sent it; only the record drops it.
- For a stopped session, the theorem must also take where the session stopped (the count of fixed-sequence messages
  accepted), not only the schedule, the salts and the committed values.

**Rename restack:** the grant carries to a head restacked onto #1270's renamed head if its diff against `56abe283c` is only
the rename (`gate.rs` → `firewall.rs`, `FC_GATE` → `FC_FIREWALL`, `GATE-REFUSED` → `FIREWALL-REFUSED`, `gate_*`/`Gate*` →
`firewall_*`/`Firewall*`: identifiers, strings and file names, no logic), including the same rename brought in from #1270.
The `GATE-REFUSED` strings in `Firewall.lean` count as rename. Anything else, the §10.3 sentence fix included, reopens the
review of what it touches.
