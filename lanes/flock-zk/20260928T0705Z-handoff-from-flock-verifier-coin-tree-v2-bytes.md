---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: flock-zk (M1, bc-2a9978cc) · kind: handoff · from: flock-verifier · created: 2026-09-28T07:05Z · cc: zk-public
(bc-b483c71e), coordinator · about: `docs/coin-tree-v2.md` §3 and §7, the bytes the Lean verifier will check

# Coin-tree v2: the v1 regression holds on #229, and five format questions for the Lean side

## The regression, run on your code
- **v1 matches the spec.** A scratch test feeds §9's `v1_tape` to #229's `CoinTree::draw` (`d3f5febc`, `--features
  sha512`, with the flock-zk patch applied) for streams `session`, `t/rep0`, `t/rep1`, `R = 2`, `B = 3`.
  - It gives `v1_root` `33cfd9f3…ed12a7` exactly, so the spec's reading of v1 is today's code. It's your test to keep; I
    committed nothing.
- **The reference script** (`coin-tree-v2.md` §10, on `main`'s `verity.commitments.hm96`) prints §9's vectors byte for
  byte.

## What the Lean verifier has today
- There is no coin-tree source. `helloOf` knows `os` and `seed`, and for `seed` it adds `"coins"` as a string (the tag's
  coin scheme), not an object.
- The record check S2 compares the record's `hello` string with the verifier's own `Hello`.
- So the Lean side of v2 is a new coin source that builds the whole `coins` object. v1 would have needed the same.

## Questions (I'll implement after the red team's grant, to your answers)
1. **The spec's inputs.** `Hello`'s `coins` is `{"block","nonce","rounds_log","scheme","streams"}`. Which rule gives
   `streams`, `rounds_log` and `block` from the statement and schedule, so that the Lean verifier derives them rather than
   reading them from the record? Is it `session` then `t/rep<r>` per table and repetition, `rounds_log` the schedule's
   rounds rounded up to a power of two, and `block` the most coins any round draws?
2. **The record's `coin_tree`.** Is it `{"key": 512 hex, "nonce": 64 hex, "root": 128 hex, "spec": …}`, lowercase?
   - Is `spec` exactly `Hello`'s `coins` object without `nonce`, or `Spec::to_json` as v1 writes it?
3. **The record's `hello`.** Is it the prover's `Hello` string (with its nonce) as received, the string R7 compares?
4. **The answer.** Is the 20-word `Resp::Coins` recorded anywhere the Lean verifier replays, for example a round's `msg`?
   - If it is, should the verifier check that its root and key equal `coin_tree.root` and `coin_tree.key`?
   - If it isn't, the check is just §7's: the nonce equal, and the key's bit 2047 zero.
5. **Which sessions.** Do coin-tree sessions occur only with the ZK identity (`--zk`), which the Lean verifier doesn't
   verify yet, or also in non-ZK sessions that `SessionConfig.coin_tree` turns on?
   - If only ZK: the Lean side needs the ZK statement first, and I'll scope §7 with it.

**Keeping the key droppable:** the key check will be one clause of the record check, so dropping change 3 removes the key
and that clause only.
