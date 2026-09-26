---
cursor:
  subagentId: "bc-eab8c043-7f1c-5a4d-802c-0b9aa73f289b"
---

# Handoff from vllm-vu-export: please re-arm the vyv guard for the #101 L40S run-root check (20260926T1635Z)

lane: vllm-vu-export · kind: handoff · from: vllm-vu-export (agent bc-eab8c043) · created: 20260926T1635Z

**Ask: re-arm the deadline to 18:45Z.** I won't create a pod until your checkpoint says the deadline is re-armed.

- **The run:** one pod, `vyv-vu-export-g3` (1× L40S). It runs #101 Build → Match → Commit (PAIRS=1), then builds the manifest under both `Q_module_body_v1` and the new `Q_word_v1{X}` check at X=16 and X=32.
  - It confirms that the Program digest, `manifest_digest` and run root are unchanged.
  - It is step 3's GPU half from `docs/fine-query-plan.md`, approved by Daniel.
- **Expected duration:** about 60 min of pod time, 75 min at most:
  - pod create and bootstrap, about 15 min;
  - Build, Match and Commit, about 30 min;
  - the manifest checks and custody, about 10 min.
- **Cost:** about $2 at the L40S rate, capped at $5, charged to the vLLM budget ($716.74 of $770 at your sweep 48).
- **Launch:** about 17:30Z, once the `Q_word_v1` branch has passed its CPU tests. The width check is being reworked on Daniel's design note: bits of the IR's `out(S)`, not words.
  - If launch slips past 17:30Z, I'll send a new expected end time rather than run into the deadline.
- **Teardown:** I terminate the pod by pid after R2 custody is confirmed, and post a one-line checkpoint with the run id.
- Query of record, the re-baseline epoch and the other lanes' pods: untouched.
