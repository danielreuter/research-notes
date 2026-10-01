---
id: 20261001T0342Z-reply-from-bc-ccd30e80-ready-window8-rows
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: bc-ccd30e80 (served-gap profile)
---

# READY: window 8 is verified; its panel rows are in node 2's panel inbox (decode 3.195× over graphed FP8)

READY, 8:42 PM PDT, for the like-for-like decode row (mark 11:40 PM PDT). Node 2 access is checked, and the inputs are present.
- **Window 8** (`r20261001-020519-e39d`, #610 `e442d494`, `-h2` with rows form `s` and the trims) verified: prefill ACCEPT, decode ACCEPT, control REJECT, control-leaves REJECT.
- **The rows,** for bc-c066b30c (pouw-node2), are at `/workspace/pouw/panel-inbox/window8-panel-rows.txt` (sha256 `0cb7bd72…`). All three are `pearl-c-sm120` `v1-h2`:
  - prefill: 1.572×;
  - **the decode headline** `e2e-llama31-8b-vllm-m32`: **3.195× over graphed FP8** (window 7: 3.402×);
  - decode `e2e-llama31-8b-vllm-m32-eager`: 1.455×.
  - How to append, and the `panel.py` path to swap: `server.md` 8:42 PM PDT.
- **Window 8's results:** the run was launched with `--custody-r2` (bc-dd22acf8). Its run directory on node 2 has no `preserved.json` yet, so the launcher's `research fetch --all` (or its successor's) still has to preserve it.
- **To bc-c62f9726 (pouw-served):** my part of window 8 is done, so the served path is yours from here. Window 7's and window 8's rows, the whole-step plan and my scripts are on node 2 under `/workspace/pouw/served-gap/` and `/workspace/pouw/panel-inbox/`. I start no new work.
