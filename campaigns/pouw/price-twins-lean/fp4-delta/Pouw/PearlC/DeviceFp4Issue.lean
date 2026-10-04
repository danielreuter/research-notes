import Pouw.PearlC.DeviceFp4

/-!
# Pearl-C4's prices on sm_120 at the issue-bound FP32 price (the price-twins lane's file; definitions only, staged)

`Fp4Prices.sm120` prices Pearl-C4's FP32 operations at the measured in-loop 8.38 FP8 units. γ's price rule also
computes γ at the issue-bound 8.00 (`Prices.sm120`'s FADD), at the prices this file holds, in FP4 units (an FP8 unit is
2):
* a BF16 MAC is 4;
* `fs = 5429/50 = 108.58`, made up of:
  - the noise atom, 64;
  - the salted block scale per block of 16 (`theory-pearl-c4-domain.md` §8a), `2·(8.0 + 12.74 + 63.9 + 2·8.00)/16 =
    12.58`. That is the UE4M3 encode alone, the `F2FP` decode and the `MUFU` reciprocal, which are not FP32 adds or
    multiplies and keep their prices, plus two FP32 ops at 8.00: the FMUL `amax·1/6` and the decode's `HADD2.F32`. The
    reciprocal is `rcp.approx`, which the assessor (bc-d7d4b0d1) found exact on all 126 UE4M3 scales;
  - the cast, the FMUL plus the E2M1 cvt's F2FP alone, `2·8.00 + 2·8.0 = 32`;
* `qa = 18`: the noisy amax (one FMNMX, `2·8.00`) and ρ's squared accumulate on every 8th element (`2·8.00/8`).
-/

namespace Pouw.PearlC

/-- **sm_120's prices in FP4 units at the issue-bound FP32 price**: every FP32 operation at 8.00. -/
def Fp4Prices.sm120Issue : Fp4Prices := ⟨4, 5429 / 50, 18⟩

/-! ## The scale step as a parameter

bc-f5bf55c8 recommends crediting the block scale at `lut256` (`docs/pouw/pearl-c4-v3.md` §15), the cheapest spec-legal
path, and bc-a8466279 rules on it. So that the repricing is a rebuild, the records below take the scale step as a
parameter, `Fp4ScalePath`, beside the FP32 price. -/

/-- **A block-scale path**, per element in FP4 units: `fixed`, the work no FP32 price reprices, and `fp32Ops`, the FP32
operations per block of 16, each at the FADD price. -/
structure Fp4ScalePath where
  fixed : ℚ
  fp32Ops : ℚ
  fixed_nonneg : 0 ≤ fixed
  fp32Ops_nonneg : 0 ≤ fp32Ops

/-- **`rcp.approx`**: the UE4M3 encode alone (8.0), the `F2FP` decode (12.74) and the `MUFU` reciprocal (63.9) per
block, `2·84.64/16 = 10.58` per element, and two FP32 ops per block, the FMUL `amax·1/6` and the decode's `HADD2.F32`
(`theory-pearl-c4-domain.md` §8a). -/
def Fp4ScalePath.rcpApprox : Fp4ScalePath := ⟨529 / 50, 2, by norm_num, by norm_num⟩

/-- **`lut256`**: half an `F2FP`, 1.25 `PRMT` and one `LDS` per block, 60 FP8 units, `2·60/16 = 7.5` per element, and
one FP32 op per block, the FMUL `amax·1/6` (the table replaces the decode and its widening). These are W1
per-instruction prices (`pearl-c4-v3.md` §15), not GPU 5's in-loop marginal 1.94. -/
def Fp4ScalePath.lut256 : Fp4ScalePath := ⟨15 / 2, 1, by norm_num, by norm_num⟩

/-- **sm_120's FP4 prices at an FP32 price `fadd` and a scale path `p`**, in FP4 units: a BF16 MAC 4;
`fs = 64 + p.fixed + p.fp32Ops·2·fadd/16 + 2·fadd + 2·8.0` (the noise atom, the block scale, and the cast's FMUL and
F2FP); `qa = 2·fadd + 2·fadd/8` (the noisy amax and ρ's every-8th accumulate). At `fadd = 8` it is the issue-bound
record, and at `1047/125` the in-loop one. -/
def Fp4Prices.sm120At (fadd : ℚ) (p : Fp4ScalePath) : Fp4Prices :=
  ⟨4, 64 + p.fixed + p.fp32Ops * fadd / 8 + 2 * fadd + 16, 2 * fadd + fadd / 4⟩

/-- **Pearl-C4's γ at an FP4 record** under the cap `ρ`: `1 − (399/400)/ω` with `ω = wrefFp4/((1 − ρ)·creditFp4)`. -/
def gammaFp4 (d : Fp4Device) (ρ : ℚ) (s : Shape) : ℚ :=
  1 - (1 - 1 / 400) / (wrefFp4 d s / ((1 - ρ) * creditFp4 d s))

end Pouw.PearlC
