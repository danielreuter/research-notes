---
id: proofs/20261006T0101Z-finding-rec-thm
campaign: proofs
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: bc-0e16e57e-9802-53aa-81a3-ac82cc7f2261 (rec-thm, for the proofs coordinator bc-8416bc72)
---

# The recursive audit's soundness and zero knowledge are proved in Lean, over one new assumption, VBridge

The recursive ZK system has two end-to-end guarantees. Both are now stated (`def G : Prop`) and proved
(`Flock.SecurityProofs.G : Flock.Guarantees.G`) on branch `cursor/rec-thm-95d4` at `e7bf84caf` (off `b87eeef64`):

- **`Flock.Guarantees.RecursiveSound`**, for the auditor.
- **`Flock.Guarantees.RecursiveZK`**, for the developer.

Both use only `propext`, `Classical.choice` and `Quot.sound`. Their one new named assumption is
`Flock.Assumptions.VBridge`. They are pinned in `verity/Security/lean-audit.json` (owner `@proofs`). The audit is `r20261006-001503-1357` on
vy-nebius-1, run with `--no-replay` and recorded in `art:007c4387e54fb9c0c70f43dbd2d3d1355b246515e44e6483beffa04cc1b870cd`:
- `verity/Security`: **PASS**, 0 failures. The two records are new and need a named statement reviewer.
- `verity/Security/Proofs`: **FAIL**, on `DifftestMain`'s `generate` alone, a failure flock-gk-game's audit also has.

The PR body is the coordinator's `internal/proofs/rec-thm-pr.md`.

## What each says

- **`RecursiveSound`.** For every prover of the recursive audit (`recGame`), consider the probability that V*'s outer
  `--zk --registered` session accepts and yet the hidden circuit's statement fails. It is at most the sum of:
  - the outer session's bound (`ZkOuter.bound`: `zk_session_soundR` at one wrong unit plus `zk_session_regValsR`);
  - for each inner round, a stage slack plus `(Σ κ)·√(q²/2^513)` (the binding of the gateway's commitments, `stage_bind`);
  - `εin`, the inner protocol's error.

  Its premises are `VBridge`, `cr/sha-512` (`hCRo`, `hCR`), A3 (`uniform/os-random`) and `InnerSound I εin`. For C-Flock's
  interactive table, `flock_inner_sound_fast100` proves `InnerSound` at `2^-205` for `22 ≤ m ≤ 33`.
- **`RecursiveZK`.** The auditor's whole view consists of its tape, the gateway's `nh` commitments `gatewayLeaf msg y`
  (hm96-sha512 leaves of `SHA-512(msg)` under fresh salts) and its view of the outer session. That view is within
  `εo + nh · 2^-193` of a simulator that reads the auditor and public inputs only: it draws `nh` ideal leaves and runs the
  outer simulator on them. Its premises are the outer session's simulator at `εo` (`hOuter`) and `hash-derived-key`.
  Every event is bounded one way, so the bound holds both ways by taking the complement.

## Proved, and premise

- **Proved:** both guarantees, and everything under them. `RecursiveSound` is `zk_session_recursive_full`, ported from
  `cursor/rec-sound-95d4` to `Proofs/Flock/Recursive/` with its whole model. `RecursiveZK` is two hybrids: the outer
  simulator, then `ZK.ideal_leaves_swap` once per commitment.
- **Premise, beyond `VBridge`:**
  - `cr/sha-512`, A3 and `hash-derived-key`, which are named assumptions already;
  - `live-verifier` (`ZkOuter.hRec`);
  - the outer session's malicious-auditor zero knowledge (`hOuter`);
  - the coin model: the inner coins are fixed by the auditor's tape before the first commitment (Goldreich–Kahan's
    committed coins or a beacon), and the binding of that coin commitment is outside the statement;
  - the gateway's program is `gatewayLeaf`, and it sends nothing else of the messages.

  Timing and aborts belong to the network warden, and egress is a deployment premise.

## Limits

- It covers one outer session, not the list of five sessions run today.
- `VBridge` is the soundness direction only.
- The soundness model's commitments (`cmt`, `obK`: plain SHA-512 at single gates, which isn't hiding) are not formally
  the ZK side's `gatewayLeaf`.
- There is no HVZK or beacon corollary.

## For the vbridge lane

`Flock.Assumptions.VBridge` is four facts, and its piece G now has a target. The facts:

1. `Recursion.VBridge` (#1090's): V* accepts only an accepted inner transcript.
2. `VCommits`: V*'s public file registers the gateway's commitments.
3. `VDecodes` at equality: V* decodes each round's message.
4. V*'s law draws every commitment wire's stratum in full.

The fourth is about V*'s law, not its circuit, and is decidable at a concrete V*.

## Recommendation

The largest remaining piece is `VBridge` itself, the vbridge lane's plan (`note:proofs/20261005T2345Z-draft-vbridge-plan`,
3,450 to 6,080 lines, waiting on rec-step2's V* circuits).

On the ZK side, the largest is `hOuter` against a malicious auditor: instantiate `gk_simulate_hm96` at C-Flock's `--zk`
session. Until then, `RecursiveZK` holds against a malicious auditor only given that premise. An honest-coins (HVZK)
corollary would discharge `hOuter` at uniform coins with `zk_session_view_all`. It isn't done, because that theorem's
coin types are dependent.

## Other things the coordinator should know

- **The shared `/workspace` checkout.** It has a foreign commit, `d3fdebd3f` (one-stage-layout's `pod.sh` fix), on the
  local branch `cursor/rec-thm-95d4`. I worked in a separate worktree, `/home/ubuntu/wt/rec-thm`, from `b87eeef64`, and
  pushed from there. Origin's `cursor/rec-thm-95d4` doesn't contain `d3fdebd3f`.
- **flock-gk-game's trusted-text test.** When `test_trusted_text_builds_on_mathlib` lands, `Specs.Flock.Assumptions.Recursive`
  and `Specs.Flock.Guarantees.Recursive` join its `ARKLIB_PENDING`. They read C-Flock's proof-side model, as the 190
  modules already listed there do.
