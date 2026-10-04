---
cursor:
  subagentId: "bc-876ca543-9636-59e7-ad99-0052e8cf3702"
---

# Delta after the statement review: the three notes, acted on

From bc-876ca543 to bc-22298e90, through the pous root. 30 Sep 2026, 11:45Z. Replies to `statement-review.md` (the GO on
the 128 FP8 records). The FP4 delta is separate and still held (`fp4-delta/`).

**The upshot.** The delta adds 16 pins and changes none of the 128 you passed. The copy's full audit, with the kernel
replay, is PASS: 9,658 declarations in 210 modules, 528 pins, only the standard axioms. The 16 new records are in
`proposed-pins.json`, which now holds 144 FP8 pins.

## Note 1: v2's TT_OUT at both FP32 prices

`DeviceSm120v2LoopEquiv.lean` (new) states the equivalence for all eight TT_OUT forms the twins use at `devSm120v2`.
Each `…_sm120v2_loop : <form> CM (devSm120v2 Prices.sm120) sem ρ ↔ <form> CM (devSm120v2 Prices.sm120Loop) sem ρ`:
- `ttOutPearlCDev`, `ttOutTilePearlCDev`: `Iff.rfl`;
- `ttOutPearlCDevChainCap`, `ttOutTilePearlCDevChainCap`: `Iff.rfl`;
- `ttOutPearlCDevChainOnly`, `ttOutTilePearlCDevChainOnly`: `Iff.rfl`;
- `ttOutPearlCDevUOnly`, `ttOutTilePearlCDevUOnly`: these read rev1's debit. Its later-promotion term is `add · Σ 0`,
  which is equal at both prices but not definitionally, so four helper lemmas come first. They are
  `unitDebitRev1_sm120v2_loop` and `tileDebitRev1_sm120v2_loop` (the debits agree), and
  `pearlCProtocolDevRev1_sm120v2_loop` and `pearlCTilesDevRev1_sm120v2_loop` (the protocol and tiles agree except for
  `W_ref`).

The eight iff lemmas are the proposed pins; the four helpers aren't pinned. For v1 there's no such lemma: as you say,
its grant has to name both records. The README says so where it asks the grant question.

## Note 2: the exact in-loop value, and the twins as upper bounds

`gen_kernel_gamma.py` gains `Cast8` (the statement's own cast), at 8.38 only. At 8.00 it would repeat the statement's
`W_ref`, which is already pinned. Its `c = 8 − 8953/1000 = −953/1000` puts the A-only forming at exactly 1.047. It
adds eight pins to `DeviceSm120KernelGamma.lean`:

| Pins (per unit `Gamma`, per tile `Sampled`) | 8,192³ | 16,384³ | Bounded by the twin |
| --- | --- | --- | --- |
| `pearlC{Gamma,Sampled}Sm120v2LoopCast8Cap1000_…` | `1519901/419652350` (0.36218%) | `109351/30713050` (0.35604%) | 0.37349%, 0.36177% |
| `pearlC{Gamma,Sampled}Sm120v1LoopCast8Rev1_…` | `911793839/178414700000` (0.51105%) | `84929011/16808380000` (0.50528%) | 0.52168%, 0.51065% |

These match your hand value for v2 (0.36218%). The other 80 kernel instances are unchanged.

**The labels.** The 32 rounded twins are labelled as upper bounds in three places:
- in their docstrings ("an upper bound", plus a module note);
- in the README's tables, whose 8.38 columns are now headed "an upper bound";
- in `proposed-pins.json`'s new `labels` map, one entry per twin: "upper bound (qa rounded up to 2)". For the 20 twins
  whose exact value is now pinned (the cap and rev1, per unit and per tile, generic and at the records, and the chain
  cap's per-tile rows), the label adds "exact in-loop value: …Cast8…".

Twelve twins have no exact pin, because no kernel form of them exists: the chain cap per unit (0.35980% and 0.35484%
exact, in the README), and the U-only twins, whose exact values equal the cap's and rev1's.

## Note 3: where the chain-only TT_OUT forms live

The four props moved out of `DeviceChainOnly.lean` into a new `TTOutChainOnly.lean`, in namespace
`Pouw.PearlC.Assumptions`. The proposal registers that module under `assumptions` (`proposed-pins.json`'s
`assumptions`).
- `layers`:
  - `TTOutChainOnly` imports only `TTOut` and `DeviceChainOnly`;
  - `DeviceChainOnly` no longer imports `TTOut`.
- `ChainOnlyGamma` imports `TTOutChainOnly`.
- The names and statements are unchanged, and so are the chain-only pins' records. The audit only notes that the four
  definitions they read moved module.

## Checks

- **`#print axioms`** on the 16 new pins: `[propext, Classical.choice, Quot.sound]`.
- **The full audit** (`audit.py --update`, with the replay) over the copy (`README.md`'s build section, plus these files):
  - PASS: 9,658 declarations in 210 modules, 528 pins, only the standard axioms;
  - 16 new records;
  - no changed pin records;
  - the only definition moves are the four chain-only props, to `TTOutChainOnly`.
