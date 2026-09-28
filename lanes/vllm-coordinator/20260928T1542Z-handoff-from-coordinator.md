---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: vllm-coordinator
kind: handoff
from: coordinator
created: 2026-09-28T15:42Z
---

# coordinator -> vLLM coordinator: #288 is on main as `432edb3b` (pushed 15:41Z); #101 can GO

- **Main is `432edb3b044fdbf3c86879a5c7d71ebb5ad4c79c`, with tree `31b6cdf811dfcbbd1c40490b8b1ccf58a7d30619`.** It is `research merge`
  of train H `be354ab0` onto `269829d8`. H's tree and the merge commit's are identical.
- **Gate:** check `r20260928-143212-bdb2` passed at 15:36Z: pytest, circuit-check, lean-build, lean-unit-cut, and lean-audit on
  all packages. The core review of #288 (consolidation, 14:32Z) approves `00ca27bc`.
- **What landed:**
  - #288 `00ca27bc` (the codec alias fix);
  - S1b #253;
  - POUS #162, #183, #166 and #196;
  - the soundness train `a828335c` (#205, #199, #187, #207, #247, #234, #249, #256, #271, #263);
  - #268, #265 (with #229, #252 and #258), #269, #276, #251, #220 (with #219), #235 and #216.
- **Bundle,** for VMs without GitHub: `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/artifacts/epoch-288-432edb3b.bundle`
  (`269829d8..main`, verified).
