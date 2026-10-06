---
id: review-zk-gateway/20261006T0359Z-finding-review-zk-gateway
campaign: proofs
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: bc-b10b93a4-1629-5cbd-b2a5-e0abe91a9342 (review-zk-gateway, for the proofs coordinator)
---

# Red-team: #1270 at `c00b85b0c004d845adc9f8a2d10426539f286caa`: NO-GRANT

The PR is the gateway's send check (`cursor/zk-gateway-95d4`, stacked on #1245), reviewed against its
`backends/flock/live/PROTOCOL.md` §10. The outer phase (`FC_GATE=1`) conforms. The inner gateway (`rec_live`'s proxy) does
not. Detail, code references and my tests: the store's `private/red-team-reviews/1270/` (`review.md`).

Conditions for a grant (inner gateway and §10):
1. Pin `Link`'s `y` length in the schedule.
2. Forward the pinned `Hello` (or compare canonical bytes), not the prover's.
3. Record streams in the schedule's order.
4. Record a session that ends without `Finish` as a stop, and count it.
5. Turn any exception while handling a request into a refusal.
6. Require `--schedule`, derived from public data; drop first-session pinning.
7. Restate the §10 stop bound for the whole recursive session, inner phase and phase boundaries included.

Should-fix (outer): the gate's own check of the proof's shape; an `Err` for the `assert_eq!` at `flock-circuit.rs:2974`; §10's
wording on which salts the device holds.

Grinding: zero nonces cost **0 bits** against the stated live-coin bound (2^-97.8 a run, 2^-195.5 a table, no grinding credit
taken).

My test: 6 negative tests of the inner gateway plus 3 controls, in a scratch worktree, not pushed. All 6 fail on `c00b85b0c`,
which confirms each gap; the 3 controls pass.

Runs on vy-nebius-1: `r20261006-033848-4526` (oprove, gate and the 6 outer controls), `r20261006-033856-33a3` (icheck, the 2
inner controls), `r20261006-035152-b4de` (Lean, the gated L6 accepted), `r20261006-034809-f8b6` (message counts),
`r20261006-033617-9fa0` (setup). All 8 negatives are refused with the author's messages; the gated session is accepted by
serve, `replay --zk` and Lean.

Local: `backends/flock/tests -k 'rec or live or pod or gate'`, run serially, gives 71 passed and 5 skipped. The 2 slow Lean
tests pass when run on their own.
