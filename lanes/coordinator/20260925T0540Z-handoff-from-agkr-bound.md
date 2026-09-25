---
lane: coordinator
kind: handoff
from: agkr-bound
created: 2026-09-25T05:40Z
---

# agkr-bound revised estimate

**Answer.** The committed version (x, W and y committed with the core scheme and the commitments bound in the A-GKR proof)
does **not** fit the remaining budget and FINAL.

- **Five rows:** about 11 more pod-hours and $16–18 more, against about $12.8 left of the $15 cap. The work would end
  after 12:00Z.
- **Minimum (A100 BF16 plus one FP8 row):** about $10–12, which is inside the cap. It would likely finish 11:30–13:30Z,
  so the 12:00Z FINAL is probably missed.

I am blocked on your decision (options at the end). My pod is being drained, so nothing is spending while I wait.

## What is done

**Public-input intermediate: complete, art:559147e1, not measured on the five rows per your 0507Z handoff.** The statement
is named `R+bound`:

- Its circuit files must be a pinned set of `R` (`pins.txt`).
- `x.bin`, `w.bin` and the public words must match the pin named `R+bound` in `verifier/src/instances.rs`.
- `--relation R` refuses a bound statement, and `--relation R+bound` refuses an unbound one.

Results on bf16-ampere, fp8-hopper and fp4-nvf4, all NEGATIVES OK:

- Rust accepts the honest proof.
- A wrong operand word with the honest y is rejected by Rust, by Python (linear functional mismatch) and by clear mode.
- The same altered witness without `bind.txt` is accepted under plain `R`. That acceptance is the gap the binding closes.
- An altered `x.bin` is rejected by the instance pin.
- `mutate`: 17/17 rejected.
- Soundness is 2^-130.19 as before; the binding batching term is ≤ 2^-161.6.

## Design sketch of the committed version

**Scheme.** `verity.commitments` `leaf/v2h`, schema `poseidon2-babybear-w24/row/v2h`:

- One Poseidon2-BabyBear-w24 digest per x row and per W column. Plonky3 parameters: width 24, rate 16, capacity 8,
  padding-free overwrite sponge, capacity initialized to `IV(role, word_bits, n_words)`.
- The digests are leaves of the SHA-256 indexed Merkle tree, giving roots R_x and R_W.
- y is committed under the `merkle` scheme, one word per leaf, as root R_y.
- These are the same roots B-Ligero's `--auth included-hash` statement publishes for the same frozen set, so both backends
  would name identical commitments.
- As in B-Ligero, y stays public and is checked against R_y outside the proof. If y must be private too, that is a
  further, larger step.

**Where the binding lives.** It mirrors `backends/direct/ligero/hashchain.py`:

- Each unit absorbs one sponge block per operand. The 16 rate lanes are a linear packing of the unit's committed operand
  columns: one BF16 word per lane (k = 16), two E4M3 bytes per lane (k = 32), or six NVFP4 nibbles over `x.p*` / `x.s*`
  (12 lanes).
- The 8 capacity lanes per operand chain unit to unit through `chain.txt` links, the way the accumulator does.
- At each VU's last unit the 8 digest lanes per operand are linked into the epilogue's public words (16 more words per VU).
- Both verifiers recompute the leaf hashes and the SHA-256 Merkle roots from those digests and compare them with R_x and
  R_W; R_y comes from the public y. The Rust side needs its own implementation of the leaf and node framing, tested against
  `verity.commitments` vectors.
- A pin per new relation, with new names (for example `bf16-ampere+commit`), keyed on relation and roots.
- New `pins.txt` lines, because the unit circuit changes.

**The obstacle.** Every A-GKR unit circuit is product-depth 1:

| circuit | product gates | committed columns |
|---|---|---|
| bf16-ampere | 26 | 264 |
| fp8-hopper | 37 | 448 |
| fp4-nvf4 | 215 | 485 |

All the nonlinearity goes through committed hint columns and LogUp. A Poseidon2 permutation has 213 x^7 S-boxes (8 full
rounds × 24 lanes, plus 21 partial rounds), and there are 2 permutations per unit. There are two ways in:

- **(i) Depth-1:** commit x², x⁴ and x⁷ per S-box. That is about +1280 columns per unit, roughly 5.8× the BF16 witness
  (264 → about 1540 columns).
- **(ii) Depth-3 GKR products:** commit only the S-box outputs, about +426 columns per unit (2.6× on BF16). This needs
  GKR depth > 1, which the fast CUDA prover has never proved. That is a correctness and perf unknown.

**Expected prover-cost delta.**

- BF16: 2–4× t.total, from 0.84 s to about 2–3.5 s on A100, against 0.897 s for B-Ligero with the in-proof hash.
- FP8 and NVFP4: 1.5–3×.
- The RTX 4090's 24 GB may force two sub-batches, with a union-bounded soundness.

**Soundness.** The statistical terms keep their form; the batching term gains the new constraints. The binding adds a
computational assumption: collision resistance of an 8-lane (248-bit) Poseidon2 digest, whose generic birthday bound is
2^-124, below the 2^-128 target. It needs naming, the same way B-Ligero's `LeafScheme.assumption` does. **This needs a
coordinator or user ruling on how it enters "2^-128 target and achieved".**

**Effort and pod-hours.**

- Implementation and debugging: 5–7 hours on a GPU pod. The work covers:
  - the gadget at circuit-text level, with a KAT against `KAT_24`;
  - the sponge-state witness, reusing `backends/direct/ligero/leaf/poseidon2.py` (`permute_torch` / `sponge_states`);
  - the chain and epilogue plumbing;
  - both verifiers, the pins and the negatives.
- Each measured row: about 1 hour including the pod bootstrap.
- Cost:

| item | estimate |
|---|---|
| A100 development, including the A100 BF16 row (about 6 h at about $1.5/h) | about $9 |
| one FP8 row (RTX 4090 about $1, or H100 about $3) | $1–3 |
| spent so far (A100 since 04:15Z) | about $2.2 |
| the other three rows | about $6 more, which exceeds the $15 cap |

## Options (your call)

- **(a)** Extend the lane: a new FINAL and budget (about $20 total), and pick the S-box route. I recommend (ii), with (i)
  as the fallback.
- **(b)** Keep today's scope to development: the gadget plus KAT, one A100 BF16 cell and its negatives. No Table 2 rows,
  within about $11.
- **(c)** Park the committed version. The lane closes with the integration (v2 handoff 0535Z) and the public-input
  intermediate art:559147e1.

My checkpoint is `blocked` on this handoff, and I poll my inbox about every 10 minutes.
