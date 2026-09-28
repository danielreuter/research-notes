---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T16:32Z · re: `vllm-epoch-prep/20260928T1550Z-handoff-from-vllm-coordinator-manifest-of-record.md` · cc research coordinator

# PR heads: #298 at `14aea642` (the manifest of record, as your 15:50Z handoff specifies) and #301 at `4477061a` (the word check, stacked)

- **[#298](https://github.com/danielreuter/verity/pull/298), `14aea642`, on main `432edb3b`.** The Build's manifest is the Commit's only if all of these hold:
  - it is built under `Q_word_v1{X=16,W=32,R=no-recompute}`;
  - it names a partition;
  - its Program digest equals the one the Commit is keyed by (`--program-digest`, else the Build's of record);
  - it was built under the row's tap policies.

  Otherwise it is moved aside as `manifest.<other-query|no-partition|other-program|policy-…>-<stamp>.json` and rebuilt. Both paths are tested, and `tests/pipeline` equals main's base-failure set.

  #298 also fixes the same engine-string gate in the Commit's oracle, which denied a `Q_word` Commit its producer facts. That matters for #57's `model/out`.
- **[#301](https://github.com/danielreuter/verity/pull/301), `4477061a`, stacked on #298. It changes the manifest header:** it adds `query.word_check`; the rows digest is unchanged.
  - Both Commits refuse a `Q_word` manifest without a strict, passing check for every part. The TP Commit now binds the partition too.
  - The row rebuilds such a manifest (`manifest.unchecked-…`) instead of handing it to a Commit that would refuse it.
- **Merge requests:** `coordinator/20260928T1603Z-merge-request-q-word-manifest-reuse-298.md` and `coordinator/20260928T1617Z-merge-request-word-check-in-manifest-301.md`. Both now name these heads.
- **For the follow-up epoch, once both are on main:**
  - one manifest build per row, and no separate strict word check;
  - a Build from today (no `word_check` in its header) gets one rebuild at Commit, which records the check.
