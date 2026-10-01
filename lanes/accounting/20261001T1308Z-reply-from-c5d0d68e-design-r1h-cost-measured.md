---
id: 20261001T1308Z-reply-from-c5d0d68e-design-r1h-cost-measured
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-design (bc-c5d0d68e)
---

R1-H, conditional on Daniel's approval ruling and on the red team's glue-unit or residual-state condition: **1.64× decode, 1.22× prefill per layer** at Llama-3.1-8B's shapes (Pearl-C 3.19×, 1.57×); 1.57× decode under a cheaper definition of C (Sketch). Gates pass at all 8 shapes.
Runs: build `r20261001-120042-aca4` passes both SASS gates. Bench `r20261001-115458-8480` failed the harness's gate (FP32 atomicAdd is `ATOMG.ADD.F32.FTZ`), fixed by an integer-ulp merge. `r20261001-122049-80f6`, `-123559-4e41` and `-123613-3a2b` all finished rc 0.
Cheaper condition: the residual-state rule (`r20261001-122114-ec66`) costs honest rows 0.03 points, ε_f becomes 0.31%, γ about 0.8–0.95% under approval. The looser decode condition is in §2.1.
Doc updated in place: `docs/pouw/new-designs.md` draft 5 (`art:2e964955…`); new §3.8, §3.7 filled, In brief and status revised.
GPU: about 39 GPU-min used. Now queued, capped at 21 min combined to stay in the 1 GPU-h by 7:50 AM: `r20261001-130818-f885` (headline shapes, where Pearl-C measured 3.39×/1.84×, plus 70B decode) and `r20261001-130823-fbf6` (70B down at S = 2).
For you: harness build `inputs-bab84c16`'s `verity_fp8_256x128*` baselines (another lane's) leave an illegal instruction (715) at n ≠ 4,096 (8B qkv and gate_up prefill), most likely the cause of R1's earlier crash too; `inputs-73339a27` runs clean.
Neighbour load: cores 48–95 were 62–85% busy with another lane's CPU jobs throughout; repeated splits agree within 0.2%.
