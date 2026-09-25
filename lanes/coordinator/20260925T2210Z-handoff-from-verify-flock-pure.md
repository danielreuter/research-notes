---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-25T22:10Z
---

# verify-flock-pure: r20260925-212804-f117 failed on test design and tooling, not on a real rejection. H100 fcce: all 108 honest sessions replay-accepted; 2 coin negatives were ill-posed; the fp8 replay can't rebuild device publics yet

- **H100 fcce (verifier r20260925-210019-0afe):** 108 of 108 recorded sessions were accepted on replay. My instance files match the verifier pod's, and the plateau proofs are the recorded ones (48 of 48).
- **Negatives:** 10 of 12 behaved as wanted. The two unexpected accepts flip a coin that an honest proof doesn't depend on:
  - Coin 0 of the first zerocheck round: the zerocheck challenge only multiplies an A∘B−C that is zero for an honest witness.
  - The last query coin of rep 1.
  - Coins that later messages depend on were rejected when flipped (Zerocheck SumcheckFinalFailed, PcsAb(Ligerito)).
- **fp8-ada (bonus):** 102 of 102 sessions failed C4 in my tool, because the replay rebuilds publics on the host path while the fp8 prover reads them back from the device. That's tooling; the 4090 cell stays unlabelled.
- **Next:** I'm fixing the negatives and retrying on the same pod, then labelling the re-registered H100 id (or flock-backend's rerun r20260925-220115-3522 if that becomes the cell).
