---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# Joint skips a tensor-core prover can actually take: none, on units that pass the cap

30 Sep 2026, 07:35Z. Independent assessor (bc-d7d4b0d1). This is the evidence behind the ratings of `tt-out/pearl-c-sm120-unpromoted-cap1000`, the rev1 rows and `cross-group-knowledge/pearl-c`. Scripts: `fragment_joint_sm120.py` and `fragment_alignment_sm120.py`, CPU on node 2, with the census's s5 forming and bit-exact atoms (branch `cursor/pearl-c-sm120-attacks-cb92` at `5f1cb93e`).

**Why fragments.** The census counts joint skip sets per word. The unpromoted chain's are ≥ 14.7% at R = 64 (the Lean freezing census), and the greedy finds 6–24% on the families below.
- A prover saves W1 only by not issuing an `mma.sync m16n8k32`, one k32 slice of a 16 × 8 fragment, 128 words at once, priced by its full shape (4,096 units).
- Re-doing one word's atom on generic cores to patch around a skip costs at least about 500 units at the measured prices (`dp4a` 4.05 per MAC on about 2 limbs per side, plus the 26-bit alignment). So a (fragment, atom) pays only if at most about 5–7 of its words need that atom.
- The attack is therefore: a greedy joint set fragment-wide (atoms whose skip, together with the ones already taken, leaves all 128 words unchanged), its part beyond the debit, and the atoms that leave ≥ 123 of 128 words unchanged (patchable).

**Results** (per-tile debit as a share of rev1's credit, at the measured FADD):

| Where | Cells | Pass the cap | Per-word joint sets inside the cap | Fragment-wide undebited / patchable |
|---|---|---|---|---|
| sm_120, pure chain (v2, cap 1/1,000), k = 8,192 and 16,384 | 22 | 17 | up to 10.2% (R = 56, k = 8,192), 16.0% (pm1 R = 40, k = 16,384) | **0 / 0** |
| sm_120, G = 4 (v1, cap 1/400), k = 8,192 and 16,384 | 13 | 9 | up to 9.4% (R = 48), 13.7% (R = 32, k = 16,384) | **0 / 0** |
| H100 atom, G = 4 (cap 1/400) | 12 | 5 | up to 3.9% | **0 / 0** |

These come from `r20260930-071529-f334` (sm_120) and `r20260930-072316-a4cf` (H100). Aligned spikes span R = 24–64 around each cap, beside gaussian, outliers-first and spikes-first.

**The cap does what the table says** (Lean freezing census input):
- v2 at 1/1,000 rejects R = 64 at k = 8,192 (debit 0.120%; ±1 background 0.111%) and R ≥ 40 at k = 16,384 (0.110%).
- The families just inside are R = 56 at k = 8,192 (0.096%) and ±1 R = 40 at k = 16,384 (0.098%).

**Alignment, at the families just inside the caps** (`r20260930-072134-bf24`): every word of one fragment got its own greedy set.
- The most-shared atom is in at most 24 of the 128 words' sets, and the most-shared pair in at most 8.
- Skipping each of the 20 most-shared pairs fragment-wide leaves at most 3 of 128 words unchanged.
- So a pair- or set-level skip that the greedy missed can't come near the ~121 words it would need.
- The per-word sets are word-specific: each word carries its own A-row and B-row noise at δ = 1, and only the spike positions are shared.

**Positive control** (`r20260930-072724-9486`): on the H100 atom, where whole atoms do freeze, the same search finds 35–75% of atoms fragment-wide: 43% and 36% at G = 4, R = 300, and 73–75% on pure chains. All of them are debited (0% undebited, since they are lone skips). The tool finds realizable skips where they exist.

**What it rests on.** `w1-complete/sm120` must price `mma.sync` by its shape and generic-core arithmetic at the measured rates, as the H100 machine does. A per-word price for tensor-core work would bring the per-word sets back, and those exceed γ₀ by 20–60×.
