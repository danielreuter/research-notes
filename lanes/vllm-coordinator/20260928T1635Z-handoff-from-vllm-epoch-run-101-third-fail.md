---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T16:35Z · re: `lanes/vllm-epoch-run/20260928T1559Z-GO-from-vllm-coordinator-replan-2330z.md`

# #101's third try (edac1cf6) got past GP-01 but failed in the manifest step: `GumbelTopPTokenSelect_v2` is not a registered Definition

- **Where it failed:** `manifest build` → `query.program_view.from_instances` → `_instances_columns` → `definition_ports` raises
  `KeyError: 'GumbelTopPTokenSelect_v2 is not a registered Definition'`. `build rc=13` (manifest not built), at 16:24:58Z.
- **What passed:** #297 did its job. The workload Program composed (`66df03fb…`), and the request Program is `11e8da5d…`.
  The program view's registry is the third place #231's sampler Definitions are missing.
  Owner: the lowering lane. `manifest build` on this row's stored Build reproduces it on CPU.
- **Evidence:** run `r20260928-160311-303b`; Build `art:2d65d5d7bdc21af3df01c041272e5a72b40a86bc74cc09075c7e726cc01f1fd0` and records
  `art:14775bd00edffa4524af27a22dd34417b1aaa8d976c84c4fcebaa38ed9c3bf08`, both PRESERVED (`manifest.log` is in the Build tree).
- **Row state:** the pod was terminated at 16:34Z. This try cost $0.43, and #101 is about $1.39 in total.
  - #101 keeps its old record, and its line in `20260928T1410Z-epoch-digests.md` says why.
  - Its $5 cap is back in the balance test's headroom.
  - **A fourth try** could still start by about 21:50Z (1.5 h) on a GO naming the fixed SHA.
- **Also:** #4's Commit PASSed at 16:27Z. It's a FAIL-class row, so its gate will defer it with the evidence, as you ruled at 12:31Z.
  #73's Build passed at 16:31Z, and its side-stored Build is `art:1b29fa7fb3da6c315d24a9a73bb13d742c29f651efc4745a89803a83deda25a3` (PRESERVED).
