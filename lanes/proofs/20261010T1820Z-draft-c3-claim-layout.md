---
id: proofs/20261010T1820Z-draft-c3-claim-layout
campaign: flock
lane: proofs
kind: draft
status: open
repo: danielreuter/verity
origin: F4 design agent (bc-74de88e1), the registered opening's `claim` witness layout for candidate 3 (top's step (b), Slack 1791655759), for the proofs coordinator bc-8416bc72
---

# Candidate 3: where the registered opening reads `claim` (11:20 PDT, 10 Oct)

Answers top's step (b) (Slack 1791655759). Read: #1710 at d4ce10b6e (`rec_sparse.py`, `rec_algebra.py`, `tests/test_rec_sparse.py`)
and main at 0ad041ef3 (`rec_outer.py`, `rec_residuals.py`, `Security/Proofs/Flock/Soundness/Assumptions/Recursive.lean`).

## Layout
- `claim` is a value the prover registers, `rec-claim`, next to `rec-acc` (`rec_outer.py:29,69`). It uses the V* session's
  program string, which every statement that reads it shares (`rec_outer.py:29`), and the prover's own salts (`Chain.build`, `rec_outer.py:181`).
- It has two rows, and row r belongs to rep r. It is per rep, not shared: τ and h are the shared ones (`reads`, `rec_sparse.py:244-251`).
- Each row is one M0 row of `P(1) = 64` u16 words. The element is in words 0-7, where word j holds bits 16j..16j+15, so bit k is
  bit k%16 of word k//16 (`words`, `rec_sparse.py:211-213`). Words 8-63 are zero and unread, like `v`'s tail (`rec_residuals.py:25`).
- RecSparse's port already has this layout: `claim` is the last port and holds 1 element (`rec_sparse.py:149-155`), and
  instance r reads row r (`rec_sparse.py:250`).
- The registered opening has one instance per session. It reads the value through two ports, `claim0` at row 0 and `claim1`
  at row 1, the way `InnerRepCheck` reads `acc0` and `acc1` at two rows of `rec-acc` (`rec_residuals.py:19,101`).

## The tie
- RecSparse instance r checks `claim + Σ_t eq(ρ_t,t)·vt_t` when T > 1 (`rec_sparse.py:464`) and `claim + Σ_p eq(ζ_p,p)·u_p`
  when T = 1 (`rec_sparse.py:462`). In both, the claim is an add term.
- In the opening, claim k's ring-switch residual becomes `dot(wv_k, rs[k]) + claim_k`. Today that slot holds
  `^ cl.value` (`rec_algebra.py:643-644`). wv_k is built from `registered_claim(sh, coins, k)`'s skip and x[0]
  (`rec_sparse.py:332-336`), and x[1:] goes to the rpp sumcheck and Ligerito as it does now. The point comes from the coins,
  so it sits in the opening's `v`.
- Both readers open the same cells of one registration with one root. If both residuals pass, then vt(ρ_t) (or u(ζ_p)) equals
  `dot(wv_k, rs[k])`, and ring switching plus Ligerito make that equal R̂(point). This is the same check the public extra claim
  made, with the claim eliminated. A claim ≠ vt(ρ_t) fails RecSparse. A claim = vt(ρ_t) ≠ R̂(point) fails the opening.
- Registering the claim late (after the last inner coin, as R₂) gains the prover nothing. Each residual makes the claim a
  function of committed inner messages (vt or u, and rs[k]) and the inner coins. VBridge is generic in R₂
  (`Recursive.lean:60`), so R₂ only gains `rec-claim`.

## What the session builder writes
- The value is M1's `sparsePhase` output claim for each rep: vt evaluated at ρ_t when T > 1, or u at ζ_p when T = 1, as the test
  builds it (`tests/test_rec_sparse.py:150-153`). The inner coins fix only the point; they don't determine the value.
- Before registering, the builder checks that the value equals R̂ at `registered_claim`'s point (as
  `tests/test_rec_sparse.py:318` does) and equals `dot(wv_r, rs[r])`. If either check fails, it refuses.
- It commits `[words([claim_0], 64), words([claim_1], 64)]` as `rec-claim` under `session_program`, with fresh prover salts
  (`G.Registered.commit`, as at `rec_outer.py:181`). This happens after the last inner coin and before any outer coin.
  The root goes in the session record next to `rec-acc`'s.
- The reads it wires: RecSparse's `claim` reads row r in instance r; the opening's `claim0` reads row 0 and `claim1` reads row 1.

## Hiding
- Hiding holds. The value never enters `v`, which the verifier registers under public salts (`rec_outer.py:13-16`). It is never
  a public input, never an extra claim (`rec_algebra.py:596-598` refuses that), and never an output. Like `rec-acc`, it sits
  behind the prover's salts.
- The point has NU + P_LOG + T_LOG coordinates, which the menu's shape fixes; it doesn't depend on the session's draws.
- RecSparse gets no extra products, since the claim is an add term (`rec_sparse.py:462,464`). The opening also gets none,
  provided `_build` adds `claim_k` as an add term, as it does `acc0` and `acc1` (`rec_algebra.py:889`). If it were treated as an
  ordinary linear atom, it would get a coefficient slot and a product (`rec_algebra.py:893-895`): 2 × 3^7 = 4,374 ANDs per
  session. That is cost, not leakage, because it depends only on the shape.

## Questions for circuits
1. `run` has `fold_only` but no opening-only mode (two registered claims, no zerocheck or lincheck); `sh.claims` counts
   w and pc (`rec_algebra.py:594-595`). K2 priced that mode as `structure(Shape(m, 6, 2))`. Its claims need a witness atom
   kind that `_build` adds the way it adds acc. Which construction carries this mode?
2. Two ports on the opening's one instance (my proposal, following acc), or two one-claim instances? The second loses the
   γ batch and runs two Ligerito openings.
3. `registered_claim` refuses a point with fewer than 6 coordinates (`rec_sparse.py:334-335`), so step (c)'s small shape needs
   NU + P_LOG + T_LOG ≥ 6.
4. In Lean, the outer statement's list of R₂ values has to name `rec-claim`. VBridge itself is unchanged.
