---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T14:10Z

# #101's Build fails on main 269829d8: the workload Program can't decode `TopPKeepWord_v1` (#231). Deferred, not written

- **What failed:** the Build's GP-01 compose (`global_program.build` → `workload.request_component` → `verity.ir.codec.decode_program`) raises:
  `ValueError: definition 'TopPKeepWord_v1{V=128256,S=32}' node 41: alias to argument 0 of node 41: aliases name an argument of an earlier node`.
- **What passed first:** the request Program derived (`83629e4e…`, 277 s). `build rc=10`, so there's no manifest, Match or Commit.
- **This is a code defect, not infra.** Core's codec rejects the descriptor that #231's keep-word Definition encodes. It will hit every
  single-request stochastic workload on main, so it needs #231's owner (the lowering lane).
- **Evidence:**
  - run `r20260928-134402-b58d`;
  - Build `art:dc2385d4e180327fabe7cae477073c42acf87dff1e592da40f97a9b04c81904b` and records `art:ab0db6da61cde0ba63c0875f96714d7427d21455befe05a83d0a8f987ccea608`, both PRESERVED (`build_workload.log` is in the Build tree).
- **Row state:** the pod was terminated at 14:09Z, after $0.49.
  - #101 keeps its old record, and its line in `20260928T1410Z-epoch-digests.md` says "deferred".
  - **Retry:** if a fix is on main by about 15:30Z, #101 can still start by 16:00Z (1.5 h). Send a GO naming the fixed SHA.
- **The others:** #73, #4 and #23 are running (#23 at 1 pair on 2× RTX 6000 Ada). #70 polls until 14:30Z.
