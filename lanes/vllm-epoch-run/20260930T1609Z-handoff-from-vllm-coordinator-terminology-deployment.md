---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: handoff (terminology, Daniel 16:05Z) · from: vllm-coordinator · created: 2026-09-30T16:09Z

**From now on, a "cell" is called a vLLM deployment:** one model × serving config × hardware target, run through Build and Commit.
- Use "deployment" in PR titles and bodies, docs, notes and handoffs.
- **Labels:** keep the dashboard's keys (`ov.ws coverage`, `ov.config <row slug>`, `ov.gate`); only the prose changes. Write "deployment" in `ov.note` text.
- **Not renamed:** existing identifiers, row slugs and file names. Don't rename code for this.
