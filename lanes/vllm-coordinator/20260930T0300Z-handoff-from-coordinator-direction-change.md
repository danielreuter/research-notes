---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: vllm-coordinator
kind: handoff
from: coordinator
created: 2026-09-30T03:00Z
---

# coordinator -> vLLM coordinator (sampled proofs; cc verity-root, POUS): direction change, sampled proofs measured on its own

**The change (Daniel via root, 02:52Z).** PoUW, PoUS and sampled proofs are no longer combined; the combined pipeline was an
integration test. Each is now measured on its own and hillclimbed for efficiency and security. The plan is
`docs/protocol-measurement-plan.md`.

**For sampled proofs:**
- **The clean measurement:** the epoch row with only sampled proofs enabled: no PoUW circuit, no PoUS in `protocol_options`.
  Record the overhead ledger's per-stage split and the escape bits per class.
- **Baseline:** point root at the table you consider current (#101's row at $2.07, #57's epoch run, the overhead ledger).
- **First targets:** replay cost per bit (`p` and `k` per class, smaller replay units); commit-path serving overhead (#443 is
  in TVD2R); and record and upload time.
- **Stops:** extending `protocol_options` to admit other protocols beside sampled proofs. #367, POUS's, is paused.
- **Continues as is:** the sm_120 port, epoch rows, and the in-flight trains.

**One hygiene bug from tonight's trains:** a vLLM test compiles a C++ kernel into the source tree
(`integrations/vllm/verity_vllm/program/kernels/cpp/build/libfa2_model.so.*.tmp`). The repository guard caught the temp file and
failed TVC2R's Lean-suite step while every test passed. Please make that build write under `tmp_path` or a cache directory.
