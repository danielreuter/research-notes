---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `tt-out/fp4-sm120` and its family (Pearl-C4 on NVFP4)

30 Sep 2026, 11:30Z. Independent assessor (bc-d7d4b0d1). Sources:
- the row, and `internal/pouw/rtx-pro/theory-pearl-c4-domain.md` (bc-a8466279), with D-NF, D-24, D-SS with the screened-block debit, D-SB and D-SK;
- the Pearl-C4 reference (`pearl_c4.py`, tree `bfd950d8`).

## 1. The `rcp.approx` flag on the chain-only price: settled, and nothing moves

`rcp_ue4m3_sm120.cu`, `r20260930-112248-d1ec` (GPU 6, nvcc 13.0): **`rcp.approx.f32` and `rcp.approx.ftz.f32` equal `div.rn.f32(1, s)` bit for bit on all 126 valid UE4M3 scale bytes (0x01–0x7E),** the 7 subnormal-code bytes included (as FP32 values they are normal).
- **So GPU 4's 63.9 per scale is spec-legal.** The chain-only figure stands at 1.961–1.973% at 8,192³ (1.248–1.254% at 16,384³), whatever GPU 5's gate reports.
- **Forming-credited γ was never affected.**

## 2. The pieces the root named

- **The ρ_D proof (the red team's conditional GO).** ρ_D = 1/64 on the E2M1 code at a dead screen up to 9.5ρ (`rhoDFp4At_holds`, `saltDead4_screened`) is staged with standard axioms. Once the GO's conditions land (two one-constant edits and #534), the ρ_D part of the forming-credited 0.7174% is discharged.
  - **One point the proof's definition makes, borne out on my rows.** "Salt-dead" is worst case over the noise support. So a block's dominant element below the screen counts as salt-live even when its code is ±6 on essentially every real draw: a block's maximum always casts to ±6, since UE4M3's rounding keeps amax/scale in [5.65, 6.4].
  - That is what my sub-screen spike rows (spikes at 6–9ρ; `fp4-int8-route.md`) have on every block. They are the "salt-live but unchanged" class TT_OUT carries, not a gap in ρ_D.
- **The screened-block debit** (D-SS, 10:35Z ruling). Every block with clean amax² > 90ρ² is debited as salt-dead, in place of the one-in-64 row cap. It is consistent with the proof, since every salt-dead element lies in a screened block, and it removes the row cap's cliff.
- **D-SK** (B̃ keyed by this job's salt; checked by `test_b_tilde_is_keyed_by_this_jobs_salt`, #534).
  - It is what makes the salt-free base split two-sided: A′·B̃ᵀ = A0·B0ᵀ + ΔA·B̃ᵀ + A0·ΔBᵀ, with both corrections paid, a 1.23–1.95× tie on stride rows (GPU 7).
  - A variant that fixes B̃ before A's salt saves 2–24%, and it is outside D₄.
- **D-SB** (every scale byte and a_E in 0x01–0x7E, every word finite). It matches the device: sm_120 reads a scale byte's low 7 bits, 0x7F and 0xFF give NaN, and 0x00 and 0x80 are zero scales (`nvfp4-scale-bytes-sm120.md`). D-SB excludes every such byte.

## 3. What TT_OUT-FP4 still carries, and how each part stands

| Part | Standing |
|---|---|
| Skips | Chains are exact per run (`ExactRun`), so a skip keeps a word only if the skipped contributions sum to exactly zero. Identity atoms are debited; exact cross-atom cancellation sets are rarer than FP8's absorption sets. Not tested on the replay by me |
| Exact rewrites (int8, Strassen, 2:4) | **NVFP4:** stopped only by scale non-flatness (0.61–0.72 modal share, so ≤ 0.2% of depth-4 operands equal-scale; `fp4-int8-route.md`) and `tile-index-sharing/sm120` (C ↑). The pre-add budget doesn't bind on shaped rows. **MXFP4:** broken, since its flat UE8M0 scales allow depth-8 int8 Strassen at about 0.7× |
| The base split | A 1.23–1.95× tie under D-SK (GPU 7's stride rows). Not re-run by me |
| Inexact words | 23–66% of words on Qwen2.5-7B's early layers. They cost only honest debit, and are outside every rewrite |

## 4. Ratings

- **`tt-out/fp4-sm120` and `tt-out-tile/fp4-sm120`: C ↑.**
  - The weakest parts it rests on are `tile-index-sharing/sm120` (C ↑) and the pending `scale-flatness/nvfp4`, which my 11:20Z finding makes load-bearing.
  - The debit's ρ_D part is discharged once the conditional GO's edits land.
  - **What would move it to B:** a proof of tile index sharing, a rated scale-flatness row, and an FP4 fragment-level skip census on the replay (as `fragment-joint-skips.md` did for FP8).
- **The MXFP4 sibling** (`pearl-c-mxfp4-v0`, under the same statement): **D**, by the int8 route (`fp4-int8-route.md`; derived from measured components).
- **`tt-out-chain/fp4-sm120`: C ↑,** on the same basis. It asserts less, but chain-only γ is 1.96–1.97% at 8,192³, over 1%. The `rcp.approx` flag is cleared.
- **`tt-out-aw/fp4-sm120`: C.** It rests on `known-weights/sm120-nvfp4` and `structure-free/rot-nvfp4`, both C (08:45Z).
- **`tt-out-tc/fp4-sm120`: C.** It needs `a2/sm120`'s FP4 form (`a2/fp4-tile`, C).
- **`tt-out-u/fp4-sm120` and its tile twin: C** (unchanged). They carry `tt-out/fp4-sm120`'s parts plus U's blind bits.
- **`tt-out-hot/fp4-sm120`, restated without its two closures: C.**
- **`no-exact-rewrite/fp4-sm120`:** **C ↑ on NVFP4** (scale non-flatness and tile index sharing) and **D on MXFP4**.
- **`no-base-split/fp4-sm120`: C ↑** (the D-SK tie is GPU 7's measurement; not re-run by me).
