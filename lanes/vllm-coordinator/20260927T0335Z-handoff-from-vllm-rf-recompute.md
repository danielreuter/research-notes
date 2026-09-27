---
cursor:
  subagentId: "bc-06147ba0-d1ae-5ddc-84d6-00cb2d93cbba"
---

lane: vllm-rf-recompute · kind: handoff · from: vllm-rf-recompute (bc-06147ba0) · created: 2026-09-27T03:35Z

# Pod estimate for gate (b) on both fixes, plus one GitHub token refresh

**Status.** Both fixes are built and their CPU checks are done on the lane VM.
- **#74 FP8:** [PR #106](https://github.com/danielreuter/verity/pull/106) (draft), `cursor/vllm-rf-recompute-fp8-cbba` @ `df13126f`.
  - With the selector on, the row's `Q_word_v1` (with #98's member check) goes from 4 violations and 113.6 G recomputed gates to 0 and 0.
- **#57 Gemma:** `cursor/vllm-rf-recompute-gemma-cbba` @ `7aeffc5d`, committed but **not pushed**.
  - The GitHub App token on my VM went invalid at about 03:30Z: `git fetch`, `git push` and `gh` all get 401.
  - The commit is bundled at `lanes/vllm-rf-recompute/evidence/gemma-7aeffc5d.bundle` (in the notes repo).
  - **Ask:** a token refresh for this VM (agent bc-06147ba0), so I can push the branch and open its PR.

**Estimate (asking approval before any pod).** Nothing is running now.

1. **Gate (b) for both PRs.** One new CPU pod, `vyv-rf-recompute-cpu`, 16 vCPU, about $0.5/h, guard 90. `gate_b2.sh` in git clones, three sides on the same pod:
   - base: `main` `3040ac1f`
   - head FP8: `df13126f`
   - head Gemma: `7aeffc5d`, which also runs the new torch tests `tests/program/test_weight_only_once.py`

   Bootstrap takes about 30 min (slow wheel hosts), then about 35 min per side. That is about 2.5 h, **about $1.25, capped at $2.50**.
2. **Optional: a #57 Build A/B.** One L40S, about 1 h at $1.09/h, **capped at $1.50**. It would build one #57 request shape (for example `LP31_T52`) twice:
   - selector off: must reproduce the recorded request digest;
   - selector on: must show one `AddScalarBf16` per norm, and `cross_call` must report 0.

   The CPU evidence already covers the structure: I rewrote the recorded request Programs the way the Build does under `once` (below). So item 2 is only for the digest A/B on a real Build. Skip it if you prefer.

The total cap is $4. The lane uses only pods it creates.

**Gemma evidence so far (CPU).**
- On `build_request_LP31_T52`, `query.cross_call` reports 5,460 duplicate `AddScalarBf16_v1{N=2304,C=1}` Calls (12,579,840 gates) as recorded, and 0 after the `once` rewrite (105 Calls remain, one per norm weight).
- On `LP1024_T18` it reports 1,890 Calls (4,354,560 gates) as recorded. The other six Programs are running.
