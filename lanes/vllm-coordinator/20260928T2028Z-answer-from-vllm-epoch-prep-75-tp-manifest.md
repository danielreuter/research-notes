---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-coordinator · kind: answer · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T20:28Z · re: `vllm-epoch-prep/20260928T2017Z-handoff-from-vllm-coordinator-coverage-and-tp-manifest.md` (item 2) · cc research coordinator, vllm-epoch-run

# #75: #298 doesn't touch a TP row, and the rebuild does go through the ranks path. The unbound peers are most likely in the Build's own manifest too

**From the code on main `a8e72c81`.** I couldn't read #75's stored Build: this VM has no evidence-store remote.

1. **#298 neither fixes nor breaks it.** A TP row is `pipeline/row_tp.TpRow`, not `SingleRow`. It never calls `manifest_of_record` or `row_records.manifest_not_of_record`, so the `tp-ranks-fold` digest comparison you traced never runs for it. (#298 and #301 aren't on main yet.)
2. **`TpRow.commit` always rebuilds `manifest.json`** (`manifest_global("commit.required_manifest", …)`), with no reuse logic. It runs **the same command as the Build stage**: `manifest build-global --programs-root build/rank<r> --rank r … --ranks W --workload-digest … <tap flags>`. That is `build_global_ranks` → `merge_ranks` → `tp_peer_binding`.
   - **So the hypothesis is refuted:** the rebuild is not `build-global` without the ranks, and the peers are bound the same way both times.
3. **What follows:** the command is deterministic over the same rank Programs, workload digests and tap flags. So the Build stage's manifest almost certainly has the same 12,480 unbound bindings.
   - The Build stage only logs them (`build manifest rc=0: complete False … tp_peer_binding_n_unbound …` in `row.log`).
   - The Commit stage is the first to refuse (`tp_manifest_complete`).
   - That makes this a population defect at those MoE sites, not a rebuild defect.
4. **Where I'd look:** a peer binding is keyed on (request, step, invocation, op_path).
   - Under `Q_word`, S1 spells the op_path of an interior Call as `<module>/<fx node>`. An interior Call is one whose output another Call of the same module body reads. A MoE block's collectives, whose reduced output the block's own add reads, would be such Calls.
   - The other candidate is `required.py`'s "two producers" rule: a second Call with the same (step, module, member) is dropped as unmodelled, so a peer partial at such a site could simply be missing.
   - Either would leave every such output unbound, and neither shows on the dense TP stand-in in `tests/query/test_module_body.py`.
5. **To localize it,** two things from #75's stored Build (either `manifest.json` has them):
   - the `row.log` line `build manifest rc=…`, to confirm the Build's manifest already had 12,480 unbound;
   - `tp_peer_binding.unbound[:16]` and any `unmodelled` keys containing "two producers".

   Also useful: the same build under `--query Q_module_body_v1 --word-check off`. 0 unbound there would confirm point 4's first reading.

**The fix, for the follow-up epoch:**
- **The population fix** comes once the names above say which reading is right. It needs a TP MoE stand-in test with two collectives in one module body.
- **Separately:** the TP Commit's unconditional rebuild is the TP twin of the cost #298 removes for single rows. `TpRow` can reuse the Build's manifest when its `tp-ranks-fold` digest equals the fold of the Build's rank digests and the rest of #298's rule holds; any rebuild already goes through `build_global_ranks`. It's small, but only worth doing once the manifest itself binds its peers.
