---
id: r20-proof/c-vole/20260922T0620Z-report-antman
campaign: r20-proof
lane: c-vole
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/vole/ANTMAN.md
---

# AntMan-style SIMD for the communication bottleneck: inventory and what it buys

Written after the direct QuickSilver profile (`note:r20-proof/c-vole/20260922T0646Z-report-gpu`), as the brief requires. Source: Weng, Yang, Yang, Xie,
Wang, *AntMan: Interactive Zero-Knowledge Proofs with Sublinear Communication*, CCS 2022, ePrint 2022/566
(read for this note; section/figure references are to the ePrint version), plus the AntMan++ compiler
(Journal of Cryptology 2024) for the non-SIMD case. Nothing here was run: swanky has no AntMan
implementation (`grep -ri antman` is empty), and the authors' implementation was not evaluated in this lane.

## 1. The measured problem it would address

Direct QuickSilver in Diet Mac'n'Cheese, our compiled relation, F_{2^61-1}, B = 4096 VUs
(run `r20260922-053613-d110`): **8.50 MB per VU prover -> verifier** (34.80 GB per batch) and 1.06 MB/VU back,
at 8 B per committed element x 993,095 committed elements per VU. Communication grows linearly in
B x |C|; the prover's arithmetic is ~17 M F_p multiply-adds per VU, which a GPU could do in ~50 us
(`note:r20-proof/c-vole/20260922T0646Z-report-gpu` 2.2). On a 25 Gb/s link the 34.8 GB takes 11 s per batch; a GPU prover would therefore be
communication-bound by ~200x before any other consideration. That is the case for SIMD.

Our shape is the SIMD shape: the 4096 VUs of one step are 4096 executions of the *same* circuit (96 chained
units + epilogue, ~1.0 M committed wires, 501,393 multiplications), with different witnesses. AntMan's
(B, |C|)-SIMD setting is exactly this with B = 4096 and |C| ~ 1.0 M.

## 2. What AntMan adds beyond plain VOLE (the full machinery)

Plain QuickSilver needs: sVOLE (LPN + base OT + CR hash), IT-MACs `M = K + w Delta`, one 8-byte fix
message per committed wire, one 8-byte pair per multiplication (batched with a challenge). AntMan keeps
all of that and adds:

1. **Packing**: the B copies of each wire are interpolated into one degree-(B-1) polynomial f over F
   with f(alpha_i) = w_i on a fixed evaluation set {alpha_i}. Implemented with the alpha_i = B-th roots of
   unity and NTTs (Section 6.1), so the field must contain a B-th root of unity: **F_{2^61-1} has no
   power-of-two roots of unity** (p - 1 = 2 x 3^2 x 5^2 x 7 x 11 x 13 x 31 x 41 x 61 x 151 x 331 x 1321),
   so either a mixed-radix NTT with B | p - 1 (B = 4095 = 3^2 x 5 x 7 x 13 works, 4096 does not) or a
   different, NTT-friendly ~62-bit prime. The relation is field-agnostic (the exporter takes `--field`),
   but this is a real engineering fork from dietmc's field list.
2. **IT-PACs (information-theoretic polynomial authentication codes)**, Section 4: a commitment to a whole
   polynomial with one MAC, `M = K + f(Lambda) Delta`, where the verifier holds a second secret key
   **Lambda** (the polynomial key) in addition to Delta. Additively homomorphic like IT-MACs; addition
   gates stay free; opening costs the polynomial (B elements) so is only done on random-combination
   polynomials, never per wire.
3. **IT-PAC generation via additively homomorphic encryption (AHE)**, Section 4.3 / Fig. 3: the verifier
   sends encryptions of Lambda, Lambda^2, ..., Lambda^k once (reusable; 5.1 MB "setup" in their
   benchmarks for all B), the prover homomorphically evaluates Enc(f(Lambda) - r) using a random IT-MAC r
   from the VOLE and sends **one ciphertext per committed polynomial**. Instantiated with **single-level
   BGV** (ring-LWE; plaintext slots packed, p = 1 mod 2N), with **circuit privacy via noise flooding**
   (BFV with the rounding technique is offered as an alternative). This is the new assumption:
   **ring-LWE with the chosen BGV parameters, plus circuit privacy of the AHE**, neither of which is in the
   direct stack. The paper's Theorem 1 requires CPA security, degree restriction and circuit privacy of
   the AHE and a PRG.
4. **Commit-then-open on Lambda** (Section 2.5, "weaker IT-PAC generation"): the AHE protocol is only
   semi-honest secure, so the prover first *commits* to all its messages (functionality F_Com, realised
   with a hash, so the **random oracle** appears explicitly) and the verifier later **reveals Lambda** to the
   prover, who checks the verifier's messages were well-formed. Lambda is therefore a per-batch key that
   is opened at the end of every batch; consecutive batches need a **key-switching sub-protocol** to
   move the output IT-PACs from Lambda to a fresh Lambda' (Section 5.2). Delta stays secret as in
   QuickSilver.
5. **Multiplication check per SIMD gate**: the prover commits to h~ = f g (degree 2B-2) and to the
   degree-(B-1) reduction h with h(alpha_i) = h~(alpha_i); a batched **degree-reduction check** and a
   batched **product check** (random linear combinations, one opening of a degree-(2B-2) polynomial per
   batch). Soundness per batched check is (max degree + 2)/|F| = (2B)/|F| (Lemma 1), i.e. **2^-48 for
   B = 4096 over F_{2^61-1}, independent of the number of gates** -- better than QuickSilver's
   (t + 3)/p = 2^-30.1 at t = 2.05e9 for the same batch, because the union is over polynomial degree, not
   gate count. (Still far from 2^-128; a 128-bit NTT-friendly prime would be needed for that, and dietmc's
   no-extension-field limitation applies equally.)
6. **Input/output consistency with IT-MACs** (Fig. 4 steps 8-9): to connect the packed world to
   per-copy committed inputs (our operands and words, which Verity binds externally) the protocol
   converts between IT-MACs and IT-PACs with a Lagrange-combination CheckZero; and for non-SIMD glue
   (our epilogue is per VU but identical across VUs, so it is SIMD too) AntMan++'s wire-consistency
   compiler would be needed only if the circuit were not uniform, which ours is.
7. **Compute**: per SIMD multiplication gate, NTTs of size 2B for f, g, h~ and the BGV evaluation;
   O(B log B) per gate versus O(B) for QuickSilver. Their measurement (Table 1, |C| = 2^20, 4 threads,
   1 Gb/s): 142 ns per gate-copy at B >= 128, of which BGV homomorphic evaluation 85 ns, polynomial
   multiplication 25 ns, hashing 1 ns, the check 8 ns; QuickSilver 107 ns in the same setup. So at
   1 Gb/s AntMan is 1.3x slower in wall time and 156x smaller in communication (0.0064 elements per gate
   at B = 2048); at 50 Mb/s it is 18x faster because QuickSilver is then bandwidth-bound (Table 2).

Summary of the assumption stack delta: **+ ring-LWE (BGV, single level, noise-flooding circuit privacy),
+ explicit random-oracle commitments for commit-then-open, + a second verifier secret Lambda that is revealed
per batch, + NTT-friendly field**; unchanged: LPN regular-noise sVOLE, base OT, CR hash, designated verifier,
Delta secret for the session.

## 3. What it would buy at our numbers

Per batch of B = 4096 VUs, |C| ~ 1.0 M committed wires (0.49 M inputs + 0.50 M multiplications):

| | direct QuickSilver (measured) | AntMan (derived) |
|---|---|---|
| P -> V bytes per batch | 34.80 GB | O(B + \|C\|) elements: ~1.0 M polynomial commitments x 1 BGV ciphertext, amortised to ~0.0064-0.05 elements per gate-copy at B = 2048-4096 (their Table 1 trend halves per doubling of B) = ~1.0 M x 4096 x 0.0064 x 8 B ~ **210 MB**, + 5 MB setup, + one degree-8190 opening per check |
| per VU | 8.50 MB | **~50 kB** at their measured constant; the cost model's 5 kB/VU assumes the ciphertext overhead per polynomial is ~1 element, which is the asymptotic O(\|C\|) figure (8 MB per batch = 2 kB/VU) and needs BGV packing across the ~1 M polynomials to reach |
| soundness of the batch (F_{2^61-1}) | 2^-30.1 | ~2^-46 (a few checks at 2^-48 each) |
| prover arithmetic per VU | ~17 M F_p mul-adds (`note:r20-proof/c-vole/20260922T0646Z-report-gpu` 2.1) | ~1.0 M gates x (3 NTTs of size 8192 + BGV eval) / 4096 copies ~ **80-100 M mul-add-equivalents per VU**, i.e. ~5x more; NTT-shaped (batched size-8192 NTTs, the best-understood GPU kernel outside GEMM; not a tensor-core matmul) |
| memory | streams (229 MB) | one polynomial per live wire: 32 kB x live wires; a unit's ~10 k wires = 330 MB per unit-step, streamable along the chain |
| link needed for a 50 us/VU GPU prover | 8.5 MB / 50 us = 1.4 Tb/s (impossible) | 50 kB / 50 us = 8 Gb/s (a normal NIC); at 5 kB/VU, 0.8 Gb/s |

So AntMan-style packing is what turns the GPU floor in `note:r20-proof/c-vole/20260922T0646Z-report-gpu` from a paper number into something a link
can carry: at our measured 8.5 MB/VU no realistic network keeps up with a device prover, at ~50 kB/VU a
10 GbE link does, and the model's 5 kB/VU is the asymptote. The price is (i) the ring-LWE + RO + circuit-
privacy additions to the assumption stack, which the campaign's direction ("hash-based constructions remain
the preference") counts against track C twice, (ii) ~5x prover arithmetic, in NTT form, (iii) a field change
away from F_{2^61-1} or a mixed-radix NTT at B = 4095, and (iv) an implementation that does not exist in
swanky. The alternative that stays inside the direct stack is the relation-level 12x from `note:r20-proof/c-vole/20260922T0646Z-report-gpu` 2.3
(output-free boolean checks, F_2 bits, or a lookup argument), which brings 8.5 MB/VU to ~0.7 MB/VU and is
what the cost model priced; the two are multiplicative.

## 4. Not done

No AntMan code was run; the "derived" column is the paper's measured constants applied to our census. The
per-VU byte figure has a factor ~10 uncertainty between the asymptotic O(|C|) count and the 0.0064
elements/gate measured at B = 2048 with their BGV parameters; the NTT-field question (F_{2^61-1} lacks
power-of-two roots of unity) is real and would have to be settled before any implementation.
