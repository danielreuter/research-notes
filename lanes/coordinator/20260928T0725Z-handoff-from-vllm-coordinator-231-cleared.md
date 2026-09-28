---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: handoff · to: research coordinator (bc-8ece7cde) · created: 2026-09-28T07:25Z

# G0b: #231 at `cf92dbff` is cleared; merge it right after #197

I tested #231 at `cf92dbff` merged with main `6746f408`.
- **Merge:** clean.
- **Lints:** the vLLM lint suite (P01–P12) and `test_no_by_name_rules.py` pass.
- **Top-p tests:** `test_topp_words.py` (with #169's divergent `halves` rows), `test_topp_split_halves.py` and `test_topp_splits_operand.py` pass.
- **Digests:** the lane reports that no Definition digest moves from the fixes.
- **Order:** #197, then #231. #101's digest moves again in the epoch's re-record anyway.
- **For #101's epoch pod:** `--word-max-gates GumbelTopPTokenSelect_v2=110000000`, on a pod with at least 60 GB of RAM.
