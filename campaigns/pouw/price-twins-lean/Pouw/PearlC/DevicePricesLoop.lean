import Pouw.PearlC.Device

/-!
# The RTX PRO 6000's W1 prices in the measured loop (the price-twins lane's file; definitions only, staged)

γ's price rule computes γ at the issue-bound FP32 add (`Prices.sm120`, 8.00) and at the measured in-loop one (8.376),
and publishes the larger. This file holds the in-loop record (`internal/pouw/ttout-restatements.md` §2; node 2 at
locked 2,100 MHz, the runs `DevicePrices` cites):
* an FP32 add is 8.376 per word (3 loop instructions per 64);
* a BF16 MAC is 2.000;
* the credited forming is the k32 noise atom (32) plus the E4M3 cast at its cheapest implementation, 8.0, at both FP32
  prices (the coordinator's ruling, 30 Sep 10:49Z, with `DevicePrices`' rule and the panel): 40 per element;
* the A-only forming is one FFMA on every 8th element at 8.376, 1.047 per element.

`Costs` counts the forming in whole units, so the record rounds the A-only forming up to `qa = 2`. That raises `W_ref`
and not the credit, so it raises γ at every shape: γ here is above γ at the measured 1.047 (0.37349% against 0.36218%
for v2 at the cap 1/1,000, 8192³). The add is exact.
-/

namespace Pouw.PearlC

/-- sm_120's W1 prices in the measured loop: an FP32 add `1047/125 = 8.376`, a BF16 MAC 2, credited forming 40 (the
cast at its cheapest 8.0) and A-only forming 2 per element (1.047 measured, rounded up so that γ does not fall). -/
def Prices.sm120Loop : Prices := ⟨1047 / 125, 2, ⟨40, 2⟩⟩

end Pouw.PearlC
