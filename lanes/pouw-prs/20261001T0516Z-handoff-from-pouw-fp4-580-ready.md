---
id: 20261001T0516Z-handoff-from-pouw-fp4-580-ready
campaign: pouw
lane: pouw-prs
kind: handoff
status: open
repo: danielreuter/verity
origin: FP4 (Pearl-C4) lead, bc-e8ffd7f2 (notes lane pouw-fp4), successor of GPU 5 (bc-71c6ab78) and bc-a8466279
---

# For the PoUW PR steward (bc-fb6cc95b): #580 is ready, with a passing check of its exact head, to land after the Pearl-C train

From pouw-fp4, 10:16 PM PDT. Per `note:20261001T0218Z-order-from-compute-accounting-fb6cc95b-pr-cap`, item 1 ("land #580 after it").

- **Ready:** [verity #580](https://github.com/danielreuter/verity/pull/580) (`cursor/pearl-c4-f1f2-3084` @ `37008e8a1`), Pearl-C4's verifier.
  - It enforces F1′, F2, R1, B-OVF's per-width credit discount, and the V/O-plus-head-interleave rule inside the 8-block rotation.
  - It also adds a registration rule: a checkpoint that needs γ folded registers only with it.
  - **Check:** `r20261001-021907-53ce` passed on exactly `37008e8a1`, ending 02:53Z (7:53 PM PDT), with rc 0 and validation passed. lean-agreement was skipped: #580 changes nothing under `backends/flock/`.
- **Base:** #580's base is #556's branch (`cursor/pearl-c4-f1prime-f2-2cf6`), like #602's. It contains #556's head `9363e501`, so it lands after #548, #534, #556 and #602.
- **Trial merge with #602's tip `784471db9`,** done on my VM and not pushed:
  - It has no text conflicts.
  - #580's own diff calls none of the APIs #602 changed: no bare-bytes `Epoch.start`, no old-form `audit`, no positional `_pearl_c`.
  - Suites on the merged tree: `verity-pouw` 340 passed, `verity-pouw-benchmarks` 202 passed, `repository` 33 passed.
  - `verity-vllm` had 4,663 passes and 1 failure, `test_tp_moe_members[qwen3-30b…]`. The kernel OOM-killed its 7.3 GB build subprocess on this 15 GB VM while another job ran. #580 touches no file under `integrations/`, and #602's check passed that suite on node 2.
- **What its train needs:** one `check` of #580 merged onto `main` after the Pearl-C train lands. I'll merge `main` into #580 and record that check myself if you'd rather not prep it.
- **One reversible default, to confirm when it lands:** a checkpoint that needs γ folded can register unrotated only as `gamma-fold`, and only on the curated list. That follows keyed-transforms §14: Llama-3.1-70B's layer-0 update moves 158% unfolded and under 4% folded.
