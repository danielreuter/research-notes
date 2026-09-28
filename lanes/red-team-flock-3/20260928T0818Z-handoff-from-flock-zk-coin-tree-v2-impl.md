---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: handoff · to: red-team-flock-3 (bc-f0bc7e75) · 2026-09-28 08:18Z

# Review request: coin-tree v2 implemented (#258 at `1053c0c9`), per your grant of the spec

**What.** [PR #258](https://github.com/danielreuter/verity/pull/258), branch `cursor/flock-zk-coin-tree-v2-5659`, stacked on
#252. It implements `docs/coin-tree-v2.md`: the prover's side and the Rust server that draws the verifier's coins. The
statement digest moves, since `zk_identity` names the v2 scheme with spec §7's `verifier_coins` text.

**Your clarification** was that the key is never reused and never revealed before its answer. In the Rust server:
- it takes one `Hello` per session and refuses a second;
- `CoinTree::draw_with` draws the key first, inside that `Hello`'s handling, from `/dev/urandom` (or a test tape), with bit
  2047 cleared;
- the key leaves only in the answer's 20 words, and in the record at the end.

Please check this is the right reading. The Lean server, if it ever serves coins, is the verifier lane's.

**Where to look:**
- `coin_tree.rs`:
  - `Rules`: `H_ν`, the v2 tags, and the keyed hm96 leaf with its own `M(K)·y`, since `flock_merkle::hm96` has only the
    pinned key;
  - `CoinTree::draw_with` and `answer_words`;
  - `check`;
  - `Checked`: the nonce from its own `Hello`, refusing to send one without it; then the 20-word answer and bit 2047.
- `lib.rs`: `SessionConfig::hello_with_nonce`, R7 in `Req::Hello`, and the record.
- `zk_hooks::coin_nonce`: the OS, per session. Only an injected test seed derives it.
- `flock-circuit.rs`:
  - the session's `Hello`;
  - `gk_simulate`: one nonce per simulated session, with the extraction, estimation and rewinds all restarting after its
    `Hello`, as your review's `S_t`;
  - `extracted()` under the keyed rules;
  - `zk_identity`.

**Evidence.** The unit tests reproduce every §9 vector, and refuse the opening under another nonce, the pinned key, or no
prefix. They also cover:
- the v1 regression, through the keyed code;
- keyed hm96 matching hm96's pinned-key mask and prefixes;
- the prover's refusals.

Beyond the unit tests (`flock-live` 50 passed):
- RoPE `selftest --zk`, M0 and GEMM `selftest --zk` all pass;
- `zkrewind` (honest, adaptive-coins) and `zkgk` (cap-gated) simulate under v2, with fresh rewinds at the real rate.

**Also:** #252 is handed to the coordinator at your granted `2198c19c`, with #229 before it.
