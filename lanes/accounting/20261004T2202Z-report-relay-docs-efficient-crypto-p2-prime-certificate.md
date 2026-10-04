---
id: 20261004T2202Z-report-relay-docs-efficient-crypto-p2-prime-certificate
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/efficient-crypto/p2-prime-certificate.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/efficient-crypto/p2-prime-certificate.md`, sha256 `3a0addc6cf34069e2d615e6e7b30751ff6350b9c1bf7bed720bd1e9cad881409`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# A primality certificate for P2's prime

28 Sep 2026. Workstream 2. This unblocks the "prime certificate" item of the P2 spec freeze
([spec draft](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/efficient-crypto/p2-spec-draft.md)). CPU only.

## Result

- **The current prime is certified.** p = 2^16448 − 21065 is proved prime by an ECPP (elliptic-curve) certificate
  finished on 28 Sep at 22:01Z.
  - **The run.** Enge's CM `ecpp-mpi` on this 4-core VM: 339 steps, 2 h 39 min of wall time, 24,491 CPU-seconds.
  - **Three independent checkers accept it:**
    - PARI's `primecertisvalid`;
    - CM's own `ecpp-check`;
    - this campaign's `ecpp_verify.py`, which shares no code with either.
  - **Where it lives.** `internal/efficient-crypto/p2-prime/cm-cert-p16448-c21065`, in PARI/GP format, SHA-256
    `6a3f6f1170295adcf73a49733da02e42ff6d96e73bacce666855cc9a5ef1d3c5`, and a Primo-format copy.
  - p ± 1 still has too little structure for a cheap N−1 or N+1 proof; that is why ECPP was needed.
- **An alternative prime certifies instantly.** p′ = 2^16448 − 1213·2^8232 − 1 has an N+1 certificate that takes
  seconds to produce and check. Three independent implementations confirm it, and it is **proved prime in Lean** by
  kernel computation in 48 s.
- **Recommendation for Daniel: keep p.** It is now certified, so the prime needs no change. p′ is no longer needed
  unless a Lean-checked primality proof becomes a freeze requirement. The spec is unchanged.

## 1. The current prime, p = 2^16448 − 21065

**N−1 and N+1 are out.** Pocklington-type proofs need a fully factored part of p − 1 or p + 1 of at least about p^(1/3)
(with the Brillhart–Lehmer–Selfridge refinement), i.e. about 5,500 bits. Trial division to 2^20 finds:

| | small factors | factored bits | remaining cofactor |
|---|---|---|---|
| p − 1 | 2 · 5 · 1021 · 314599 | 31 | 16,417 bits |
| p + 1 | 2³ · 3² · 17 · 47 · 21019 · 76403 | 46 | 16,402 bits |

ECM finds factors of at most a few hundred bits, far short of 5,500. The pseudo-Mersenne form 2^w − c gives no
algebraic factorization of p ± 1.

**ECPP is feasible.** PARI/GP 2.15's `primecert` was measured on this VM, sharing it with other jobs:

| bits | 1,024 | 1,536 | 2,048 | 3,072 | 4,096 |
|---|---|---|---|---|---|
| seconds | 1.2 | 3.6 | 9.6 | 49.9 | 151 |

- **Scaling.** Time grows roughly as bits^4 (exponent 3.9–4.1 between the last three points).
- **Estimate for p.** At 16,448 bits that gives about 11 hours, or about 22 hours if the exponent drifts to 4.5
  (*est.*).
- **The faster tool: Enge's CM 0.4.4** (FastECPP; `ecpp` serial, `ecpp-mpi` parallel), built on this VM from
  source.
  - **Calibration.** Serial `ecpp` took 43 s at 1,001 digits, against the paper's 48 s (Enge, "FastECPP over MPI",
    arXiv 2404.05506). The paper's serial 510 min at 5,000 digits therefore transfers: about 8.5 h here.
    `ecpp-mpi` with 4 processes took 8.0 min at 2,001 digits, against about 14 min serial, and its advantage grows
    with size. So p should take about 3–5 h on 4 cores (*est.*).
  - **Certificates.** CM's certificate is in PARI format, and both PARI and `ecpp_verify.py` accept it; tested at
    1,001 digits.
- **The run** (`internal/efficient-crypto/p2-prime/cm_job.sh`, tmux `cm-ecpp`):
  - `ecpp-mpi` with 5 processes on 4 cores, since 28 Sep, 19:19Z;
  - **checkpointed**: CM's `.cert1`/`.cert2` files resume a restarted run, and they are copied to
    `internal/efficient-crypto/p2-prime/cm-checkpoints/` every 10 minutes, with a heartbeat recording date and VM
    uptime;
  - it verifies with PARI's `primecertisvalid`, CM's `ecpp-check` and `ecpp_verify.py`, then copies the certificate
    there;
  - a babysitter agent keeps the VM awake, because it pauses when no agent is active, and restarts the job from its
    checkpoints if it dies;
  - the earlier PARI run (13:40Z) was stopped at 19:17Z: it had had only about 40 minutes of VM time because of the
    pauses, and CM is several times faster.
- **Fallback.** If this VM keeps pausing, the checkpoints move to a CPU pod. At 32 vCPUs, `ecpp-mpi` should take
  about 1–2 h (*est.*); the paper measured 51 min at 5,000 digits on 128 cores.
- **The independent verifier.** `ecpp_verify.py`, standard Python with gmpy2 and no PARI code, checks every
  Goldwasser–Kilian step with affine arithmetic that rejects on any non-invertible element. It accepts PARI's
  256-bit and 1,024-bit certificates (0.4 s for 38 steps), and rejects tampered ones: a moved point, a changed t, a
  broken chain. At full width it should take tens of minutes (*est.*).
- **Verifier cost at full width.** `ecpp_verify.py` took 13 s on CM's 73-step certificate at 3,322 bits.
- **The result (28 Sep–29 Sep).**
  - **CM `ecpp-mpi` finished** at 22:01Z: 339 steps, 9,529 s of wall time (2 h 39 min) and 24,491 CPU-seconds on 5
    processes and 4 cores. CM's built-in `-c` check passed.
  - **Three independent checks**, all passing (`cm-ecpp.log`, `pari-verify-cm.log`, `mine-verify-cm.log`):
    - PARI 2.15.4's `primecertisvalid` returned 1 in 644 s. It also confirmed that the certificate's first N is
      exactly 2^16448 − 21065.
    - CM's `ecpp-check` reported a valid ECPP certificate.
    - `ecpp_verify.py` accepted all 339 steps against the target 2^16448 − 21065, in 7,799 s including VM pauses.
  - **The files** are in `internal/efficient-crypto/p2-prime/`:
    - `cm-cert-p16448-c21065`, the PARI/GP format, SHA-256
      `6a3f6f1170295adcf73a49733da02e42ff6d96e73bacce666855cc9a5ef1d3c5`;
    - `cm-cert-p16448-c21065.primo`, SHA-256 `a759215b2ecb294b8516b4069c72bc1f031cd8409c1ceed4833b6dcd9c762244`;
    - the run's checkpoints and heartbeat, in `cm-checkpoints/`.
  - **Two first-pass failures, both in my own setup.** PARI's first check hit its 8 MB default thread stack, and
    `ecpp_verify.py` hit Python's 4,300-digit limit on integer conversion. Both were rerun with the limits raised
    (`verify_cm.sh`).
  - **Keeping the VM awake.** The heartbeat shows the VM paused once, between 19:29Z and 20:12Z, before the keep-awake
    agent was running. From 20:12Z it stayed awake until the run ended.

**Lean check: not practical for ECPP.** It needs elliptic-curve arithmetic modulo a possibly composite N and the
Goldwasser–Kilian theorem, which Mathlib doesn't provide. An ECPP certificate would therefore be checked by two
independent programs, not by Lean.

## 2. A proposed alternative, p′ = 2^16448 − 1213·2^8232 − 1

**Why this form.** Take p′ = 2^w − k·2^v − 1 with k odd and v ≥ w/2. Then:
- p′ + 1 = 2^v · (2^(w−v) − k). The power of two alone exceeds √p′, so an N+1 proof needs no factoring at all.
- p′ ≡ 7 mod 8, so p′ ≡ 3 mod 4 as P2 requires.
- Reduction stays shift-and-add, because 2^w ≡ k·2^v + 1.

**The search.** Over k odd ≤ 1,999 and v = 8,224–8,255 (`search.py`, `search-log.jsonl`):
- each candidate was sieved by primes below 2·10^5, then given a Fermat test to base 3, then BPSW;
- three primes were found, at (k, v) = (1213, 8232), (1379, 8250) and (1579, 8233);
- the first, with the smallest k, is proposed.

The hit rate matched the standard density model: the same code finds primes at the predicted rate at 1,024 and 2,048
bits.

**The certificate** (`cert-p16448-k1213-v8232.json`):

```text
N = 2^16448 − 1213·2^8232 − 1       16,448 bits, N ≡ 7 mod 8
N + 1 = 2^8232 · (2^8216 − 1213)     v = 8232
Lucas parameters P = 3, Q = 1, D = P² − 4 = 5,  gcd(5, N) = 1
ω = (3 + √5)/2 in Z_N[√5] has norm 1 and ω^((N+1)/2) = −1
2^8232 − 1 > isqrt(N)
SHA-256 of N (2,056 big-endian bytes): cae8f6f1d954c4a09a55c52cda10ddac8837aa5767ded768f0f26d2d677e10d6
```

**Why it proves N prime.** This is the N+1 test of Brillhart–Lehmer–Selfridge (1975) and Morrison (1975), in the
Lucas–Lehmer–Riesel form.
- Let q be any prime divisor of N.
- In F_q[√5], the map y ↦ y^q sends √5 to ±√5 (Euler's criterion). So ω^q is ω or its conjugate, which is ω⁻¹ since
  ω has norm 1. Hence ω^(q−1) = 1 or ω^(q+1) = 1.
- Since ω^((N+1)/2) = −1 while ω^(N+1) = 1, the order of ω is divisible by 2^8232.
- So 2^8232 divides q − 1 or q + 1, and q ≥ 2^8232 − 1 > √N.
- A composite N would have a prime divisor at most √N, so N is prime.

**Independent checks.** Each implementation recomputes N from (w, k, v):

| implementation | what it computes | time |
|---|---|---|
| `gen_cert.py` (gmpy2) | the Lucas V-sequence: V_A by a ladder, then 8,230 doublings, reaching V_((N+1)/4) = 0 | 10 s |
| `verify_cert.py` (standard library only) | every hypothesis, and ω^((N+1)/2) by square-and-multiply on pairs in Z_N[√5] | 23 s |
| `pari_check.gp` (PARI/GP) | ω^((N+1)/2) in PARI's `Mod(·, x² − 5)` arithmetic, plus a BPSW test | 4 s |

All three agree. The generator and verifier were also tested on 18 primes of the same form at 64–1,024 bits, all
certified, and on 18 composites, all rejected.

**Lean: proved.** `P2Prime.p2_prime' : Nat.Prime (2 ^ 16448 - 1213 * 2 ^ 8232 - 1)`, by the A2 prover, is in
`lean/submissions/efficient-crypto/p2-prime/P2Prime.lean`.
- **The criterion.** It rests on a general N+1 theorem, `prime_of_nplus1`. Its hypotheses are all decidable facts
  about naturals:
  - N is odd and 2^v divides N + 1;
  - D is coprime to N;
  - x = a + b√D has norm 1 mod N;
  - a square-and-multiply on pairs mod N gives x^((N+1)/2) = −1;
  - N < (2^v − 1)².
  The proof uses Mathlib's `QuadraticAlgebra (ZMod q) D 0`, Frobenius and Euler's criterion.
- **The kernel check.** The 16,448-step power is checked by `decide +kernel`, which is kernel evaluation with no
  `native_decide`.
- **Axioms.** `propext`, `Classical.choice` and `Quot.sound` only.
- **Timing.** The kernel check takes 48 s. An independent kernel replay of all 71 constants takes 52 s. My own rebuild
  in a separate build tree took 59 s, with the same axioms.
- **Non-vacuity.** Sanity primes of the same form at 64 and 128 bits are proved. A 64-bit composite of the form is
  rejected by exactly the power check, and all the criterion's hypotheses are shown satisfiable.
- **Not pinned.** If it were, the statement is self-contained and needs no new trusted definition.

**Bound to the modulus.** `verify_cert.py CERT.json 16448,1213,8232` also checks that the certificate is for the
expected (w, k, v), as the crypto review asked. Against any other tuple it fails.

### What switching to p′ would change

- **Spec.** The prime id, the test vectors and the challenge ladder's rule.
- **Root cost for the adversary.** Unchanged. (p′ + 1)/4 = 2^8230·(2^8216 − 1213) still needs about 16,446 sequential
  squarings: no addition chain for an exponent of that size is shorter.
- **Decode kernels.** Reduction becomes about three shift-and-scalar folds instead of two, *est.* under 2% of a
  squaring on CPU. The GPU kernels' reduction step would need rework (the MVP owner).
- **Domain tail.** The fraction of 16,448-bit strings ≥ p′ rises from 2^-16433 to about 2^-8205. That is still
  negligible for tweak rejection and σ's exceptional branch.
- **Lean rows.** The exact-domain `m1p` rows would need new pins at p′. The same proof applies: its hypothesis
  2·B·(2^w − p′) ≤ 2^w holds with a wide margin at B = 2^23.
- **Discrete-log shortcuts.** p′ = X^8 − 310528·X^4 − 1 with X = 2^2056 is as special (SNFS-friendly) as the current
  form, which the crypto review already priced as far outside budget.
- **Crypto review: acceptable with conditions** (`crypto-review-p2-instantiation`; section "Proposed prime p′" in
  `internal/efficient-crypto/attacks/p2-instantiation-review.md`).
  - **What it confirmed.** The certificate argument is correct. Neither the large 2-power in p′ + 1 nor the sparse
    form gives a root or discrete-log shortcut; discrete logs use p′ − 1, whose 2-adic valuation is 1 as before.
  - **One new structure.** Modular negation is an exact bitwise complement on the low 8,232 bits. This weakens the
    heuristic behind the same-mask negation study.
  - **Conditions before freezing p′:**
    - rerun the character, negation, differential and split-lattice controls on this modulus family;
    - record an exact SNFS estimate and a smoothness screen of p′ − 1;
    - benchmark the three-term reduction, and recalibrate SeqRoot and Q;
    - regenerate the `m1p` pins;
    - archive the certificate, with the verifier bound to (w, k, v).
  - **Its conclusion.** Waiting for the current prime's ECPP is the lower-risk freeze path.

## 3. What Daniel decides

| Option | Certificate | Lean-checked | Cost |
|---|---|---|---|
| A. Keep p = 2^16448 − 21065 | **Done:** ECPP, 339 steps, accepted by PARI, CM's checker and an independent verifier | No | None |
| B. Switch to p′ = 2^16448 − 1213·2^8232 − 1 | N+1: done, three independent checks, **and proved in Lean** | Yes | The crypto review's conditions above, plus spec, vector and kernel-reduction changes |

**Recommended default: A.** The ECPP certificate is done and all three checkers accept it. It changes nothing else,
and the crypto review calls it the lower-risk path. **B** is needed only if a Lean-checked primality proof becomes a
freeze requirement, and it comes with the review's conditions.

**The ECPP run's history.**
- The first launch, at 13:08Z, overflowed PARI's 3 GB stack at 16,448 bits; at 4,096 bits the stack never exceeded
  128 MB.
- It was relaunched at 13:40Z with a 7 GB limit and 2 threads, and with PARI's break loop off, so a failure exits
  and is logged instead of hanging.
- At 5 minutes it had passed the earlier failure point, at 2.9 GB resident.
- If it needs more memory than this VM has, the log in `internal/efficient-crypto/p2-prime/ecpp-current.log` will say
  so. Option A would then need a larger CPU machine.
- **Stopped at 19:17Z.** Between 13:45Z and 18:47Z the VM's uptime advanced only about 30 minutes, because it pauses
  when no agent is active. The run had therefore had only about 40 minutes of VM time.
- **Replaced** by CM `ecpp-mpi` at 19:19Z (`cm_job.sh`), which is checkpointed and several times faster.
  - A first CM launch at 19:18Z exited at once: the number was passed as a decimal string, and Python 3.12 won't
    print an integer that long. The fix passes the expression `2^16448-21065`.

Files: `internal/efficient-crypto/p2-prime/`. The scripts: `search.py`, `gen_cert.py`, `verify_cert.py`,
`pari_check.gp`, `ecpp_verify.py`, `ecpp_job.sh` and the ECPP timing scripts. The outputs: the certificate JSON, the
logs, and the test ECPP certificates at 256 and 1,024 bits.
