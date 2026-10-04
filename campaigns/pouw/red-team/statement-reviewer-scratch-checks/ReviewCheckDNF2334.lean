import Pouw.PearlC.Fp4FormingCode

namespace Pouw.PearlC.Fp4Dev.DNF2334
open Pouw.PearlC Pouw.PearlC.Fp4Dev

theorem rhoD_rfl : CodeProofs.RhoDFp4At 90 = RhoDFp4 := rfl
theorem rowRules_rfl : CodeProofs.RowRules4At 90 = RowRules4 := rfl
theorem gap_closed (k : ℕ) (x : Fin k → ℚ) : ¬ RowAdmit4 (fun _ _ => (-1 / 4096 : ℚ)) k x := by
  rintro ⟨h, -, -⟩; norm_num at h
theorem negzero_by_byte (k : ℕ) (x : Fin k → ℚ) : ¬ RowAdmit4 (fun _ _ => (-0 : ℚ)) k x := by
  rintro ⟨-, h8, -⟩; have : (e4m3 (-0 : ℚ)).val = 0 := by decide +kernel
  simp only [this] at h8; omega
theorem cL_matches_556 :
    cL 8192 8192 8192 = 6612 / 10000 ∧
    cL 3000 5000 700 = 8471 / 10000 ∧
    cL 1 1 1 = 20000 / 10000 ∧
    cL 128 16 128 = 20000 / 10000 ∧
    cL 129 17 129 = 15873 / 10000 ∧
    cL 16777216 65536 262144 = 2697 / 10000 ∧
    cL 16777215 65535 262143 = 2697 / 10000 ∧
    cL 65536 8192 1024 = 8081 / 10000 ∧
    cL 1024 8192 65536 = 8081 / 10000 ∧
    cL 20000 9000 100 = 11591 / 10000 ∧
    cL 10866025 19773 207002 = 2990 / 10000 ∧
    cL 1620224 9495 49352 = 3469 / 10000 ∧
    cL 12270484 7603 112564 = 3937 / 10000 ∧
    cL 1258146 11266 227356 = 3364 / 10000 ∧
    cL 14031530 9157 126177 = 3364 / 10000 ∧
    cL 3043824 55643 30991 = 3319 / 10000 ∧
    cL 4154105 29261 32434 = 3373 / 10000 ∧
    cL 13310389 6500 115911 = 3937 / 10000 ∧
    cL 1563056 17456 151839 = 2990 / 10000 ∧
    cL 14063973 18908 61758 = 3154 / 10000 ∧
    cL 10350933 23689 54031 = 3154 / 10000 ∧
    cL 6303906 48811 51082 = 2964 / 10000 ∧
    cL 2106849 7813 107982 = 3937 / 10000 ∧
    cL 16656907 56046 164704 = 2697 / 10000 ∧
    cL 15623007 59400 189574 = 2697 / 10000 ∧
    cL 10058512 32562 94250 = 2990 / 10000 ∧
    cL 8190520 10729 157418 = 3364 / 10000 ∧
    cL 16613349 45021 235319 = 2697 / 10000 ∧
    cL 9661589 9595 61901 = 3469 / 10000 ∧
    cL 14029874 21622 179336 = 2990 / 10000 ∧
    cL 5099755 64090 221092 = 2697 / 10000 ∧
    cL 1315578 10174 164495 = 3364 / 10000 ∧
    cL 11412613 45899 260401 = 2697 / 10000 ∧
    cL 15307711 9013 49072 = 3469 / 10000 ∧
    cL 9057660 62142 34079 = 2964 / 10000 ∧
    cL 2035729 40581 233645 = 2697 / 10000 ∧
    cL 9549442 50567 181931 = 2697 / 10000 ∧
    cL 757087 60516 186366 = 3394 / 10000 ∧
    cL 5638768 15348 258838 = 3364 / 10000 ∧
    cL 1978183 28601 150698 = 2990 / 10000 := by decide +kernel
theorem cL_past : cL (2 ^ 24 + 1) 8192 8192 = 0 ∧ cL 8192 8192 (2 ^ 18 + 1) = 0 := by decide +kernel
end Pouw.PearlC.Fp4Dev.DNF2334

#print axioms Pouw.PearlC.Fp4Dev.DNF2334.rhoD_rfl
#print axioms Pouw.PearlC.Fp4Dev.DNF2334.rowRules_rfl
#print axioms Pouw.PearlC.Fp4Dev.DNF2334.gap_closed
#print axioms Pouw.PearlC.Fp4Dev.DNF2334.negzero_by_byte
#print axioms Pouw.PearlC.Fp4Dev.DNF2334.cL_matches_556
#print axioms Pouw.PearlC.Fp4Dev.DNF2334.cL_past
