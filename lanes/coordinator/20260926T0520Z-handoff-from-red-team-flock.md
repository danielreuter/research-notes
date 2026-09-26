---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T05:20Z
---

# red-team-flock: all eight real-K Chunk(n) and wgmma cells meet PB1–PB4, CN1 and CN2, labelled NON_ZK_PROOF; the two wgmma cells have model-y tiers

**Cells:**
- bf16-ampere on the A100: art:149cdaf9 (K 2048) and art:673c1835 (K 8192).
- fp8-ada on the 4090: art:43986c5d (K 2048) and art:c0999f7f (K 8192, 2 proofs).
- fp8-hopper on the H100: art:c200eef3 (K 2048) and art:c4d03dd5 (K 8192, 2 proofs).
- bf16-hopper-wgmma on the H100: art:c767e092 (K 2048) and art:bbb95342 (K 8192, m 35).

**Conditions:**
- **PB1:** each record names the verifier commit and binary sha. The commits are 20082dcb, f0f88574 and e4f631bd. All
  three contain the NV1 admission (45fdab2d), and f0f88574 → 20082dcb has no `backends/flock` diff.
- **PB2:** each record reports the union bound: 2^-195.44, or 2^-194.44 for the 2-proof cells.
- **PB3:** my replay, run r20260926-050108-7fa6 (CPU, e4f631bd, binary 0463d83f), used each verifier pod's own
  instance files, whose roots replay recomputes natively.
  - All 60 recorded sessions were accepted.
  - All 20 negatives were rejected: the other session's proofs and swapped reps, for every sub-batch.
- **PB4:** every proved session has link_mode exchange, require_link true, and the cell's Σ. The verifier and prover
  hostnames differ in every cell.
- **CN1:** the NV1 admission is in every verifier binary.
- **CN2:** the largest proof is n × VUs = 30,720 (bbb95342, m 35). All others are at most 16,384.
- The unit netlists equal the granted pins: e97ecb9e, e66262a0, 904ca664 and 12c3c8d3.

**wgmma tiers:** in both wgmma cells, y is the `bf16-hopper-wgmma` model chain on the captured A100 #101 inputs. It is
not a captured H100 output.
- I recomputed both models over each file:
  - c767e092: all 4,096 y match the Hopper model. The recorded A100 set differs in exactly 1 word (VU 3591,
    0x3723 → 0x3724).
  - bbb95342: all 1,920 y match the Hopper model. The recorded set differs in 3 words (VUs 1229, 1352 and 1918).
  - Both counts match the headers' `differ_from_set`.
- The tier suffix `:y=bf16-hopper-wgmma` is right: it keeps these y roots out of the captured tier.
- **Fix:** `instances.source = "captured"` is true only of x and W. Registration should say captured inputs and model y.
  The label stands, but these cells must not be cited as proving the captured set's y, or as H100 silicon output.

**Labels:** on all eight cells, proof_class=NON_ZK_PROOF, verified=accepted, verifier, and a `finding`. The findings on
the two wgmma cells spell out the model-y caveat.

The CPU pod (cpu3c-16) is terminated, about $0.10.
