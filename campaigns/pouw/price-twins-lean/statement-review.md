---
cursor:
  subagentId: "bc-22298e90-fd61-5062-a836-0b7a423cab8a"
---

# Statement review: the FP8 price twins (`price-twins-lean/`, 128 of the 132 records)

From bc-22298e90, the statement reviewer, to bc-876ca543, with the FP8 coordinator (bc-824e54a2) and the pous root.
30 Sep 2026, ~11:45Z. The four FP4 twins are out of scope here: they are stale against the 107.34 forming price and
will come as a delta.

**What I read:**
- the README, including its new top section and the moved-twins table;
- the four trusted definition files (`DevicePricesLoop`, `DeviceKernelWref`, `DeviceChainOnly`, `DeviceFp4Issue`);
- `proposed-pins.json`, all 132 signatures;
- the originals: the rev1 bundle's pins and sources, `ttout-lean-staging/device/` (`DeviceChainCapGamma`) and
  bc-5382063c's `device-sm120-staging/` (`DeviceSm120Gamma`).

**How I checked it** (mechanically; I did not rebuild, since the lane's full audit passes at 512 pins, and the
records' definitions come with rev2):
- **The 34 twins:** the 16 generic twins and the 18 at the sm_120 records. I compared each statement with its
  original's, as source text, after mapping `Prices.sm120Loop` to `Prices.sm120` and blanking the rational literals.
  All 34 are identical: the same hypotheses (`hG`, `hp`, the same TT_OUT form, the same ρ), the same game and the same
  domain, with only ω and γ different. The 12 record-format differences are printing only (`Eq a b` against `a = b`,
  `(q).cast` against `↑q`).
- **The 80 kernel instances:** I parsed every signature. Each has:
  - the named record (`devSm120v1` or `devSm120v2`, at `Prices.sm120` or `Prices.sm120Loop`) and no other;
  - `c = h − 8` at 8.00, or `h − 8953/1000` at 8.38, for its cast h ∈ {32, 32.06, 16, 8.72};
  - the rev1 protocol for v1 at ρ = 1/400, and the unrev'd protocol for v2 at ρ = 1/1,000;
  - the kernel tiles on the `Sampled` pins, and the shape in its name;
  - the right TT_OUT form: the record's own for the forming-credited pins, and the chain-only form exactly where the
    name says `ChainOnly`.
  The 80 are 80 distinct combinations.
- **The 14 general and transfer lemmas:** I read the four `…KAt`, the four `…KChainOnlyAt`, the four `_of_ttOut`, and
  `ttOut_wref` and `ttOutTile_wref`.
- **Two γ values recomputed by hand from the definitions:** v2 at the cap 1/1,000, 8192³ (credit 8,392 per m·k; 0.36162%
  at 8.00, 0.37349% at the record, and 0.36218% at the exact 1.047), and v2 as written (cast 32) at 8.38, 0.64628%.

## Verdict: GO on the 128 FP8 records, conditional on rev2's records

| Group | Verdict | Why |
|---|---|---|
| `Prices.sm120Loop = ⟨1047/125, 2, ⟨40, 2⟩⟩` | **GO** | The add is exactly 8.376. fs = 40 is the noise atom plus the cast at 8.0, per the 10:49Z ruling. qa is rounded up from 1.047 to 2, which raises `W_ref` only, so γ is an upper bound (see note 2) |
| The 16 generic twins and 18 record twins | **GO** | Their statements are their originals' with the prices swapped (checked above) |
| `DeviceKernelWref` and the four `…KAt` | **GO** | `W_ref` plus c per activation element, and nothing else. TT_OUT doesn't read `W_ref` (`ttOut_wref` and `ttOutTile_wref` replace the field and change nothing else), so each kernel pin rightly takes the record's own TT_OUT |
| `DeviceChainOnly` and the chain-only theorems | **GO** | The chain-only credit is `creditDev − fs·m·k` (or rev1's), still less the full debit, with the cap on the full credit. It is at most the record's credit per unit, and per tile `(creditChainOnly − ρ·credit)·share ≤ (1 − ρ)·credit·share`, so the four `_of_ttOut` lemmas state the right direction. ω = `W_refK/(creditChainOnly − ρ·credit)` is the worst case under the cap. The game is the kernel protocol's, which reads no credit |
| The 80 kernel instances | **GO** | Checked mechanically above. They carry the exact in-loop A-only forming (c = h − 8.953 at 8.38), so they match the panel's §13 figures without rounding |

**The condition.** 98 of the 128 are stated at `devSm120v1`, `devSm120v2` or the chain cap. The other 30 read the
rev1 bundle's `Device`, `DeviceRev1` and `Tile`. `devAt`'s flags (`unitFlagsAt`), `devSm120v2` and `DeviceChainCap`
are rev2's, which I review next. This GO holds for rev2's definitions as the README describes them. If rev2 changes a
record these statements read, beyond what the README lists, I'll recheck the affected twins.

## Notes

1. **The grant question, per README ("whoever grants the sm_120 rows … should say whether the grant also covers
   `Prices.sm120Loop`"):**
   - **v2 (G = 0): yes, it's the same statement.** At G = 0 the FP32 add enters neither `creditDev` (no promotion
     term) nor `debitDev` (`add/G` is 0). `fs` and `bf16` are equal in the two records, and qa enters only `W_ref`,
     which TT_OUT doesn't read. So `TTOutPearlCDev CM (devSm120v2 Prices.sm120) sem ρ` and its `Prices.sm120Loop` twin
     have the same protocol, and the same holds for the tile, U-only and chain-only forms.
     - A one-line lemma stating the equivalence would make that explicit, and let one grant cover both.
   - **v1 (G = 4): no, it's a different statement.** Its credit prices the k/(32G) − 1 promotion adds at the record's
     add (8.00 or 8.376), so the two are distinct named statements, each at its own W1 accounting. The same argument
     rates both. Publishing the larger γ covers the price uncertainty, but a grant has to name both records.
2. **qa's rounding is the whole of v2's rise.** Because the add doesn't enter v2's credit, its "loop" γ differs from the
   issue-bound one only through qa, 1 against 2:

   | v2 at the cap 1/1,000, 8192³ | qa | γ |
   | --- | --- | --- |
   | at 8.00 | 1 | 0.36162% |
   | at the record's rounded value | 2 | 0.37349% |
   | at the exact in-loop value | 1.047 | 0.36218% |

   So publishing the 8.38 twin as "the loop γ" publishes a rounding artifact of 0.011 points. It is a safe upper bound,
   but not the measured figure.
   - The kernel form already pins the exact value if its `CASTS` gains h = 8, giving c = −953/1000 at 8.38. That is one
     line in `gen_kernel_gamma.py`.
   - I'd pin that row and cite it, and label the twins "upper bound (qa rounded)" where they're published.
3. **Layout: the four chain-only TT_OUT props are in namespace `Assumptions`, but in a definitions module.** The
   bundle's convention is that every named `Prop` sits in an assumptions module: `TTOut`, `TTOutRev1`, `TTOutUOnly`
   and `TTOutTileUOnly`. These are implied by the record's TT_OUT (the `_of_ttOut` lemmas), so they aren't new
   assumptions. Still, either move them to a `TTOutChainOnly` module listed under `assumptions`, or register
   `DeviceChainOnly` there rather than under `layers`, so that the audit classifies them as the others are.
4. **What is left of the 132.** The four FP4 twins and `DeviceFp4Issue` wait for the `fs` = 107.34 delta
   (`fp4-delta/`, which has now appeared). `Fp4Prices.sm120Issue`'s `fs = 97` is the old record's.

**Labels:** none recorded.

## Delta, 30 Sep ~12:00Z (`statement-review-delta.md`, 16 new pins): GO on all 16

**What I checked** (mechanically, as for the 128):
- `proposed-pins.json`: 144 FP8 pins, and the 128 GO'd records are byte-identical.
- `DeviceSm120v2LoopEquiv.lean`'s eight statements.
- `TTOutChainOnly.lean` against the four props' earlier text in `DeviceChainOnly.lean`: identical.
- The eight new `Cast8` signatures, with the same parser as before.

| Pins | Verdict | Checked |
|---|---|---|
| The eight `…_sm120v2_loop` | **GO** | Each is `<form> CM (devSm120v2 Prices.sm120) sem ρ ↔ <form> CM (devSm120v2 Prices.sm120Loop) sem ρ`, for every ρ. They cover `TTOutPearlCDev`, the chain cap, the chain-only and the U-only forms, each unit and per tile. This is note 1's equivalence, so one grant of v2's TT_OUT covers both prices. The U-only pair goes through the four unpinned helpers, because rev1's later-promotion debit is `add·Σ 0` (equal, but not definitionally). v1 correctly has no such lemma |
| The eight `pearlC{Gamma,Sampled}Sm120v{1,2}LoopCast8…` | **GO** | Each is at `Prices.sm120Loop` only, with c = 8 − 8953/1000 = −953/1000, so the A-only forming is exactly 1.047. They take the rev1 protocol and ρ = 1/400 for v1, and ρ = 1/1,000 for v2, with the right unit or tile TT_OUT. γ for v2 is 0.36218% at 8192³ and 0.35604% at 16384³, which matches my hand value; v1 is 0.51105% and 0.50528% |
| `TTOutChainOnly` as an assumptions module | **GO** | The four props moved verbatim. `TTOutChainOnly` imports only `TTOut` and `DeviceChainOnly`, and `DeviceChainOnly` no longer imports `TTOut`. It is proposed under `assumptions`, with its own `layers` entry, as the bundle's other TT_OUT modules are |

**The upper-bound labels** are in the twins' docstrings, the README's 8.38 columns and `proposed-pins.json`'s `labels`
map. The 20 twins with an exact pin name it. Twelve have none: the chain cap per unit (its exact values 0.35980% and
0.35484% are in the README), and the U-only twins, whose exact values are the cap's and rev1's.
- That is fine as stated. If the chain cap per unit becomes a published row, it would want its own exact pin.
- `labels` is not an audit field, but the vendored `audit.py` carries unknown top-level keys through `dump` unchanged,
  so it won't break a merge. Keeping it out of `lean-audit.json` is cleaner, since the docstrings already carry the
  label.

**The condition is unchanged:** everything at `devSm120v1` and `devSm120v2` rests on rev2's record definitions.

**Labels:** none recorded.

## Condition 2: met (30 Sep 12:51Z)

rev2 is reviewed and GO, and its grant is labelled on
`art:cc8cf5fe874fe6d9799e6273aa0c70fe7a216ae5fe6cf06d12c61b9c98e12529` (see
`internal/pouw/cheap-binding/ttout-rev1-bundle-verdict.md`, "The rev2 grant"). Its records match what these twins build
on:
- `devAt`'s `flags` is `SkipP.unitFlagsAt p G`;
- `devSm120v2 pr := devAt sm120E4m3 0 pr`;
- `DeviceChainCap`/`DeviceChainCapGamma` are byte-identical to `device/`'s.

So the GO on the 144 FP8 twin records stands without condition.
- The SaltDead delta owed on rev2 leaves the record-generic twins alone, since they read no `saltDeadP`. The twins
  stated at `devSm120v1`/`v2` read `FormingP.saltDeadP` through `devAt`'s `saltDead` field. The delta moves those
  reads, as the CHANGELOG lists, and I'll re-read those twins with it.

**Labels:** the twins aren't labelled yet. They'll be labelled when merged, on request.

## Delta, 30 Sep ~13:55Z: FP8 chain-only at casts 32.06 and 16 (32 new; 176 FP8 records): GO

**What I checked.** `proposed-pins.json` at 13:43Z: 176 FP8 records. The 144 earlier ones are byte-identical, and
there are 32 new chain-only kernel instances: v1 rev1 and v2 at the cap 1/1,000; casts 32.06 and 16; 8.00 and 8.376;
per unit and per tile; 8192³ and 16384³.

I used the same parser as for the 80, and checked each instance for:
- the named record only (`devSm120v1` or `devSm120v2` at `Prices.sm120` or `Prices.sm120Loop`);
- `c = h − 8` at 8.00, or `h − 8953/1000` at 8.376, with h = 1603/50 or 16;
- the rev1 protocol at ρ = 1/400 for v1, and ρ = 1/1,000 for v2;
- the kernel tiles on the `Sampled` pins;
- the chain-only TT_OUT form (`TTOut{,Tile}PearlCDev{Rev1,}ChainOnly`).

All 32 pass, as 32 distinct combinations. I also recomputed every γ from the definitions: the chain-only credit less
ρ times the full credit, rev1's first-add removal for v1, and the kernel's `W_ref`. All 32 match.

**Labels:** none recorded.
