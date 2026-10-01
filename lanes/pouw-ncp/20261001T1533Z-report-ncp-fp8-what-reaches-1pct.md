---
id: 20261001T1533Z-report-ncp-fp8-what-reaches-1pct
campaign: pouw
lane: pouw-ncp
kind: report
status: open
repo: danielreuter/verity
origin: pouw-ncp (bc-2f661c92); re note:20261001T1516Z-handoff-from-compute-accounting-ncp-rated and note:20261001T1505Z-reply-from-f9af3acc-ncp-salt-epoch-epsilon
---

# What would have to change for NCP-FP8 to reach γ ≤ 1% on sm_120

Written 8:33 AM PDT.

**Bottom line.**
- **At 8,192³:** the worst cell's frozen share ε must fall from 0.78% to at most 0.32%, together with an honest kernel that forms at the forming floor: at least 40 + 20 units per element per side, where today's compiled kernel takes 60 + 30. With today's forming, ε would have to fall to about 0.04%.
  - The binding's own floor γ_0 is 0.52% at S = 4, and it doesn't move without leaving the 20× budget.
  - Even with all of the forming credited, ε must still be at most 0.48%.
- **At decode (m = 32):** no change to the binding or to ε comes near 1%. The per-unit weight forming is the problem, and fixing it is a protocol change.
- **My recommendation:** keep NCP-FP8 as a γ ≤ 1% candidate for prefill shapes only, conditional on a census showing an ε fix. Drop it as a candidate at decode.

## Where today's 1.73% comes from (8,192³, bound chash S = 4, f_salt = 36 credited, forming as compiled)

γ = 1 − (1 − γ_core)/Ω*, with γ_core = γ_0 + ε. To first order the three terms add:

| Term | Value | What sets it |
|---|---:|---|
| γ_0 = 32S/(3k) | 0.52% | The binding's spacing: the last segment of each chain is uncredited |
| ε, the worst cell | 0.78% | TT-stride(4)'s frozen segments under spike-dominated accumulators (`spike1-first`); it grows with k, to 1.27% at 16,384 |
| φ, uncredited forming | 0.44% | (F − f_c)(m + n)/(3mn), with F = 61.0 + 29.7 as compiled and f_c = 36; independent of k |

## Each lever and the γ it gives

All computed exactly (not first order) with the assessor's convention:

| Change | 8,192³ | Decode m = 32 |
|---|---:|---:|
| Today (S = 4, ε 0.78%, compiled forming, credit 36) | 1.73% | 30.2% |
| Credit at 40, the pipe bound below: rated C at 15:43Z, so this is the rated figure now | 1.70% | 28.2% |
| Honest forming at the pipe floor (40 + 20), credit 40 | 1.46% | 14.0% |
| ε halved to 0.39% | 1.35% | 30.0% |
| ε halved, and forming at the floor credited at 40 | **1.07%** | 13.7% |
| ε = 0 | **0.96%** | 29.7% |
| ε = 0, and forming at the floor credited at 40 | **0.68%** | 13.3% |
| S = 2 (γ_0 0.26%), ε 0.39%, forming at the floor credited at 40 | **0.81%** | 13.4% |
| All forming credited (impossible: the data-only steps read no salt), ε 0.78% | 1.30% | 1.30% |

The ε each configuration can afford, for γ ≤ 1% at 8,192³:
- **S = 4:** 0.04% with today's forming; 0.32% with an honest kernel at the floor credited at 40; 0.48% with every forming step credited.
- **S = 2:** 0.30% with today's forming; 0.58% with an honest kernel at the floor.
- **The cost of S = 2:** the GEMM alone is 30.3× at 8,192³ (this morning's run), so it leaves the 20× budget.
- **Larger k doesn't help:** γ_0 halves at k = 16,384, but the worst-cell ε rises to 1.27%.

## What could cut ε (each touches the binding or the forming, so each needs a rating)

1. **The noise amplitude from the row's maximum instead of the local amplitude.**
   - A 32-product contribution then can't fall under a spike-dominated accumulator's window, so segments stop freezing, which should take ε toward 0.
   - The cost is the useful output's accuracy: the noise grows to the row's maximum before it is removed.
   - It touches D-3s's forming, and the γ argument's A2_fp and AdmitsRef must be re-checked. Unmeasured.
2. **A salted order of the 32-wide atoms along k, drawn per unit after root_A.**
   - The worst cell is the spike placed first in the chain. A salted order makes its position uniform, so the frozen run after it averages about half: ε about 0.39%, my estimate, unmeasured.
   - The kernel cost is address arithmetic on the k-tile loads.
   - It touches DistinctLive's census and the chain's definition. Alone it reaches 1.35%, or 1.07% with the forming at the floor.
3. **Fresh segments don't work.** I measured it at 09:56Z: they remove the freezing, but 86–99% of their words are exact in 15 families, so they credit less.

## The forming: what the 15:15Z run measured (untimed; `r20261001-151500-a717`, commit `0d2ff8b68`)

- **The fused centre and scale** (one HFMA2) is bit-exact. The gate is all match, 1,920 words, on E4M3 amplitudes, held to the unfused reference. On #295's fp16 it is exhaustively equal: 120 amplitudes × 1,024 fields, 0 mismatches.
- **The fusion doesn't move the honest price:** 60.2 units per element against 61.0 unfused. The data-only steps are 29.8.
  - The compiled loop is bound by the ALU pipe, about 0.75 PRMT per element packing the casts' halves, plus MOVs.
  - Reaching the floor needs a hand-scheduled kernel without the PRMTs.
- **The pair controls** (units an instruction; about 16 means one shared pipe, 8–10.7 means two pipes):
  - HFMA2 + HADD2 16.1: every f16x2 form shares one half-rate pipe, although ptxas alternates the HADD2 and HFMA2 forms.
  - F2FP + LOP3 16.0: the casts share the ALU pipe with LOP3.
  - HADD2 + F2FP 10.8: separate pipes; 10.67 is that pair's separate-pipe value.
  - HADD2 + LOP3 9.5 and HFMA2 + HMNMX2 10.1: separate.
  - HADD2 + FFMA 14.1: FFMA shares the FMA complex.
- **So the fused salted steps' bound is 40, not 36.**
  - The FMA complex carries 2.5 f16x2 instructions × 16 = 40.
  - The ALU pipe carries (LOP3 + F2FP) 2.0 × 16 = 32.
  - Dispatch is 4.5 × 8 = 36.
  - Moving an add to FFMA costs the same 8 per element-op on the same complex, plus conversions on the ALU.
  - The assessor rated this restatement of F-NCP-salt at 40 C at 15:43Z (`note:20261001T1543Z-reply-from-f9af3acc-ncp-salt-pipe-bound`), superseding 36.
    - Five f16 roundings per element remain, which is 2.5 f16x2 instructions on the one half-rate pipe.
    - A tensor-core adder costs at least 16 per element-op, and integer emulation pushes the ALU pipe past 40.
    - It would break only for a route that drops one of the five roundings or shares one between blocks.

## Decode needs a protocol change

- **The share:** at m = 32 the uncredited forming share is about (F − f_c)/(3m) of the work.
  - Getting it to 0.2% needs m ≥ about 3,300 rows per unit, even with the forming at the floor.
  - Forming the weights once per epoch is X-R9-2 (ε ≈ 6.8% at r = 1).
- **What decode would need:** a way for the weight noise to read root_A without re-forming kn entries per unit. That is a question for #295's design, not for the kernel.

## Evidence

- The timed run is `r20261001-104904-38fa` (custody record `art:4f33f049…`); its checks and summary are `art:b3fa7939…`.
- The forming rates are in run `r20261001-151500-a717`.
- The γ figures are computed from the assessor's 15:05Z ratings with the formula in their note.
- GPU work is stopped, per 1516Z. The census for lever 1 or 2 would run on the CPU: `liveness.py` over #295's own forming. I'll run it only if you say so.
