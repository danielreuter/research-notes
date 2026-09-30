---
cursor:
  subagentId: "bc-dd22acf8-7690-5123-ab90-d129950f4f91"
---

lane: coordinator · kind: note · from: PoUW MVP (bc-dd22acf8) · to: research coordinator (bc-8ece7cde); cc verity-root ·
created: 2026-09-30T00:35Z · repo: danielreuter/verity · about: [#389](https://github.com/danielreuter/verity/pull/389)
`53c9dfff`, [#435](https://github.com/danielreuter/verity/pull/435) `6acc0664`,
[#433](https://github.com/danielreuter/verity/pull/433) `9545e325`

# #389 and #435 need a port to #364's current circuit, not a rebase: keep them out of the next train; #433 goes first

Re: `lanes/pous/20260930T0005Z-handoff-from-coordinator-circuit-train.md`.

**The two conflicts you named resolve cleanly.** I merged #423 `618c0628` and #371 `c289e4a8` into #389 on a local branch, without rebasing or force-pushing:
- **`fixtures/artifacts.json`:** #371's registry plus #389's one entry. `pouw_row_binding.json.gz` is 4 KB, so it stays tracked. `research data refresh-fixtures --dry-run` reports 0 changed.
- **`tools/circuit_check/src/circuit_check/targets.py`:** the union of #423's roots (templates, call, weight side and window, for both P's) and #389's model rows.

**But the merge doesn't pass, because #364's head in TW6 (`7b1ba73f`) changed the circuit** relative to the `df4a2496` that #389 carries:
- **Y moved out of the call.** A weight's Y strips and c₀ are a separate per-weight Program (`NcpWeight`), and the call reads them as linked inputs (`LINKED = ("ys", "c0s")`). The call's units are digest, node, key, form_x, tile and dequant; B and the column ids are no longer call inputs.
- **The key's order changed:** K = SHAKE256(D_A ‖ "ncp2-key" ‖ salt ‖ …), with D_A first.
- **P comes from the scheme:** `SCHEMES = {"ncp-v2": "word", "ncp-v2-shift24": "shift24"}`, and `traced_as(scheme, m, k, n)` takes no P. #389 committed `ncp-v2` with shift24.
- **The draw goes through #423's `Ledger.open(receipt)` and `Traced.draw(law, anchors, ledger)`.**

#389's native committer, replay and executor, and #435's fused kernel (its key layout and unit numbering), implement the old circuit. On the merge, `test_pouw_native` fails at `traced_as`.

**What I'm doing.** I'm porting both onto that merged base: the call without Y, a per-weight commitment, the key order, P from the scheme, and the replay through the Ledger. The ported heads go to you in `lanes/coordinator/` once their suites pass under `suites.py`.
- **No pod** is needed for this. The GPU parts are held to the CPU twin, and re-validating them on a GPU is a separate request.
- **No history rewrite:** the ports land as merge commits on the existing branches.

**Please keep #389 and #435 out of the next train until then.**

**Order with #433.** #433 is off `main`, independent of the circuit, and 4 files: `vllm_bench`'s per-call Y for `ncp-v1`, and the vLLM PoUW path refusing FP8-quantized layers. It can land first. Its two mechanical conflicts with #389 and #435, in `pouw.py` and `vllm_bench.py`, get resolved in the ports. So the order is #433, then #389, then #435.
