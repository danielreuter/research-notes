import Pouw.PearlC.Fp4FormingCode
open Pouw.PearlC.Fp4Dev.CodeProofs in
example : RhoDFp4At 90 = Pouw.PearlC.Fp4Dev.RhoDFp4 := rfl
open Pouw.PearlC.Fp4Dev.CodeProofs in
example {alpha beta : (k : ℕ) → (Fin k → ℚ) → ℚ} (hp : PinnedScales alpha beta) : Pouw.PearlC.Fp4Dev.RhoDFp4 alpha beta := rhoDFp4At_ninety hp
