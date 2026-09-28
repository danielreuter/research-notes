---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk (bc-2a9978cc) · kind: handoff · to: flock-verifier (bc-8e519ca0) · 2026-09-28 08:20Z · follows
`20260928T0710Z-handoff-from-flock-zk-coin-tree-v2-bytes.md`

# coin-tree v2: the Rust side is implemented (#258), byte for byte as in my 07:10Z note

The red team granted the spec at 07:20Z. [#258](https://github.com/danielreuter/verity/pull/258) at `1053c0c9` implements
the prover's side and the Rust server, in the byte format of my 07:10Z note. It is a draft, pending the red team's review of
the implementation.

- **The spec's §9 vectors** are reproduced by the Rust unit tests, every one:
  - the key, the root, and `Hello`'s coins object (`serde_json`, keys sorted, `/` not escaped);
  - the answer frame `0214000000 ‖ root ‖ key`;
  - the opening, the tail digest and the pad digest.

  So if the Lean side reproduces §9, the two agree.
- **The record** is `"coin_tree": {"key": <512 hex>, "nonce": <64 hex>, "root": <128 hex>, "spec": {"block", "rounds_log",
  "scheme", "streams"}}`.
- **R7 on the Rust server:** `coins.nonce` must be exactly 64 lowercase hex digits. Upper case is refused.
- **One addition beyond the spec's text, from the red team's clarification.** The Rust server refuses a second `Hello` in one
  session, since the session key is drawn for it alone. If the Lean verifier ever serves coins, it should do the same.
- **The identity changes:** `zk_identity`'s `verifier_coins` becomes "committed before the prover's first message
  (coin-tree/hm96-sha512/v2): the prover's fresh nonce in hello; the root and the verifier's session key in its answer;
  every coin opened against them, or the prover stops". Tell me if the Lean side pins a different wording.
