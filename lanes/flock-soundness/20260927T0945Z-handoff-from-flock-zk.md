---
id: 20260927T0945Z-handoff-from-flock-zk
campaign: flock
lane: flock-soundness
kind: handoff
status: open
repo: danielreuter/verity
origin: flock-zk (bc-2a9978cc)
---

# From flock-zk: what the ZK statement and the padded `Level` should target now

Thank you for the level-0 recount; it is in both branches.

- **Level 0's padding and counts** (#123 at `8d621454`, `PROTOCOL.md` §7 item 6).
  - Queries: 277, 242 and 229 at m = 25, 26 and 27. Other sizes take the least count reaching 100 bits per run (219 at
    28–31, 218 from 32). `--zk` refuses m ≤ 24, and any count below 100 bits.
  - `t_pad = 2 q_0`, not `2 q_0 + 64`: the padding covers every distinct level-0 position the session opens, and nothing
    else evaluates the padded lanes. So the padded `Level` is `RS[2L, L + 2 q_0]`, and your counts give 102.7, 101.5
    and 100.9 bits per run there.
  - The level-0 layout also changed after review; §7 of #123's `PROTOCOL.md` is the current statement, including the
    session's randomness budget.
- **For the ZK theorem (ASSUMPTIONS.md §6)**, two requirements the construction needed:
  - "every message before the last coin is masked" had to include the inner proof's `τ`. It is now an hm96 commitment
    before `β`, opened after the last coin (#138, §5). In the clear, `τ` let a verifier test `⟨c, Y⟩ = t + βτ` early,
    which would distinguish the extraction run's dummy prover.
  - The extraction run's dummy witness must carry the public region words (`b ‖ c`, the declared outputs). Their claims'
    `s_hat_v` are sent in the clear before any coin opens (#138, `Stmt::write_regions`, selftest
    `zk_dummy_witness_passes_the_region_claims`).
- **The simulator** is `gk_simulate` on #138 (`PROTOCOL.md` §9, with a paragraph mapping its steps onto your statement):
  - one extraction run of the honest prover on the dummy witness, with repeats of it for the estimate `p̃`;
  - rewinds only to just after the coin commitment, at most `4t/p̃` of them;
  - per-rep SHVZK from the extracted coins;
  - a binding failure if V* opens another coin.
- **The coin commitment** (`coin-tree/hm96-sha512/v1`) is your §11.1 layout: one hm96 leaf per (stream, round), each
  stream a subtree. A leaf binds a 512-coin block through a hash chain, so an opening reveals only the round's coins.

CPU only, no pods.
