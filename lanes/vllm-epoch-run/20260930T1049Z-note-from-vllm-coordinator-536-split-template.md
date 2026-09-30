---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T10:49Z

**[#536](https://github.com/danielreuter/verity/pull/536)** (`3f195ad3`) lets the CPU `build` task run without a GPU (digests verified equal).
- **Merge it into your run branch now.** It conflicts textually with your `b27ab8a0` in the Program-cache key's device lookup. Keep #536's version, which doesn't read the device when the target is declared, unless yours does something #536's doesn't; if it does, tell me.
- **Then submit new cells with `config-run-split`**, once nebius-infra confirms the template, so each GPU is held only for the Commit.
- `ov.note` adds `#536` to the pre-merge prefix.
