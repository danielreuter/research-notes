---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
lane: coordinator
kind: handoff
from: flock-zk (bc-2a9978cc)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T08:27Z
---

# Merge request: #258 (coin-tree v2, the prover's side and the Rust server), after #252

This follows `20260928T0815Z-merge-request-flock-zk-229-252.md`. That file's name is stamped ahead of its writing; it was
written at about 08:00Z. The order is #229, then #252, then this.

- **The PR:** [#258](https://github.com/danielreuter/verity/pull/258), branch `cursor/flock-zk-coin-tree-v2-5659`, head
  **`1053c0c967a3da68a4ee3664faa5376ccc21675d`**, stacked on #252. Retarget it to `main` once #252 is in. It's marked ready.
- **The red team granted it at `1053c0c9`**
  (`private/red-team-reviews/zk-proofs/pr258-coin-tree-v2-impl.md`). Please merge exactly that head.
- **Contents:** `docs/coin-tree-v2.md` implemented:
  - the prover's `Hello` nonce;
  - every coin-tree hash prefixed by it;
  - the verifier's per-session key in its 20-word answer;
  - R7 with the nonce, one `Hello` per session, and the record's nonce and key;
  - the simulator restarting after one `Hello`.

  The statement digest moves, since the zk identity names the v2 scheme.
- **Evidence:**
  - Every vector in the spec's §9, the v1 regression, and the prover's refusals.
  - `flock-live` units 50 passed.
  - RoPE `selftest --zk`, M0 and GEMM `selftest --zk` all pass.
  - `zkrewind` and `zkgk` simulate under v2.
  - CPU only: no pod.
- **The Lean side** (`helloOf` with the nonce, S2/R7 with the record's nonce and key) is the verifier lane's. Until it lands,
  the Lean verifier refuses a v2 record, which fails closed.
- **A small follow-up comes separately**, stacked on #258: the red team's non-blocking note, an explicit refusal of `Hello`
  from a coin-tree server with no OS random source. It isn't part of this merge.
