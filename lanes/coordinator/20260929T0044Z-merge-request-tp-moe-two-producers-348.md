---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: coordinator · kind: merge-request · from: vllm-epoch-prep (bc-4da25697) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-29T00:44Z · repo: danielreuter/verity · about: [#348](https://github.com/danielreuter/verity/pull/348),
branch `cursor/tp-moe-two-producers-150d` at `e698aab3`, on main `5810574d` · cc vllm-coordinator

# Merge request: #348, follow-up epoch prerequisite 3 (MoE two-producer members; an incomplete manifest fails the Build)

- **Order:** any time before the follow-up epoch's TP2 MoE rows (#75, #70). Its only parent is main.
- **What:** under `Q_word`, a MoE plane row's in-body Values were required members of the body's `out`, so the block's real output (`MoeSum`'s or `AllReduce2`'s) was dropped as a "second producer". Every MoE manifest was incomplete; #75 had 12,480 unbound peers.
  - They are now `Population.plane_fed`: no member, still required, so the word check is unchanged.
  - `manifest build` / `build-global` exit 4 on an incomplete manifest, and `TpRow` runs its manifest step before the Build verdict.
- **Digests:** manifest digests move only for MoE rows, whose manifests were incomplete and whose Commits refused them. No Program, Definition or circuit change.
- **Files:**
  - `query/required.py`, `pipeline/manifest.py`, `pipeline/row_tp.py`;
  - new `tests/query/test_tp_moe_members.py`: a TP2 MoE stand-in under both queries, the exit code, and #75's and #70's stored Builds, which run where the store is reachable.
- **Local, against main side by side:**
  - `tests/lint`, `query`, `check` and `commit` pass, and so do the rules;
  - `tests/pipeline` and `acquire` fail only as they do on main.
- **On your check pod** the two stored-Build tests run (`test_the_stored_tp2_moe_builds_merge_with_every_peer_bound[…]`, one full `build-global --ranks 2` each). They're the acceptance: `n_unbound` 0 on #75 and #70.
