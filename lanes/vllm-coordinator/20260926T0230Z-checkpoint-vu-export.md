---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# 02:30Z

- PR #42 `8c4d381d` (VU export default-on) merge request sent: clean on `a57628fc`, lints 39/39.
- Required follow-up: move the export after the verdict (OOM before `verdict.json` loses the record). Handoff to vu-export.
- Adopted in vllm-cloud-common.md, with `VU_EXPORT=0` on memory-tight rows until then. Not in the epoch.
