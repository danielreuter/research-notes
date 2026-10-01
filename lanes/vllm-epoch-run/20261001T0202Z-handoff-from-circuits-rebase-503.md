---
id: 20261001T0202Z-handoff-from-circuits-rebase-503
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: low priority: rebase #503 onto main (conflicts in test_config_run.py and config_record.py) when your queue is steady

The PR hygiene audit flags #503 (uniform k-unit replay draw) as conflicting with main in `test_config_run.py` and `config_record.py`. Your run
branch carries it already. When the feeder is steady, merge main into #503 (merge commit, no force-push), keep #503's uniform draw and its
port into PR A's `c2_replay` / `replay_bundle.ARGS`, and post the new head in `lanes/circuits/` for a grant. Not urgent: the queue comes first.
