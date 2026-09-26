---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Pending review: VU exporter on by default (owner-approved 02:12Z; vllm-vu-export makes the change)

When its merge-ready handoff lands, check:
1. **Verdict and digest neutrality:** with the export on, #101's Program, manifest, run root and verdict equal the record; the export runs after the replay record and value source are taken, as in PR #42; `commit/verdict.json` is unchanged byte for byte.
2. **Failure isolation:** an exporter error is recorded and never fails or changes the Commit (or say explicitly if the owner wants it to fail).
3. **Cost:** wall-time and disk per row (#101 was 1,568 VUs, 186 MB). Large rows (#67, B=8 rows) must not push pods out of disk or past stage timeouts. Measure one large row, or bound it.
4. **An opt-out** (env or flag) for memory- or disk-tight runs, and the default resolved in one place (a5's typed config / CLI), not per script.
5. **Custody:** the exported sets go to R2 with the run (`--custody-r2` picks up the run dir) or are registered as artifacts; paths are documented.
6. The usual: clean merge on main, lints, P10, gate (b) same-pod, and a post-#29 tree with sampled_proofs on PYTHONPATH.

Then adopt it: the row scripts (`verity-vllm row` defaults, `tp_stage`, the regression runner) and `lane-briefs/vllm-cloud-common.md` (a "VU export" bullet: default on, where outputs land, opt-out, disk budget). The epoch's current runs are unaffected; the epoch adopts it only after its review.
