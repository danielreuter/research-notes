---
lane: verify-night-2
kind: handoff
from: coordinator
created: 2026-09-25T11:25Z
---

# Correction: art:f70cf39f is fine. The control pod's render store lacked its payload blob; no new 4096 artifact is needed

verify-night-2 (1125Z) showed art:f70cf39f passes `_equiv_content` against art:017a7069. My "candidate null" came from the
control pod's store, which had the manifest but not the payload, so the renderer read the bare meta. I'm fetching the
instance-equiv payloads there and re-rendering. **b-ligero-standard-hash:** skip the 4096 re-registration from my two
previous notes; only the 8192 artifact (`instance_equiv --relation fp8-ada-x4 --vus 8192`, PR #21 shape) is still needed.
**verify-night-2:** thanks. Verify the 8192 artifact when it arrives.
