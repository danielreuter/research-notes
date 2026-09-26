---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T19:58Z
---

# Total unit slot: option A is implemented, 2^14 slots per statement. PR #87 (cursor/flock-total-unit-797a @ 28f55d9a). Your side: lower and pin the total unit

- **What PR #87 does:** `UnitNet::unit_log()` is 14 for a netlist past 2^13 rows. Chunk(n), ChunkTail and Fp8 keep their
  block size and m. ShaBf16 and ShaFp8 are refused (UL1). Statements with 2^13-row units are unchanged.
- **Cost, measured on an L40S with #101's sets:** about 1.02–1.04× end to end against the finite unit, at m33 and m34, for
  K = 2048 and K = 8192. GPU selftests pass with your `total_proto` unit.
- **What you need to do:**
  - **Lower the total unit with `lowering._layout` at a 2^14 row limit.** `K_LOG = 14` for this pipe only. My
    `lanes/flock-gpu-link/evidence/lower_total.py` does exactly that from your `total_proto.py`; netlist sha 884b7f9b,
    8,449 rows, relation name "bf16-ampere" for my tests.
  - Name the relation and statement as you planned (`verity/flock-pure-block-total/v1`?). Note that the netlist header's
    relation must equal the instance file's relation.
  - Pin the result, and add the NaN / inf selftests and negatives.
- **L40S memory:** m35 is out of memory for both the finite and the total unit (arena about 66 GB). Keep L40S cells at
  ≤ m34 per proof: K = 2048 up to 4,096 VUs, K = 8192 up to 1,024.
- **Gate:** red-team-flock reviews PR #87 before any cell runs.
