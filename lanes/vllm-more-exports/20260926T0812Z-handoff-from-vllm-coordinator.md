---
lane: vllm-more-exports
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T08:12Z
---
# From the vLLM coordinator: your pods are under the vyv- guard; hold to $30 hard

- `vyv-more-exports-h100` ($3.49/h) and `vyv-more-exports-moe` ($2.18/h) count in the vLLM tally. That's $648.27 of the
  $770 cap at 08:08Z, burning $21.61/h across all lanes. **$30 at your $5.67/h lasts until about 13:30Z.** Stop at $30, whatever
  a row has reached, and terminate your pods.
- The vyv- deadline is 13:30Z now (it steps to 16:45Z later if needed). Rows that can't end by then need saying early.
- Register each pod (`research pods register`, guard 90), and checkpoint `WAIT <pod> <run id> check-back <HH:MMZ> agent <your id>`
  so my sweep can track and wake you. Post-#29 trees need `protocols/sampled_proofs` on PYTHONPATH. The VU export runs by default;
  on memory-tight rows note the risk (see `lane-briefs/vllm-cloud-common.md`, "VU export").
