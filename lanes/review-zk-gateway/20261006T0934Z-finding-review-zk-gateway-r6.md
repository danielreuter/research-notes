---
id: review-zk-gateway/20261006T0934Z-finding-review-zk-gateway-r6
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1323@12d84d3e824032f8c8647be1db7a9e58352d2f5f, pr:1303@65ab946f0b80a38236a98c638f04c2e4184a77f7]
---

# Red-team round 6: #1323 at `12d84d3e8` NO-GRANT; #1303 at `65ab946f0` GRANT

The detail, probes, transcripts and outputs are in the store's `private/red-team-reviews/1323/` (`review-r6.md`, `r6-*`)
and `private/red-team-reviews/1303/` (`r6-*`).

**The audit:** `r20261006-091429-b73a`, on vy-nebius-2 (CPU), in the run's own clone of `12d84d3e8` with a fresh `.lake`.
- PASS: 6,097 declarations in 51 modules, `propext`, `Classical.choice` and `Quot.sound` only, no `sorry`, 14 guarantees.
- Kernel replay: 6,028 constants accepted.
- Pins and reads equal the committed file, and the tree is clean after.
- #1303's Lean subtree at `65ab946f0` is `1f6a738f9`'s, so this audit covers it.

## #1323 (`cursor/firewall-contract-95d4`): NO-GRANT

**Holds:**
- `lean-audit.json` is additive: 7 new pins and 3 read records grow; `Flock.Hm96`'s digest moves only with its 11 added
  definitions. No existing pin or definition hash changes.
- Coins: an opening is refused, and relayed must equal the challenger's.
- `FirewallComputes` is a hypothesis only of `holds_computed`.
- The recorder logs the calls as made, refused ones included. Each of the six tamper controls differs from the honest
  transcript only in its named part, and splicing the honest part back is accepted.
- The 12-session finding reproduces. With `74b2c0d3a`, and with `65ab946f0`, merged in scratch: 1,277 of 1,277 released
  item for item, and the four test files pass, 70 tests.
- `git merge-tree` is clean onto `1f6a738f9` and onto `65ab946f0`. No circuit Definition, template or lowering.

**Blocking.** A transcript that leaks one bit is accepted in 11 of 11 probes:
- **B1. Commitment count and placement are free.** An extra, a dropped and a moved commitment are each accepted.
  - Fix: `State.owed`, set from the schedule item's node and row counts. `commit` needs `owed > 0` and decrements it; every
    other item needs `owed = 0`.
- **B2. Freshness and exposure are checked by tape id, not value.** Reused salt bytes under a new id, a salt shown under
  another id, and a pad shown under another id are each accepted.
  - Fix: `run` refuses tape salts or pads that aren't pairwise distinct; state it in `holds_commit` and `holds_masked`.
- **B3. The public statement comes from the transcript.** All four are accepted: its own `schedule` (a bit in Hello),
  its own or empty `relations` (rule (b) is vacuous), and any `by: statement` value.
  - Fix: `run` and `Holds` take the verifier's public input (schedule, relations, statement values) as a separate
    argument, `contract --public FILE`, and `firewall_agree` passes `SCHEDULE` or `schedule_for`. Refuse `statement` until
    it is an input, and refuse masked values when there are no relations.
- **B4. The body overstates the theorems.**
  - `holds_commit` has no freshness conjunct: prove it, or drop "fresh".
  - `holds_fixed`'s non-schedule values are the transcript's own `want`, not "the one its source fixes".
  - "`firewallLeaf` is the leaf rec-thm's `gatewayLeaf` states" is unproved: `gatewayLeaf` is `ZkView.leafH`-based and
    joined only by rec-thm's `leafSplit`. Reword it.

**Not blocking:**
- Which own, recheck and shadow items appear is free.
- `FirewallComputes`' `spec` is a free parameter, and the audit records `holds_computed`'s `assumptions` as `[]`.
- Check outcomes are self-reported.
- Exposure is detected only literally.
- Salts are fresh only within a session.

**What the outer-phase exporter must cover:** public inputs (schedule, relations, statement values) from the verifier, never
the transcript; each commitment, masked, check and own item at the position and count the skeleton fixes; value-distinct
salts and pads; and `FC_GATE_TAMPER`'s controls through the contract.

## #1303 (`cursor/firewall-contract-741b`): GRANT at `65ab946f0b80a38236a98c638f04c2e4184a77f7`

**Holds:**
- The delta since R3 is `1f6a738f9` (the Lean open moved to the stream's first round, plus `calls`), `65ab946f0` (calls
  recorded before they are judged) and two clean merges of #1270.
- The rest of #1303's own diff is byte-identical to R3's grant.
- The exhaustive Open-placement probe now compares calls too. Over 528 sessions, proxy and Lean agree on every record and
  call list, and the coin server sees 9 views (8 stop points and the finish).
- 69 tests pass.
- Mutations bite. Reverting the Lean move fails 2 tests. Dropping the proxy's stray-call guards fails at `65ab946f0` and
  passes without R4.
- R3's findings hold; its theorem-over-`record` caveat is moot.
- The body is current. Lean's three asks are done: `74b2c0d3a` merged, the dispatch accepted, refused calls logged.

**Carry:** the grant carries across a further merge of `cursor/zk-gateway-95d4` only while #1303's own diff on its seven
files stays byte-identical.
