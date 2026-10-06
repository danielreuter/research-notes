---
id: review-zk-gateway/20261006T1348Z-finding-review-zk-gateway-r9b
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1323@888c567720185bdeccb2a86d12539146ef8ebde9]
---

# Red-team round 9′: #1323 at `888c56772` GRANT (rename only)

Round 9 granted `5f2fb2322` (`note:review-zk-gateway/20261006T1227Z-finding-review-zk-gateway-r9`). The head is now
`888c567720185bdeccb2a86d12539146ef8ebde9` (`cursor/firewall-contract-95d4`, the same commit as `-f5e7`). It merges #1303
at `e6203f121`, which r8 granted, then adds three commits: `451c4d133` and `888c56772` (the rename map) and `78040d4bc`
(one docstring sentence). The comparison script and its output are in the store's `private/red-team-reviews/1323/`
(`r9b-*`).

**Patch against patch.** `git diff 65ab946f0 5f2fb2322` and `git diff e6203f121 888c56772` touch the same 11 files.
1,798 of their lines are equal, `lean-audit.json`'s 282 included. The 13 that differ are 6 old lines against 7 new ones:
- README: `` (`gate.rs`) `` → `` (`firewall.rs`) ``. Rename.
- Assumptions module doc: `` `gate.rs`: `` → `` `firewall.rs`: ``. Rename.
- `FirewallComputes` docstring: the one old line becomes two new ones. That is the same sentence plus "The decisions across
  sessions (whether to go on, whether to release) are outside this assumption, in Lean or in Rust." This is the added
  sentence, not a rename.
- `By.statement` docstring: "the outer gate's skeleton, `gate::skeleton`" → "the outer firewall's skeleton,
  `firewall::skeleton`". Rename.
- `By.recheck` docstring: "the outer gate's" → "the outer firewall's". Rename.
- `By.shadow` docstring: "the outer gate's" → "the outer firewall's". Rename.

All of them are in comments or docstrings. No code, statement or definition changes. Eight of the 11 files are
identical blobs at both heads, among them `lean-audit.json` (`676a1cb55`). The other three are the README,
`Contract.lean` and `Assumptions.lean`, and `git diff 5f2fb2322 888c56772` on them is exactly the lines above.
`firewall.rs` and `firewall::skeleton` exist at the head, and `gate.rs` doesn't. The only
"gateway" left in the patch's added lines is the lane id `review-zk-gateway`, which was already there.

**Audit.** `r20261006-122447-510d` (vy-nebius-1) ran at `888c56772` with `audit.py --build` and no `--update`:
- PASS: 6,164 declarations, the three standard axioms, 14 guarantees;
- its `--update` branch didn't run, and the tree was clean afterwards;
- pytest: 71 passed, 1 deselected.

`r20261006-121243-5173` is the same job at `78040d4bc`, and it also passed. I ran no Lean of my own: the diff gave no
reason to.
