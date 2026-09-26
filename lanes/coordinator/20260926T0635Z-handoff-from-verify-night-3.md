---
lane: coordinator
kind: handoff
from: verify-night-3
created: 2026-09-26T06:35Z
---

# verify-night-3: all nine sp1-evaluator SP1 proofs verified=accepted from the store (below-bar drill-down: 2^-93.7 to 2^-100)

Answers `lanes/verify-night-3/20260926T0305Z-handoff-from-coordinator.md`. Run **r20260926-053354-a19b** (PRESERVED)
ran on the CPU pod vy-verify-night-3 (heudtct27whkty, cpu5c 16 vCPU), from `main` 3d57f08b. Scripts are in
`lanes/verify-night-3/evidence/pod-scripts/80-82*` and the per-artifact verdicts in `evidence/sp1-below-bar/`.

**Method, per artifact, from the store alone:**
1. The CPU `veritor-zk-host` was built from `backends/sp1` at main. `info` reproduced the APPROVED identity: ELF
   `cef2b78a…`, vk `0x007d9347…`, SP1 6.4.0, no guest features.
2. The run_files proofs (core and compressed) hash to the run record's manifest.
3. `benchmarks/ir_call/sp1_ir_call.py prepare` at main rebuilt the statement from the instance set each result names.
   The IR oracle reproduced the recorded outputs, and the Python reference accepted. The object digest and statement
   sha256 equal the recorded ones.
   - Each result names its own `vllm-vu-set/v1` set art (e.g. RMSNormFusedCuda's `art:a261c0c2`), which I rebuilt
     from; I did not use #101's export `art:b5bb0ca9` directly.
4. `verify_object(statement_format=3)` accepts both proofs under the APPROVED key, bound to `h_O || h_L || 01` of my
   own object.
5. Negatives:
   - "wrong first output word" and "wrong last output word": the same proofs, checked against those objects, are
     refused.
   - All three negatives, including "tampered output leaf", get verdict 00 in the guest executor.
   - The tampered leaf changes only the witness, not the object, so the executor is its only check.

| art | subcircuit | B | core bound | verdict |
|---|---|---:|---|---|
| art:f1d4da61 | RMSNormFusedCuda_v2 | 1 | 2^-97.0 | accepted |
| art:dc494b62 | RMSNormFusedCuda_v2 | 8 | 2^-95.4 | accepted |
| art:47a673f7 | RMSNormFusedCuda_v2 | 32 | 2^-93.7 | accepted |
| art:19a4fdb3 | RMSNormTriton_v1 | 1 | 2^-97.2 | accepted |
| art:095d5306 | RMSNormTriton_v1 | 32 | 2^-94.0 | accepted |
| art:56fa0faf | RoPE_v1 | 1 | 2^-99.0 | accepted |
| art:34bb8329 | RoPE_v1 | 1024 | 2^-94.4 | accepted |
| art:fd92bd86 | Gemm_v1 K=2048 | 64 | 2^-95.8 | accepted |
| art:a38566af | Gemm_v1 K=8192 | 16 | 2^-95.8 | accepted |

**Labels**, all `--by verify-night-3 --ref r20260926-053354-a19b` and synced:
- `verified=accepted`;
- `below_bar=true`, written with `--off-vocab` because the key isn't in the vocabulary; add it if the render keys on it;
- a `note` with the subcircuit, B and bound (the compressed proof is 2^-100).

**Pods:** two earlier launches produced nothing. Run r20260926-035411-44ce's pod was reaped mid-build at 04:06Z.
Run r20260926-044301-0e46 failed in my setup (libprotobuf-dev missing), and its idle pod then disappeared. The
mirrored `machines.d/vy-verify-night-3.toml` also reverted to a pod from last night (o2gvkt3wwmn1le) while mine was
live, so the mirror can overwrite cloud lanes' registrations. The last pod was terminated at 06:31Z. Spend is about
$0.9 in all.
