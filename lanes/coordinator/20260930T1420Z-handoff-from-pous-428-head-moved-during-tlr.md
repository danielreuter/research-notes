---
id: 20260930T1420Z-handoff-from-pous-428-head-moved-during-tlr
campaign: pous
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous -> research coordinator: #428's head moved to `540a68a7` while TLR's check runs

Our lane pushed to #428's branch (`cursor/pous-trusted-layer-pins-576e`) at about 14:14:49Z, before it saw
note:20260930T1352Z-note-from-coordinator-461-lean-deps-pin saying TLR had already merged and re-hashed #428. Sorry for the
overlap; nothing further will be pushed to that branch.

- **The push:** a fast-forward from `00d31707` to `540a68a7`, one merge commit of `main` (`8a4e1147`). The only conflict
  was `protocols/pous/lean/lean-audit.json`, merged with `tools/lean/merge.py` and rehashed with `audit.py --update`; all
  66 `review.txt` lines read "rehashed with SHA-256: the same statement". Against `main`, the diff is exactly #428's 19 files.
  Local compare-mode audit, `check.sh` and the Python tests pass.
- **What we ask:** keep TLR on your own merge (check `r20260930-134914-6dcb`, expected `958a2e63`) if `research merge` allows
  it; if the moved head blocks it, `540a68a7` is content-equivalent and yours to take or overwrite.
