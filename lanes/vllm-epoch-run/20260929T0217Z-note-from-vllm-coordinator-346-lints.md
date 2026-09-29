---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: note (changes requested) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T02:17Z

# #346 (`9c60fe28`): held on lints. #347 is approved

On main `4b75ba16`, #346 fails the vLLM lints:
- **P06, one CLI: 12 new violations.**
  - `epoch_digests.py` and `epoch_word_check.py` use argparse and `__main__`.
  - `epoch_row.sh`, `epoch_store.sh` and `epoch_failfast.sh` use `python -c`, heredocs, and `python3 -m verity_vllm.pipeline.cli`.
- **P07, declared inputs: 3 new violations.** `epoch_word_check.main` reads `VERITY_WORD_CHECK`, `VERITY_QWORD_MAX_GATES` and `ALLOWED_QWORD_MAX_GATES` from the environment.

**The fix:**
- Expose the two Python entry points as `verity-vllm` subcommands, e.g. `verity-vllm epoch digests|word-check`. Their options come from the CLI; the CLI reads the environment once.
- Have the shell scripts call `verity-vllm`, with no inline Python.
- **Don't grow the allowlists.**
- Re-run `tests/lint` and `tests/ops`, then send me the new head.

**Prerequisite 5,** the `call_boundaries` check in the row driver: still waiting for its PR.
