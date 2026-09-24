---
id: r21-silicon/fp8-proof/20260922T1838Z-report-fp8-proof
campaign: r21-silicon
lane: fp8-proof
kind: report
status: closed
repo: verity-main@4bf0c4f
---

# fp8-proof: first B-Ligero proof of an exact FP8 (Ada E4M3) tensor-core dot product

Branch `lane/fp8-proof` (worktree `verity-main-wt/fp8-proof`), 5 commits on `main` 72e8c7a, head **4bf0c4f**, clean tree,
not pushed. Diff vs base: 11 files, +1,263/-14 (`backends/direct/ligero/fp8/*`, `protocol.py` +45/-14 hooks, `run.py` +8,
one registry line). Relation: `GemmCoordinate<1536>` over `sm89.mma.m16n8k32.e4m3` = 48 chained K=32 transitions,
c_0 = +0, the final FP32 accumulator word public. Oracle: `verity.ml.tc.silicon.tc_dot(ADA_E4M3_M16N8K32, ...)`
(imported; `packages/verity/**`, `tools/tc_probe/**` untouched). Pod: `vy-sp1` (RTX 4090 sm_89, torch 2.4.1+cu124,
`/workspace/venv312`, Python 3.12.14).

## What was built (`backends/direct/ligero/fp8/`, 1,183 lines + 40-line README)

* `relation.py` -- `FP8Params(Params)` duck-types the checker's `Params` so the BF16 gadget classes (`Product`,
  `GroupMax`, `AlignState/AlignProduct`, `SignedSum`, `LeadingBit`, `Normalise`, `StateOut`, `Pack`) are reused
  unchanged on the adder-side parameters: sig 4, operand exponent 4 bits, adder width 14, zero-exponent floor -139,
  groups (16,16), accumulator-side significand 14. New pieces: an **E4M3 decode** (8-bit words: sign, 4 exponent bits,
  3 fraction bits, subnormal selector; NaN codes 0x7F/0xFF rejected by a range/selector pair; no inf) and the
  **lossy accumulator rescale**: the incoming FP32 significand is decoded as 24 bit rows and the truncated 14-bit
  adder-side significand is an *affine expression* of the top rows (`Mt = sum_{i>=10} f_i 2^(i-10) + nz 2^13`), so
  it costs **no new gadget class**: 24 bit rows + 2 constraints (`acc.nz0/nz1`), 26 rows/unit. The dropped 10 bits
  are constrained only to be bits -- exactly the silicon semantics. Domain: finite operands and finite accumulators.
* `witness.py` -- torch hint generator (vectorised, device) + `oracle_words` (calls `silicon.tc_dot`).
* `chain.py` -- `FP8_HOOKS = RelationHooks(public_vectors_fp8, word "<u1", chain-end "<u4", tag "|rel=fp8-ada|v1")`,
  `FP8ChainRunner` around the unchanged `protocol.prove/verify`, `gate_vu_fp8` (on-device negatives), `bench_vu_fp8`
  (the BF16 `bench-result/v1` envelope: prove_wall/verify_wall/proof_bytes/depth/soundness_bits/rows_per_unit +
  `census.*`; `workload_fingerprint.relation/model/commit`). Public claim per VU = the final FP32 word packed as 22
  bits (the low 10 bits of an honest chain end are provably zero; `pack_public` rejects nonzero low bits) plus the
  operands digest, hashed into the transcript before any coin (PROTOCOL 12/13).
* `census.py` -- rows/unit by class and by gadget scope. `tool.py` (`BENCH_VU_FP8`, registered `bench_vu_fp8`).
  `run.py --relation fp8-ada {gate-vu,bench-vu}` (one dispatch block). `protocol.py` gained a `RelationHooks`
  dataclass; `BF16_HOOKS` is the default of `statement_digest/prove/verify`, so the BF16 path is byte-identical.
* Tests green: `PYTHONPATH=.:... uv run pytest backends/direct/ligero -q` -> 8 passed (6 fp8 + 2 pre-existing v2;
  the v2 toy test needs `.` on PYTHONPATH on `main` too); `tests/test_repository.py` (hygiene) 5 passed.

## Census, FP8 unit (K=32 step) vs BF16 unit (K=16 step)

| | FP8 Ada (this lane) | BF16 (`unit.py`) | ratio |
|---|---|---|---|
| rows/unit | **3,769** | 3,516 | 1.07 |
| bit rows | 2,474 | 2,401 | 1.03 |
| selector rows | 640 | 610 | 1.05 |
| hint rows | 161 | 92 | 1.75 |
| pin / product / inverse rows | 192 / 301 / 1 | (counted in the above) | |
| linear / quadratic constraints | 589 / 3,532 | 347 / 3,387 | 1.70 / 1.04 |
| units per VU (K=1536) | 48 | 96 | 0.5 |
| **rows per VU** | **180,912** | 337,536 | **0.536** |
| VUs per l=4096 proof (B_proof) | 85 | 42 | 2.0 |

Of the 3,769 rows: E4M3 decode of 64 words ~ 64 x (8 bits + subnormal/NaN selectors); 32 exact products (<= 8-bit);
alignment to the 14-bit adder relative to the group max; lossy rescale 26; two grouped sums; normalise/RN to FP32.

## Tests

* `fp8/relation_test.py` (CPU): **2,000 random finite cases accepted** against `silicon.tc_dot`; **52 wrong-claim
  mutations rejected** (accumulator bit flips, wrong truncation of the incoming accumulator, off-by-one rounding,
  swapped group order, NaN operand smuggled in, nonzero low bits in the public word); 60 witness-row mutations
  rejected; 2-VU chain prove+verify on CPU for non-ZK/interactive and ZK/fiat-shamir; `pack_public` rejection.
* On-device gate `r20260922-183111-3c01` (`gate-vu --batch 64 --vus 64 --row-negatives 60`, cuda): 64 honest VUs
  accepted (per-VU and batched, l=256); **negatives 91/91 rejected** = 22 claimed-word bit flips + 2 (+-1 ulp) +
  2 NaN operands + 1 operand flip + 4 chain mutations (broken link, c_0 != 0, kept accumulator bit, dropped
  (truncated) accumulator bit) + 60 witness-row mutations.

## Runs on vy-sp1 (commit 4bf0c4f; `research inspect <id>`; labels `proof_class`, `relation`, `candidate=B-Ligero`, `hardware=rtx4090 --by fp8-proof --ref <id>`)

| run | relation | B | ZK / mode | prover s (sum over proofs) | verifier s | proof MB | soundness log2 | depth | proofs x B_proof | ms/VU |
|---|---|---|---|---|---|---|---|---|---|---|
| (a) `r20260922-181917-0877` | fp8-ada-k1536 | 64 | none / interactive | 0.035 | 0.026 | 3.33 | -128.13 | 3 | 1 x 85 | 0.55 |
| (b) `r20260922-183241-a43e` | fp8-ada-k1536 | 1024 | none / interactive | 1.465 | 1.087 | 154.9 | -128.53 | 3 | 49 x 21 | 1.43 |
| (c) `r20260922-182131-1099` | fp8-ada-k1536 | 4096 | none / interactive | **1.643** | **1.189** | **169.9** | **-128.62** | 3 | 49 x 85 | **0.40** |
| (d) `r20260922-183412-7a35` | fp8-ada-k1536 | 4096 | **zk / fiat-shamir** | 2.055 | 1.465 | 263.9 | -128.40 (FS queries 2^60, t_pad 512) | 1 | 49 x 85 | 0.50 |
| control `r20260922-182930-bf16` | bf16-k1536 | 4096 | none / interactive | 2.420 | 2.203 | 321.6 | -128.29 | 3 | 98 x 42 | 0.59 |

Soundness: the existing accountant, union bound over the sub-batches (FP8 B=4096: per-proof -134.2 x 49). Verifier =
the Python verifier accepting every rep (`validation.status: passed`). (b) reuses the BF16 splitter, which kept 49
proofs and under-filled them (21 of 85 slots), hence its worse ms/VU. (d) is the existing HVZK masking layer applied
**unchanged** (`--zk --mode fiat-shamir`; ZK cost +25% prover, +55% bytes; privacy is vacuous while operands are
public, as for BF16). The first BF16 control launch (`r20260922-182300-bf16`) failed: the built operand arrays are
not committed; relaunched pointing at the pod's existing `vu-k1536` instances (same card, commit, session).

## FP8 / BF16 ratio vs the pre-registered expectation

Expectation: rows/unit near 3,516 and per-VU cost near BF16 ("not 2x cheaper"). Measured at B=4096, same card:
**rows/unit 1.07x (confirmed)**, but **per-VU prover 0.68x, verifier 0.54x, proof bytes 0.53x**. The unit covers
K=32, so a VU is 48 units instead of 96: an l=4096 proof holds 85 VUs instead of 42 and B=4096 is 49 proofs instead
of 98. Everything that scales with the proof count halves (encode 0.046 vs 0.086 s, Merkle 0.048 vs 0.094, openings
0.144 vs 0.308, tests 0.435 vs 0.871, verifier, bytes); what does not is the witness/hint generation (torch witness
0.655 vs 0.766 s, hints 0.29 vs 0.21 s -- rows x VUs is 0.54x but the FP8 hint path is untuned and has 1.75x the hint
rows), which is now 58% of the FP8 prover. So the "not 2x cheaper" half of the expectation held for the prover
(1.47x cheaper) and failed for verifier and proof size (1.9x cheaper).

## Unfinished / caveats

* Nothing on the deliverables list is missing; the low-hanging fruit is the FP8 hint generator (58% of the prover)
  and a splitter that fills proofs at B < 4096 (run (b)).
* `soundness_bits` is achieved log2 from the accountant with its `hash_placeholder: True` (SHAKE-256 expander), as
  for BF16.
* Pod time this lane: ~1.3 h of vy-sp1 (~$1), most of it venv setup and failed launches (Python 3.11 system
  interpreter, `$RESEARCH_RUN_DIR` expansion, an un-split `--env` shell variable: `r20260922-183400-gate`,
  `-184000-b1024`, `-184001-zk4096` never started -- ids are mine, not timestamps).
