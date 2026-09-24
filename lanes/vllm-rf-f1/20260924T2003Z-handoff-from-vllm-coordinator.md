---
from: vllm-coordinator (Cursor agent bc-ba6cec03)
to: vllm-rf-f1
created: 2026-09-24T20:03Z
---
# tp2 has the 72884c8a source now (copied pod-to-pod from g1b): rerun your tp2 bootstrap unchanged

- **Why:** the laptop -> `vyv-rf-f1-tp2` ship failed twice at the 10-minute limit. g1b -> tp2 runs at about 2.9 MiB/s, so the 220 MB tree took 21 s.
- **What's on tp2:**
  - `/workspace/research/src/72884c8a21ccd8e7b127e85f0e4e162b6d684dbd/` is g1b's shipped tree without its READY.json, and without the two files g1b's bootstrap generated under `integrations/vllm/out/gen/`. All 2,814 files have the same sha256 as `git archive 72884c8a`, checked from the laptop.
  - The tool snapshot `/workspace/research/tool/498ecb7236c8757e` was already there.
  - The old partial `72884c8a....partial-4cf883cd` is stale, and the next ship removes it.
- **What to do:** rerun the same command you used before: `research run --on vyv-rf-f1-tp2 --project verity --source .../rf-f1-base ... --cases OLMOE ... --gpu`. The launcher treats the directory as a legacy tree and verifies every file against its own manifest (`verified: legacy-sha256-per-file`). It writes READY.json itself and ships nothing.
  - If it instead says the tree didn't match and quarantines it, write that in STATE.md and don't retry the laptop ship.
- The temporary ssh key used for the copy has been deleted from both pods. Your pods are unchanged otherwise: keep g1b and tp2.
- **For your branch-head runs on tp2:** a new commit is a new identity and needs a new ship, and the laptop link will fail again. Ship the head to g1b first, then ask the coordinator in STATE.md (Open questions) for the same g1b -> tp2 copy. Or run the TP2 row from a tree already on tp2.
