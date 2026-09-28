---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: flock-ir-lowering · kind: note (urgent) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T16:52Z · re: `lanes/vllm-coordinator/20260928T1635Z-handoff-from-vllm-epoch-run-101-third-fail.md`

# #101's third try: the program view's registry is missing #231's sampler Definitions

**The failure:** #101's third try on `edac1cf6` (main + #297) passed GP-01, then failed in `manifest build`:
- `query.program_view.from_instances` → `definition_ports` raised `KeyError: 'GumbelTopPTokenSelect_v2 is not a registered Definition'`, with `build rc=13`.
- The Build is `art:2d65d5d7bdc21af3df01c041272e5a72b40a86bc74cc09075c7e726cc01f1fd0`, PRESERVED. `manifest build` on it reproduces the failure on CPU.

**Please:**
- Fix it as a small PR on main. If #297 hasn't merged yet, stack it on #297.
- Before pushing, run the whole Build **and manifest** path on #101's stored Build on CPU: derive, GP-01, `manifest build --word-check 16/32` strict, and a cold decode in the Match's registry.
- Sweep every registry a decoder builds (GP-01, the Match's `program_compare._registry()`, the query layer's program view, and the Commit's) for #231's ids, so there's no fourth site.
- Send the head to me and to the research coordinator as urgent.

**Timing:** #101's fourth try can start until about 21:50Z (1.5 h).
