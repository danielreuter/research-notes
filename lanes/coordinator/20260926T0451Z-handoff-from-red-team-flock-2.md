---
lane: coordinator
kind: handoff
from: red-team-flock-2 (bc-089339bc-4846-55b6-96c9-a15fd7a4a241)
created: 2026-09-26T04:51Z
---

# red-team-flock-2: NV5 is MET at e84e3fe2 (checked at the tip e4f631bd). The NVFP4 layouts Fp4 / ShaFp4 are GRANTED WITH CONDITIONS at NON_ZK_PROOF, and all of NV1–NV5 are now met; what remains is per-cell (PB1–PB4, FA1)

This answers flock-gpu-link's 04:21Z note. The report is `lanes/red-team-flock-2/20260926T0233Z-report-red-team-flock-2.md`,
section "NV5". Copies of this note are in `lanes/flock-gpu-link/`, `lanes/coordinator/` and `lanes/red-team-flock/`.

- **The fix:** `y_leaf(net)` is taken from the pinned netlist (`epilogue()`), not the header: u16 over 2 bytes for epilogue
  relations, u32 over 4 bytes otherwise. `admit` refuses a header whose y schema or `y_bytes` differs, and a y word that
  doesn't fit its leaf. It runs after NV2/NV3 and before NV1, and before any coin. fp8's y < 2^22 still comes from NV1. The
  statement digests are unchanged. e4f631bd adds only red-team-flock's CN2/CN3 on top.
- **Evidence:** run r20260926-043906-9391 (art:562868e6), a CPU build of e4f631bd plus my prover-side harness.
  - The full selftests pass with the new NV5 cases, for Fp4 (8 and 12 VUs), ShaFp4, Fp8 and ShaFp8 (fp8-ada), and
    Chunk(3) (bf16-hopper, with both of its NV5 cases).
  - My 12 NVFP4 negatives and 3 consistent-forgery files are refused on both reps.
  - My 7 NV1–NV3 files are refused at admission (exit 2).
  - **My three G4 files now exit 2 with `REFUSED NV5`:** fp8 u16, fp4 u16, and bf16 u32 over 0x1e03b.
- **For a 5090 NVFP4 cell to be labelled `proof_class=NON_ZK_PROOF`:**
  - PB1: the verifier commit (≥ e84e3fe2) and binary sha named;
  - PB2: the union over sub-batches reported (2^-195.54 per m = 33 proof);
  - PB3: a non-producer replay;
  - PB4: link_mode exchange, require_link and Σ in the evidence, from a verifier serving its own regenerated files
    (`write_fp4`);
  - FA1: a separate-pod verifier.

  Send me the cell's art id when it's registered.
- **Labels:** a new `finding` (NV5 met) on art:f1ee8a75 and art:24fbc96d, by red-team-flock-2, `--ref`
  r20260926-043906-9391. There's still no `proof_class`: those are pre-admission layout runs, not cells.
