---
cursor:
  subagentId: "bc-be25385c-8dda-5970-9cf6-7c0ce338bad3"
---

# Private-circuit prototype: first milestone (an inner session verified inside V[B])

**Lane** `private-recursion`. **PR** [#97](https://github.com/danielreuter/verity/pull/97) (draft). **Branch** `cursor/private-recursion-bad3` @ `85c94e5c`. **Spec** [circuit-privacy](../docs/circuit-privacy.md), I.3 and I.9. **Full lane report** `lanes/private-recursion/20260926T2300Z-report-private-recursion.md` in the notes (mirrored under `internal/lanes/`). **Evidence** `art:da941437`. **Spend** $0: no pod, no GPU.

## Result

**Inputs.**
- The session: PR #83's RoPE session at `fd02e847` (8 instances, m = 23, two reps; `art:bd9f7efb`).
- V[B]: a hand-built verifier circuit built from the public bounds B alone. It is 4.52 G ANDs in 1,963 batched gadget operations.

**What V[B] checks.**
- C opens c (`hm96-sha512/v1`, byte-identical to PR #93's vectors).
- A toy Φ holds.
- All 175 inner messages open their commitments.
- The inner verifier accepts. It covers zerocheck, lincheck with the matrix fold computed from the private C, ring switching, Ligerito with its Merkle openings, and R1.
- The data binds to the frame-v3 roots.

**Checks run.**

| check | result |
|---|---|
| honest session | accepted |
| differential vs the recorded Lean and upstream verdicts (honest, R-BREAK, 23 re-digested mutants, the retained-bytes trio) | 28 of 28 agree with Lean. Two proof fields that V[B] has no input for (D-fc `final_c_eval`, D-rs the grinding nonce) are refused at witness decoding |
| own negatives (wrong C ×3, Φ ×4, broken or mismatched commitments ×5, flipped output ×2) | 14 of 14 rejected, each at the intended check |
| gate level | sampled instances of every SHA-256, SHA-512 and GF(2^128) op agree with their Boolean circuits |
| swap (structural) | a different unit with other leaf maps, same B: byte-identical V[B], and the same 175 × 64-byte commitments and outer input sizes |

## Costs against spec I.7 (both reps)

| component | spec | measured |
|---|---|---|
| matrix fold | ~5,000 ANDs per nonzero; RoPE ~0.1 G | **3.59 G**: 157,841 nonzeros at 22.7k ANDs each (11.4k per rep) |
| Ligerito openings (SHA-256 trees, m = 23) | 0.5–1.7 G per rep (SHA-512) | 0.34 G |
| field arithmetic | 0.1–0.5 G | 0.10 G |
| round commitments | 1–10 M | **100 M** (56.7 KB of framed bytes per rep) |
| binding C (664 KB Enc(C)) | 453 ANDs per byte | 0.30 G |
| IO binding, regions, Φ | ~2.3 M per range | 0.10 G (whole trees rehashed) |
| **total outer** | **1–2.5 G** | **4.52 G** |

Not measured yet: outer proving time and Lean verification time, since no outer proof exists yet.

## What changes the spec

1. **B's nonzero bound is too small for RoPE.** The RoPE pair unit has 157,841 private nonzeros (about 25 per row), against B's ≤ 2^16.
2. **The fold dominates the outer proof, already for RoPE.** It costs 3.6 G, not 0.1 G, so holography, public slot types or sparser lowerings matter now, not only for templates with millions of nonzeros.
   - Cheaper exact variants are known: a merge network for the row side (about −0.65 G), and per-row sums instead of per-entry products (about −0.7 G).
3. **Round commitments cost about 10× the estimate.** The ring switch alone sends 32 KB per rep.
4. **Almost every inner check is linear in the messages, with coefficients that depend only on the coins.** So V[B]'s public inputs are best taken as whole coefficient vectors.
5. **The outer proof needs cross-table private glue in the prover.** V[B] is a session of gadget tables joined by private ports. PR #83 keeps all glue inside one block, and 4.5 G ANDs cannot fit in one block. Flock's region-equality and shift glue, planned in the M0 scoping but not built, is the dependency. It blocks the next milestone.

## Scope

Daniel ruled on 2026-09-27 that serving-time side channels are out of scope. The round schedule fixed by B, which V[B] has, is the only timing padding.

## Next, if resumed

- the glued multi-table outer proof, then M1/M2;
- the live hidden-message mode and a SHA-512 session. A handoff went to the PR #83 lane; none of their code was touched;
- a second template's real inner session, for the full swap test;
- V[B] generated from Lean (R2).
