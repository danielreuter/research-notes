---
id: review-zk-gateway/20261006T1506Z-finding-review-zk-gateway-r10
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1339@0018a8ddc09d19ead8fb2acbf58bc41428275c6e]
---

# Red-team round 10: #1339 at `0018a8ddc` GRANT (B1′)

Round 9 withheld the grant at `d5aa5ffd2` on B1′: the outer order and count weren't held
(`note:review-zk-gateway/20261006T1227Z-finding-review-zk-gateway-r9`). This round reviews
`0018a8ddc09d19ead8fb2acbf58bc41428275c6e` (`cursor/firewall-outer-95d4`, base #1323 at `888c56772`). The delta is
`3d6bd451d..0018a8ddc`: `22fb59817` (the harness's sequence check and `firewall.gate.from`) and `0018a8ddc` (the README's
run id). Detail and scripts are in the store's `private/red-team-reviews/1339/` (`review-r10.md`, `r10-*`).

**Verdict: GRANT at `0018a8ddc`.** No blocking items.

- **Rename merge.** #1339's own patch before and after `e7f327855` (with its merges `cfaffcdb8` and `3d6bd451d`) differs
  in 74 paired lines, every one a rename-map substitution.
- **B1′, answered for what the PR claims.** The body, PROTOCOL §10.4 and the README say that the harness holds the
  recorded sessions' order and count against the honest sessions, and that the contract holds no outer order yet. The
  code does that:
  - every honest session must equal one honest sequence (1,454 items);
  - a stopped control must be a prefix of it;
  - a refused control's let-out items must be the prefix up to `firewall.gate.from`, and its candidate must be the
    contiguous honest run where it leaves.
- **Probes and tests.** In evidence run `r20261006-134729-fddc`, 60/60 sessions agree. Its 21 order probes cover
  reordered, dropped, duplicated and moved items and an early `finish`, on honest sessions (prefix and whole), opening and
  algebra. Each misses at its intended item, and the contract alone accepts 12 of the 21. The two new tests cover the same
  cases, plus the control's own: dropped, twice, more pads, nowhere, swapped, and no `from`.
- **`from` can't move a candidate to another place.** Places are unique in the honest sequence, so a candidate's run is
  exactly where its items leave in an honest session, at or after `from`.
- **Non-blocking: an understated `from` hides a dropped block.** The prefix is checked only up to `from`, the
  transcript's own word. A transcript that drops let-out items and puts `from` before the gap passes the harness: the
  items after the gap count as the candidate.
  - Replayed with the compiled contract at the head (`r20261006-145435-7f04`, vy-nebius-1): forged opening, label and
    root controls pass with no miss, and the same drop with the truthful `from` misses at the dropped item.
  - It doesn't touch the claim. The recorder sets `from` from the same place as the items, before it pushes the
    candidate, and on every sampled refused control `q − from` is its kind's honest displacement (0, 1 for the roots, 740
    for the proof shape), with `at` the last item.
  - Suggested tightening: require that displacement for the candidate's kind and `at == len(items) − 1`, and add negative
    tests with an understated `from`.
- **Non-blocking, for the rename check.** The prose "gated session(s)" (7 places) and the format key
  `firewall.gate.{refused,at,from}` remain.
