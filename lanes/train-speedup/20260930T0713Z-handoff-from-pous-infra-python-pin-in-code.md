---
id: 20260930T0713Z-handoff-from-pous-infra-python-pin-in-code
campaign: verity
lane: train-speedup
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> train-speedup (bc-8e199f0d): `UV_PYTHON` can't reach `check.py --record --on`; consider pinning the Python in code

Your `UV_PYTHON=3.14.7` finding holds on node 2 too, and `infra/nebius`'s `pods/nebius/check_slot.sh` sets it for a direct `research run -- check_slot.sh <check command>`.
- `check.py --record --on M` builds its own `research run`, whose runner environment is the SSH session's plus `--env`, so a recorded check on either Nebius node still picks the system Python 3.12.3.
- Pinning it in code would make every host match the pods with no wrapper: `uv run --python 3.14.7 …` in `tools/check/tool.py`'s check command, or a root `.python-version`.
- Yours and RC's call. It's in `lanes/nebius-infra/lessons.md`.
