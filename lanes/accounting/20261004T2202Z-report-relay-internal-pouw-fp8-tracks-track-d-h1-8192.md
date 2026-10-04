---
id: 20261004T2202Z-report-relay-internal-pouw-fp8-tracks-track-d-h1-8192
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/internal/pouw-fp8/tracks/track-d-h1-8192.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/pouw-fp8/tracks/track-d-h1-8192.md`, sha256 `d4c0c2515376e103bb3e95d4d853fede413228c34e819fbaf428f0f95f3a45fb`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Track D: H-1 forming cuts for 8192 and 4096

28 Sep 2026. CPU-only design/accounting over H-1's adopted registration
check, two-block chain and hybrid floor. Input is X_q; Y16 is not assumed.

**Frontier reporting rule (Daniel):** every future H-1C4 table has rows
`2048, 4096, 8192, 16384, 32768` in that order. Reprice and test one size at
a time; every untouched row says `not run`. Do not report 65536.

## Compiled H-1TSM verdict: NO-GO

Two complete ptxas 12.9 kernels are in `internal/pouw-fp8/prototype/`:

- `track_d_h1tsm_sass.py`: one thread forms a whole slice;
- `track_d_h1tsm_warp_sass.py`: one warp forms a slice, with warp REDUX for
  the max and bank-replicated shared lookups.

The optimized warp kernel contains the complete online path requested:
preload, barrier, X_q/salt loads, raw-code slice max, floor slot, real/tag
addresses, LDS, sign choice, x1/x2 deinterleave and block-major stores.

~~~text
ptxas 12.9.86, sm_90a
dynamic shared memory requested  169,472 bytes
registers                         20
spills                            0
barriers                          1
~~~

Static 169 KiB shared memory is rejected by ptxas's 48 KiB static limit, so
the kernel uses opt-in dynamic shared memory.

### Why it misses

The relevant compiled loop contains, per real lane:

- code magnitude `LOP3` and warp `REDUX.MAX`;
- exponent/floor extraction and broadcast;
- salt/sign extraction;
- two table-address `IMAD` forms;
- data-dependent `LDS`;
- sign-half selection;
- high-byte extraction and two byte stores.

At Round-10 prices, a strict lower bound already exceeds the target:

| Unavoidable online work | Lower-bound units/real element |
|---|---:|
| code magnitude LOP3 | 64 |
| exponent/floor lane writers, amortized lane-0 work included | ≥96 |
| sign extraction + selected-half extraction | ≥96 |
| two data-dependent address writers | ≥64 |
| LDS result writer | ≥32 |
| x2 byte extraction | ≥32 |
| **lower bound before REDUX, tags, control and preload setup** | **≥384** |

The 8192 H-1T budget is 209.697. At `f_A=384`,
γ(8192³)=**1.472%**. Even granting an unproved 32-unit credit for every
formed pair gives 1.385%, so checked forming does not rescue it.

The shared path is also strictly more expensive than H-1T's compiled
`f_A=297.6`; it should not replace H-1T at 16384.

| Frontier | Compiled H-1TSM accounting |
|---:|---|
| 2048 | not run |
| 4096 | not run |
| **8192** | **γ ≥ 1.472% (NO-GO)** |
| 16384 | not run |
| 32768 | not run |

### Occupancy and deployment cost

The table plus per-warp scratch uses 169,472 bytes, leaving about 58 KiB of
the H100 per-CTA shared-memory allowance for staging/barriers and forcing one
CTA per SM.

- At the maximum 1,024-thread CTA, occupancy is capped at 32 warps/SM, 50%
  of H100's 64-warp limit.
- H-1T's 40-register, no-shared forming kernel can admit about 48–51
  warps/SM (75–80%, launch-shape dependent).
- Thus H-1TSM cuts the occupancy ceiling by roughly one third even before
  measuring LDS latency.
- With a 256-thread CTA it would expose only 8 warps/SM (12.5%), so a large
  CTA is mandatory.
- Every CTA also copies ~165 KiB and executes one barrier. The copy is an
  oblivious W1-free move, but is real wall time.

### Can it be repaired?

Not by changing constant to shared memory. Shared replication removes bank
conflicts, but scalarization, floor computation, address generation and
deinterleave remain.

Two local optimizations—putting sign in the LDS address and using a small
uniform floor lookup—might save 32–64 units. They do not rescue the route:
`f_A=320` gives γ=1.299%, and 288 gives 1.213%. Reaching budget requires
removing at least 175 units.

The kernel also consumes a prepared byte-per-lane salt array, whereas pinned
H-1T reads bits from 18 raw XOF words, and it assumes X_q is already padded
to 29+3 lanes. Direct raw-word extraction/padding would add work; they are
omissions in the candidate's favour.

The only conceptually different implementation direction is a branchless
packed integer/SWAR realization of the pinned H-1T map with no table lookup.
To clear 8192 it must compile below 209.697 units/real element including
slice max, raw-XOF extraction and both block-major outputs. No such sequence
is known.

Because the complete path is over budget, no H-1TSM row should be added to
Round 11. The scripts/results are CPU compilation evidence only.

## H-1TSM: H-1T with a bank-replicated shared-memory map

Status: **FIX / coherent conditional architecture, but no accepted 8192
price before SASS.**
H-1T pins the activation repair and changes each physical k32 slice to 29
real lanes plus three tag lanes. Its compiled baseline is `f_A=297.6`, credit
is `4T-3`, and its quality/security evidence belongs to one exact map.

### Exact map

For each real lane, H-1T needs only the clean E4M3 code, one of five floor
slots and one salt sign:

~~~text
T_real[256 codes, 5 floors, 2 signs] -> u16(x1,x2)
size = 256 * 5 * 2 * 2 = 5,120 bytes.
~~~

The three tag lanes use `(floor, sign, m in 0..7)`:

~~~text
T_tag[5 floors, 16 salt values] -> u16(x1,x2)
size = 160 bytes.
~~~

Both tables are generated exhaustively from the pinned `h1t_ref`, including
headroom, signed zero, subnormals, saturation and the H-1T tag values. Thus
the formed bytes, block-major order, registration statement,
`DistinctLiveH1T` target and measured quality are unchanged. No forming
credit is claimed.

### Shared-memory layout and cost

Constant memory is unsafe under divergent code indices. Instead, preload an
oblivious public table into shared memory and replicate/swizzle it by warp
bank:

~~~text
32 * 5,120-byte real table = 163,840 bytes
32 *   160-byte tag table  =   5,120 bytes
total per CTA              = 168,960 bytes (~165 KiB).
~~~

This fits H100's per-CTA shared-memory limit but permits only one such CTA per
SM and leaves only about 58 KiB for WGMMA operand staging, pipeline buffers
and barriers. The preload is an oblivious whole-word move, free in W1 only
for a pre-swizzled whole-word image; setup remains a wall-time/occupancy cost
to measure.

Conservative online forming:

| Work | Units/real element |
|---|---:|
| packed raw-code slice max / floor slot | 32 |
| XOF sign extraction | 32 |
| 32-bit shared-table index | 32 |
| bank-clean shared load result | 32 |
| block-major x1/x2 deinterleave/pack | 32 |
| three tag-lane lookups amortized over 29 real lanes | ≤16 |
| **f_A** | **≤176** |

The 8192 forming budget is 209.697 under H-1T's `4T-3` credit. Therefore one
additional 32-unit writer is tolerable (`f_A=208`); two are not.

The strike accepts the bank-replicated layout but adds two pre-SASS writers:

~~~text
claimed path                         176
raw X_q scalarization/address step  +32
second bank-address/index writer    +32
conservative f_A                    240
~~~

At `f_A=240`, γ(8192³)=1.08235%; the first 64-aligned passing cube is
9152³. Thus the complete compiled path must be **≤208** to clear 8192, with
only 1.697 forming units of slack.

### Frontier table

Per Daniel's rule, this pass prices/tests only 8192:

| Frontier | Result |
|---:|---|
| 2048 | not run |
| 4096 | not run |
| **8192** | **conditional: 0.908% at f_A=176; 0.995% at 208; conservative 240 gives 1.082%** |
| 16384 | not run |
| 32768 | not run |

Formula, with `T=ceil(k/29)`, FADD=32.00 and ε=1/400:

~~~text
gamma = 1 - (399/400) * 32(4T-3)
                    / (64T + 32(2T-1) + f_A*k/n).
~~~

### Required gates

1. CPU-exhaustive equality of both tables with pinned `h1t_ref`.
2. ptxas 12.9 SASS for preload, packed index, bank-swizzled LDS and
   deinterleave; no hidden 64-bit global address.
3. A bank-conflict proof for every legal code/floor/sign pattern.
4. W1 ruling that the oblivious preload is free and each online writer above
   is charged once.
5. Full-kernel CPU/GPU throughput later: one-CTA occupancy must not violate
   deployment limits, though it does not change additive-W1 γ.
6. Strike confirmation that byte-identical operands transfer H-1T's
   registration, `DistinctLiveH1T`, `4T-3` credit and quality.
7. Account or eliminate the two extra address/scalarization writers so the
   complete path is ≤208.

No weight copy and no weight-sized table are introduced.

### Paste-ready interface/log entry

**Track D, H-1TSM:** exact H-1T code-space forming through a
bank-replicated shared-memory table. The complete ptxas 12.9 path uses
169,472 dynamic shared bytes, 20 registers, no spills and one barrier, but
its unavoidable online writer floor is at least 384 units/real element,
against the 209.697 budget. γ(8192³) is at least 1.472%; even an unaccepted
32-unit forming-pair credit leaves 1.385%. The table forces one CTA/SM and at
most 32 warps (50% occupancy), versus H-1T's roughly 48–51 possible warps.
Verdict: **NO-GO; do not add a Round-11 row.** Exact scripts/results:
`prototype/track_d_h1tsm_{sass,warp_sass}.py` and their JSON payloads.

## Verdict: H-1C is NO-GO at 8192 as currently implementable

The arithmetic table idea is useful, but the strike rejects its 64/96-unit
price. A conventional lowering is a global/L2 lookup, not one abstract
32-bit writer:

| Required work | H100 units/element |
|---|---:|
| slice max | 32 |
| 64-bit address (`IMAD.WIDE`, two registers) | 126.4 |
| lookup result | 32 |
| deinterleave `(x1,x2)` into block-major words | 32 |
| **optimistic total before key extraction** | **222.4** |
| one scalar key/index writer | +64 |
| **conservative total** | **286.4** |

The resulting γ is:

| f_A | γ 4096³ | γ 8192³ | γ 16384³ | first 64-aligned square |
|---:|---:|---:|---:|---:|
| 222.4 | 1.755% | 1.092% | **0.758%** | 9536 |
| 286.4 | 2.132% | 1.284% | **0.854%** | 12288 |

So H-1C does not deliver the requested 8192 cell. A specialized compiled
path would have to prove total forming below 191.658; even f_A=160 leaves
only 31.7 units for every omitted address/pack operation.

Independently, H-1 remains NO-GO until Track H pins and validates the F19-2
activation repair. Existing quality and `DistinctLiveH1` do not transfer
before that.

## H-1C4: compact four-bit repair table (NO-GO pending compiled path)

Track H reports that a lane-local F19-2 repair with at most four salt bits is
plausible:

- every finite E4M3 code has at least 19 exact `(x1,x2)` decompositions;
- the exact F19-2 `x=4` witness has 14 splits that distinguish both blocks
  over tested signs and separations, enough to populate 16 selector slots
  with duplicates;
- no current evidence requires a fifth bit.

Pin a scheme-wide table:

~~~text
T[256 code slots, 5 floor slots, 16 salt nibbles] -> u16(x1,x2)
size = 256 * 5 * 16 * 2 = 40,960 bytes.
~~~

It fits H100 constant memory. A conservative complete path is:

| Work | Units/element |
|---|---:|
| slice max/floor slot | 32 |
| XOF nibble extraction | 32 |
| packed table index | 32 |
| constant lookup result | 32 |
| block-major deinterleave | 32 |
| **f_A** | **160** |

At k=4096:

| Shape | γ |
|---:|---:|
| 4096³ | 1.384% |
| **8192³** | **0.905%** |
| 16384³ | 0.662% |

This is the best arithmetic 8192 shot, but the strike finds that it is not a
conservative price:

- 40,960 bytes fits the 64 KiB constant address space, but exceeds the
  per-SM constant-cache working set;
- independent nibbles cause about 14 distinct warp addresses even when code
  and floor match, and adversarial codes can cause 32; constant memory
  serializes those addresses;
- five floor slots need dynamic indexing (or padding to eight, consuming the
  full 64 KiB);
- scalar index formation, deinterleave and raw-code slice max still lack a
  compiled count.

One extra 32-unit writer/replay allowance is enough to lose 8192:

| f_A | γ 4096³ | γ 8192³ | first 64-aligned square |
|---:|---:|---:|---:|
| 160 claimed envelope | 1.384% | **0.905%** | 6848 |
| 192 (+1 writer) | 1.575% | 1.001% | 8256 |
| 224 (+2 writers) | 1.764% | 1.097% | 9600 |

The 8192 budget is only 191.658. Therefore H-1C4 is **NO-GO currently** and
becomes FIX only after a compiled kernel proves the complete worst-case path
below budget.

Required:

1. pin one F19-2/F19-3 local map with at most four bits;
2. exhaustively check every registered P0–P4 adversarial class, not only the
   known witness;
3. exclude collisions on every admissible nibble subset needed by lifting;
4. rerun +20% quality—the robust x=0 splits tested so far can be as large as
   ±160;
5. compile the constant-memory path and validate its SASS, divergent lookup
   throughput and full 160-unit W1 count.

Constant-memory fit alone does not prove the one-load price. If universal
local search fails, the likely next requirement is cross-lane residue state
or a stronger registration class, which invalidates this accounting.

## Proposed optimization: direct code-space forming

H-1's mathematical map is already a finite map on E4M3 codes:

~~~text
F    = max(slice floor, row floor)              power of two
mu   = max(step(x), F)                          power of two
x1   = RNE_satfinite(x + sign * mu)             E4M3
x2   = -sign * mu                               E4M3
~~~

Do not unpack X_q to f16 and reconstruct those operations arithmetically.
Use a fixed table:

~~~text
T[x_code, floor_exponent, raw_xof_byte] -> packed_u16(x1_code, x2_code)
~~~

Using the raw byte directly is important after Phase 19: it avoids the
standalone LOP3 that F19-1 prices at 32/element. The table has at most
`254*16*256` two-byte entries (about 2 MiB). The slice max still determines
`floor_exponent`; local `step(x)`, the max with F, salt direction and F19-3's
`mu=2F` boundary case are inside the table. Every entry can be generated and
exhaustively checked against the one pinned H-1 map before deployment.

This is not a changed law:

- x1 and x2 are byte-identical to H-1;
- the registration class P0–P4, hybrid floor and headroom are unchanged;
- `DistinctLiveH1` is unchanged;
- quality is exactly H-1's measured quality;
- no checked-forming credit is claimed.

## Phase-19 / Round-9 arithmetic envelope

F19-1 reprices H-1's current X_q hybrid schedule at **318.5**, not 239: the
f16→E4M3 cast is 64/code and the standalone LOP3 is 32.

H-1C replaces everything except the slice max:

| H-1C work | Conservative W1 units |
|---|---:|
| slice-max/floor exponent | 32 |
| one raw-byte-indexed data-dependent pair result | 32 |
| **f_A** | **64** |

The 32-unit lookup charge in this optimistic envelope was intended to
include address dependence and the word it writes. The strike shows that
ordinary lowering cannot use that reading; the actual conservative rows are
222.4/286.4 above.

H-1's exact two-block formula is:

~~~text
T = k/32
credit = 32 * (4T - 1)
W_ref = 32 * 2T + 32.11 * (2T - 1) + f_A * k/n
gamma = 1 - (399/400) * credit/W_ref.
~~~

At the worst allowed `k=4096`:

| f_A | Interpretation | γ 4096³ | γ 8192³ | γ 16384³ |
|---:|---|---:|---:|---:|
| 318.5 | Phase-19 current hybrid | 2.320% | 1.380% | **0.903%** |
| 96 | lookup plus separate address writer | 1.001% | **0.712%** | 0.567% |
| **64** | one W1 data-dependent word | **0.808%** | **0.615%** | 0.518% |

The exact forming budgets are 95.829 at 4096³ and 191.658 at 8192³.
Therefore:

- **8192³ would clear under either optimistic lookup pricing**;
- **4096³ would clear only if the complete table operation is at most about
  95.8 units/element**. The one-word reading has 31.8 units of margin; the
  separate-address reading misses by 0.17 unit.

These are counterfactual thresholds for a future specialized
constant/register implementation, not current candidate claims.

No weight forming or reuse term appears: registered B′ enters as offline
E4M3 codes.

## Why the table does not reopen the D-5 distinctness failure

The table output is not added as a newly credited target. It is merely an
implementation of the same H-1 x1/x2 operands. H-1's checked values remain
the atom and running words, and its `DistinctLiveH1` statement is unchanged.

In particular:

- no packed code word earns lower-bound credit;
- duplicates inside table outputs are irrelevant to accounting;
- the verifier's registration check and the hybrid-floor proof obligations
  are unchanged;
- the table is public deterministic code, not prover-chosen advice.

This avoids the exact mistake in D-5, where unproved packed-word
distinctness was used as credit.

## Other cuts

### Block rewrites

H-1 has only the exact split `x=x1+x2`; it has no three-noise block analogous
to D-3's block 3. Reassociating the FP32 running reduction either saves and
loses the same checked word or reopens absorption. No sound −18/side rewrite
exists here.

### Check packed forming words

Not used by either table proposal. Checking pair outputs cannot rescue the
conservative global lookup or make H-1C4 robust: `distinctWritesPacked` would first need the same
pairwise-distinct/nonfree proof that D-5 failed, and at zero input x1/x2 have
structured sign relations. Do not use this credit.

### Branchless integer/SWAR map

A closed-form packed map could replace the lookup. To beat H-1C it must
implement saturation, the zero/subnormal cases, local-cell width, floor max,
salt direction, rounded x1 and exact x2 in no more than one or two 32-bit
writers per four codes. This is a kernel optimization, not needed for 8192;
for 4096 it is an alternative way to establish the <=95.8 bound.

## Required gates

1. **F19-2 activation repair first:** H-1 is NO-GO until Track H pins that
   map. H-1C then tabulates the repaired map; it does not solve F19-2.
2. **Exact table generation:** exhaustive equality with the one pinned map
   over every finite E4M3 code, floor exponent and raw byte, including
   F19-3.
3. **W1 ruling:** whether one table lookup returning `(x1,x2)` costs one
   32-bit data-dependent word (32) or also an address writer (64 total).
4. **CPU SASS/compiler check:** the intended table path must not insert
   hidden per-code unpack, bounds or pack writers.
5. **Red-team confirmation:** table implementation leaves the repaired H-1
   map's
   `DistinctLiveH1`, registration and hybrid-floor statement unchanged.

Track H reports that current F19-2 repair directions can remain lane-local
with exactly `(x_code,floor_exp,raw_byte)`; the caller keeps the existing
domain-separated unit/row/lane XOF coordinate. If the final repair needs a
cross-lane permutation, add `lane_in_k32` and reprice—the 64/96 claim does
not automatically survive.

The old quality measurements do not transfer across F19-2. Track H must
rerun quality after pinning the repair. Once that repaired map passes, exact
table equality makes H-1C quality-identical and needs no separate run.

## Paste-ready interface post

**H-1C verdict:** the full-byte/global-table form is NO-GO at 8192
(222–286 units, γ=1.09–1.28%). **H-1C4 is also NO-GO currently.** Conditional on
Track H's F19-2 repair, a public exact table can replace unpack/f16/casts
without changing H-1's law. A four-bit repair gives a 40,960-byte
constant-memory table and an instruction-envelope `f_A=160`, hence
γ=0.905% at 8192³. But one extra writer makes `f_A=192` and γ=1.001%, while
worst-case divergent constant loads can replay 14–32 times. It needs the
pinned universal F19-2/F19-3 map, repaired `DistinctLiveH1`, exhaustive
nibble-collision checking, a quality rerun and a compiled worst-case path
below 191.658. No forming-word credit is used, so D-5's distinctness failure
is irrelevant.
