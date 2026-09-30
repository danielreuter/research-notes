---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: assumption-sweeps
kind: handoff
from: coordinator (relaying root)
to: assumption-sweeps (bc-5be66fb3)
created: 2026-09-30T16:10Z
---

# "Cell" is now "vLLM deployment"

**Terminology (Daniel, via root 16:08Z):** what we've been calling a "cell" is a **vLLM deployment**. Use "vLLM deployment" in new notes, code, labels you choose and reports from now on. Existing identifiers (for example `vyv-cov-`, `row run`) stay as they are.

The dispatcher (`node1-dispatcher`) is also designing for two queues, GPU-only generation and CPU checking; the vLLM coordinator is splitting the work that way, with Daniel's approval.
