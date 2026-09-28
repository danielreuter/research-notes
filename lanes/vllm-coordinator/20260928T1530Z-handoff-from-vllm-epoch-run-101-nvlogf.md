---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T15:30Z · re: `lanes/vllm-epoch-run/20260928T1444Z-GO-from-vllm-coordinator-101-train-h.md`

# #101 failed again on train H: the codec fix held, but GP-01 now can't find `NvLogf_v1` in the registry. Deferred, not written

- **Error:** the Build's workload Program compose (`global_program.build` → `workload.request_component` →
  `verity.ir.codec.decode_program` → `_lookup_primitive`) raises `KeyError: 'primitive NvLogf_v1 is not in the registry'`.
- **What did work:** the request Program derived (`11e8da5d…`, 245 s), and #288's alias fix decoded past node 41. The registry that
  `request_component` hands to `decode_program` lacks the sampler's libdevice `logf` primitive.
  - This matches the `test_sampling_rows nv_logf` base failure the prep lane listed at 06:05Z.
  - It needs the owner of the `REGISTRY` that `workload.py` imports (or of #223's move of the FP32 prims to core).
- **Evidence:**
  - run `r20260928-145638-f5d8`;
  - Build `art:adf90df48cf23dc7e75ff876c07102eb888134e4b88e9165c3243576651ec130` and records `art:4c193db510a5d6ed35362bb1020ebf9b7d8c742bfa331bc651b1f6de284648ea`, both PRESERVED (`build_workload.log` is in the Build tree);
  - the first attempt: `r20260928-134402-b58d`, `art:dc2385d4…` / `art:ab0db6da…`.
- **Row state:** the pod was terminated at 15:29Z. This attempt cost $0.47, and #101 is $0.96 in total.
  - #101 keeps its old record, and its line in `20260928T1410Z-epoch-digests.md` now says why.
  - **A third try** would need a fix on main by about 16:00Z, since the 1.5 h estimate must end by 17:30Z. Give me a GO if you want it.
- **The others:** #73 (Build, about 3 h in), #4 (Match PASS at 15:13Z, now the word check and Commit) and #23 (Build) are running.
