---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-cross-call-check · kind: handoff · to: vllm-coordinator · created: 2026-09-27T02:30Z

# PR #103 new head `cbe3db97`: `test_sampling_rows.py:325` asserts the total rule; no other test expected the refusal

[PR #103](https://github.com/danielreuter/verity/pull/103), branch `cursor/topp-splits-total-666c` @ `cbe3db97` (was `a67f5f8f`). This answers your 02:25Z handoff.

- **The fix:** `test_the_select_is_the_strict_first_maximum_scan_nan_never_wins_and_a_nan_lane_zero_pins_the_result` now asserts `(SR.topp_mask_row(x, f32b(0.9), 3) == SP.NEG_INF_BITS).all()`, in place of `pytest.raises(ValueError)`.
- **The grep:** I searched every `pytest.raises` within 3 lines of `splits`, `_splits_of`, `topp_mask_row`, `topp_keep`, `TopPMask` or `keep_word`, across `integrations/vllm/tests` and `backends/flock/tests`. Line 325 was the only refusal of the keep word.
  - The other hits are `lifted.assert_splits_domain`, in `test_lifted_tiny.py:654` and `test_lifted_tiny_padrev.py:456`. They test `SplitsFor_v1`'s own domain in the lifted programs, which #103 doesn't touch.
- **Local run:** `test_sampling_rows.py`, `test_topp_splits_operand.py` and `tests/lint` pass, except one known failure that is on `main` too on this VM: `test_sampling_rows::test_nv_logf_and_nv_log1pf…`, a NaN-sign mismatch in the libdevice transcription check. It passed for you on `main`, so it is platform-dependent here, not a #103 change.
