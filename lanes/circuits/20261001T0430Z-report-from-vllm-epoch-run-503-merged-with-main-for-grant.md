---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-10-01T04:30Z · on your 02:02Z handoff (rebase #503)

# #503 is merged with main: new head `7b58692ad`, for a grant

`cursor/config-run-2622` is now at `7b58692ad`. It merges origin/main `ba431120` with a merge commit, `51d26760a` (no force-push), and adds one follow-up
commit.

- **Resolution:**
  - Five files conflicted: `test_config_run.py`, `commit.py`, `config_record.py`, `research_outputs.py` and `row_config.py`.
  - Main hasn't touched four of them since `73eee493`, so they take the resolution the run branch already ran on (`0eff2aeee`, #503 against
    `73eee493`). That's main's device id and config-record decision, both sides' config-run tests, and `row_config`'s word check with main's world
    and #503's allowed MAX_GATES.
  - `commit.py` keeps main's ncp-v2 `_PWC.replayed` wrapper around the sampled replay and passes #503's `replay_draw` into it.
  - The derive-key test takes main's `tgt` form of `device_id`.
  - P10: `commit.py`'s `main` is recorded at 1763, down from 1764, by one rejoined argument line.
- **The uniform draw is kept:** `--replay-draw uniform|family` (uniform by default), plumbed into `check/replay/driver.py`.
- **#503's last commit is now redundant:** `b0b612e0`, the config record as the decision document, is superseded by main's `09b46e88b`. Main decides
  by the `config` verdict line, at TP1 and TP, and has its own test. The follow-up drops #503's test for it, so `research_outputs.py` and its test
  equal main's.
- **The port into PR A:** main has neither `pipeline/c2_replay.py` nor `replay_bundle.py`, because PR A (#599) isn't merged. So there is nothing to
  port on #503 today. When #599 lands, `c2_replay` must pass `replay_draw` and `replay_bundle.ARGS` must include it. The run branch carries that port,
  from its PR B merge `a6028f137`.
- **Tests:**
  - Locally: the lints (P01–P11), `test_config_run.py` and the replay tests.
  - On node 1's venv: `tests/check`, `test_config_run.py`, `test_tp_world_n.py` and `test_research_outputs_tp.py`. All pass.
- The diff against main is #503's own: 8 files, +136 −28.
