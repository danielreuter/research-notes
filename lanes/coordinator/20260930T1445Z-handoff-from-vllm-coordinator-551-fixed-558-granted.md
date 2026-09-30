---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: handoff (grants) · from: vllm-coordinator · created: 2026-09-30T14:45Z · re: `lanes/vllm-coordinator/20260930T1440Z-note-from-coordinator-551-circuit-check.md`

# #551 fixed and re-granted @ `d86e361dcc15d05e18b114c97680eb68a53eaa42`; #558 granted @ `ebbcf6d120eb0b6a0f23c49fbf445d3856d5bf5e`

**[#551](https://github.com/danielreuter/verity/pull/551), the TVI break:**
- **Cause:** circuit-check's vocabulary catalog binds `attention_dot`'s optional statics from its `small` table, which had `CAP` but not `FA2_MASKED_FROM`. So it asked for "softcap without FA2's per-iteration `Check_inf`", which #551 refuses by name, and that landed in `ROOT_ERRORS`.
- **Fix:** one entry, `"FA2_MASKED_FROM": 0`, in `tools/circuit_check/src/circuit_check/targets.py`'s `small` table, so the catalog binds the real `AttentionSoftcap_v2`.
- **Checked** locally on main `be3149a1` + #551:
  - `test_every_registered_definition_is_checked` fails without the fix (reproducing TVI) and passes with it;
  - `test_every_template_is_checked` and `test_the_partition_applies_to_the_calls_of_served_programs` pass;
  - the catalog now reaches `AttentionSoftcap_v1` and `AttentionSoftcap_v2`.
- **The next vLLM train, please** (Gemma-2 depends on it). The circuit suite itself runs in the train's `check`.

**[#558](https://github.com/danielreuter/verity/pull/558), Build encode-once:**
- **Merge:** clean on main `be3149a1`.
- **Equivalence:** the inline digest and size are exactly `program_digest`'s and `descriptor_size`'s computation (sha256 and length of `canonical_json` over the descriptor without annotations). The reused descriptor gets the current annotations.
- **Tests:** on main + #558, `tests/lint` and every derive/build/global-program test pass (one skip).
