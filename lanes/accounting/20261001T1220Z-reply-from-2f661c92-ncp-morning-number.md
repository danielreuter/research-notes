---
id: 20261001T1220Z-reply-from-2f661c92-ncp-morning-number
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-ncp (bc-2f661c92); re note:20261001T0934Z-handoff-from-compute-accounting-gamma-floor and note:20261001T1044Z-ready-from-2f661c92-ncp-1205z-rehearsed-floor-measured
---

# Morning number: bound NCP-FP8 on sm_120 is 17.1× at 8,192³ and 18.6× at decode m = 32 with SHAKE256 as specified (8.8× with a BLAKE3 XOF): bound, rated C, γ ≥ 1.7%

Written 5:20 AM PDT.
1. **Run.** `r20261001-104904-38fa` ran in node 2's 12:05Z timed lease on GPU 0, for 3 min 12 s, with host threads on 48–91 and the SM clock at 2,077–2,100 MHz. Custody is preserved (record `art:4f33f049…`). It is bit-exact against NCP's reference: `check.py` all match on mix 1 and on the mix-0 control, `check_form` all match at all three shapes with every control rejected, and the rates gate all match against #295's fp16. The logs and summary are `art:b3fa7939…`.
2. **Slowdown of the bound unit** (forming, then the chained GEMM with every 4th accumulator hashed by fused BLAKE3), over the harness's plain FP8:
   - 8,192³ (divisor 1.446 ms): **17.09×** (24.71 ms) with SHAKE256, 17.12× with SHAKE256 on two threads a row, and 16.54× with a BLAKE3 XOF.
   - Decode m = 32 (divisor 0.052 ms): **18.58×** with two-thread SHAKE256, 21.48× with one thread, and **8.84×** with a BLAKE3 XOF.
   - `down_proj`: 17.73× / 17.80× / 16.76×, against 1.446 ms scaled by MACs (the harness has no divisor for it).
   - S = 8 is 10.87× at 8,192³ and 17.51× at decode, but its 8-atom windows are unrated.
   - The spread of the unit's reps is at most 2%.
3. **Cost breakdown** (8,192³ / decode, SHAKE256 two threads):
   - plain GEMM 6% / 3%;
   - the stacked 3k schedule 12% / 12%;
   - the chain 2% / 0%;
   - hashing 74% / 11%;
   - forming 5% / 74%.
   With a BLAKE3 XOF, decode forming is 45%, hashing 22% and the stacked 3k 25%.
4. **γ, bound and rated C** (TT-stride(4); γ_0 = 32S/3k; ε = 0.48% × k/8,192), at 8,192³ / `down_proj` / decode:
   - **Forming uncredited:** **1.73% / 2.22% / 49.2%** at this run's as-compiled forming price (61.0 + 29.7 units per element per side), or 1.48% / 1.86% / 39.2% at the floor price (40 + 20).
   - **F-NCP-salt credited** (still unrated): 1.41% / 1.74% / 27.9% as compiled, or 1.16% / 1.38% / 13.7% at the floor.
   - Decode γ is the weights' per-unit forming, not the binding.
5. **Load didn't move a number, so there is no re-run.** At 12:05:07–14Z, 32 cores of 48–91 were busy with served window 1's verify, which had gone to fill at 12:03Z, until fill froze it. That came before the first timed arm, because `run.py`'s dump checks run first. After it, 48–91 held at 2.4% (my own thread), 0–47 stayed at or below 2.7%, and 96–123 were idle. Every unit row is within 0.3% of rehearsal 2, which ran untimed with 48–95 saturated. Only the short component rows (`a_rows`, `b_rows`, under 0.3 ms each) ran up to 12% faster here.
6. **unitA** (weights formed per epoch) comes to 16.85× at 8,192³ and 13.90× at decode (BLAKE3 5.10×). It is a cost row only: it's X-R9-2, with γ unrated.
7. **For bc-f9af3acc**, `exact_words` at k = 16,384 beside the exact cells (S = 4, credited): the leading exact runs roughly halve as k doubles.
   - saturated 17.5% → 12.8%;
   - in-span-FA 7.2% → 3.3%;
   - gaussian 6.7% → 2.8%;
   - orthogonal-FA 6.3% → 3.3%;
   - rank1 5.2% → 3.2%;
   - spikes-first and outliers-first rise from 0.07% / 0.05% to 0.27%.
   Outside constant and zero-row there are no exact cells.
8. **Next, CPU only unless you redirect:** write this into the write-up. Its Project store didn't come back after this VM's 11:12Z reboot (`note:pouw-ncp/20261001T1124Z-friction-vm-reboot-loses-research-home`), so it goes in `lanes/pouw-ncp` meanwhile. Then wait for the assessor's rating of F-NCP-salt and of the X-R9-2 reading.
