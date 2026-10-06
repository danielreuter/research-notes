---
id: vbridge/20261006T1100Z-finding-vstar-register-coef
campaign: proof-service
lane: vbridge
kind: finding
status: active
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
cursor:
  subagentId: "bc-5d1693f8-59d6-5a38-89a1-48bfd0365a30"
---

# V*'s coef, dirs and v as values the verifier registers itself: no V* statement has a public input, and what it costs

Question (task 1 of @proofs's 08:34Z message, B2's ruling, #1261's gap 3): can V*'s staging register `coef` and `dirs`
(and the algebra's `v`) as values the verifier registers, so that no V* statement has a public input, with the honest
K = 4096 session still accepted and a wrong `coef` or `dirs` refused? And what does it cost?

## Answer

Yes. The branch is `cursor/vstar-register-coef-95d4`, on #1284's `cursor/rec-step3-95d4` (`273017068`). The commits are
`96142e0b4` (the registrations), `f011d6057` (the slot bound) and `a9b50258c` (a comment). The PR body is
`/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/internal/proofs/vstar-register-coef-pr.md`.

- **The design.** The verifier computes each row as before and registers it with `Registered.commit` under public salts:
  `rec_residuals.verifier_salts`, SHAKE-256 of the program, the value's name and the row's index, as `zero_salts` does.
  The values are `rec-coef` and `rec-dirs` for each level and `rec-v` for each algebra part. The rows are public, so the
  salts hide nothing; the reads need only the binding. The prover's rows and salts are the same registration's, and the
  verifier's `pub.bin` holds every row's `b || c`.
- **Definitions.** `RecOpen_v4` has a `dirs` of 64 words (one M0 row; the unit reads word 0's low H bits), and
  `InnerRepCheck_v2` has a `v` of P(nv) words (the unit reads its first 128·nv bits). circuit-check passes both, with 0
  failures.
- **Negative controls.** The forged-`coef` and forged-`dirs` sessions are refused at L0 by the server and by upstream's
  replay, both with `opening: RingSwitch(ClaimMismatch)`. Each is the prover's row one bit off, under the verifier's salt.
  The other forgeries are refused where they were on rec-step3.

## What it costs

- **Per opening.** `coef` costs LANES/4 SHA-512 compressions (16 at L0, 4 at L1–L6) and `dirs` costs 1. That is 10,822
  in a session (436 × 17 + 682 × 5). The plan's estimate, about LANES hm96 compressions per opening, was high.
- **L0.** It doubles its block (k_log 23 to 24), because it already filled 7.75/8 of 2^23. Its proof grows from
  1,070,554 to 1,088,410 bytes, its prove time from 1.17 to 1.82 s, its serve verify from 1.5 to 4.7 s, and its GPU peak
  from 11.1 to 21.1 GiB. L1–L6 keep k_log 23 and their proof sizes.
- **`v`.** As a row port it costs about nv/8 compressions per rep. Unbounded, K = 4096's first algebra part reaches 171
  slots and k_log 27 = `K_MAX`, and its serve verify takes 43–64 s (run `r20261006-100522-5713`). `MAX_SLOTS = 128`
  splits the algebra into two parts at k_log 26 (128 and 125 slots, run `r20261006-101921-b847`): 2^27 bits in all, as
  on rec-step3.
- **A cheaper `coef`, not done.** `coef` is κ[level][r][l] · eq(α)[j]. With κ as a constant of the level's template, the
  products by κ are free in ANDs, and an opening registers one F element. That would take back most of L0's cost.

## Runs (node 1)

| Step | Runs |
|---|---|
| vstage | `r20261006-093343-89f7`; bounded algebra `r20261006-101921-b847` |
| oprove | `r20261006-100522-5713` |
| Lean | see the PR body |
| Baseline (rec-step3) | vstage `r20261006-022005-409a`, oprove `r20261006-024439-6203`, Lean `r20261006-040407-0310` |

## Hazards met

- `test_rec_algebra.py`'s Lean mutation test runs `lake build` in the tree whenever `lake` is on PATH. It made a 327 MB
  `.lake` in `/tmp/vb-coef` twice; I deleted both. `--deselect backends/flock/tests/...` doesn't match, because the suite's
  rootdir is `backends/flock`; use `-k 'not rejects_exactly_the_mutations'`.
- The VM's disk was full (254 GB, mostly other lanes' worktrees and pytest dirs). Freeing space, I deleted
  `/tmp/pytest-of-ubuntu/pytest-655` (64 KB), which was another agent's, by mistake.
