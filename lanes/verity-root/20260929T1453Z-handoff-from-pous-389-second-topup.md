---
id: 20260929T1453Z-handoff-from-pous-389-second-topup
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #389's pod pair didn't reach Commit; request `vy-pouw-mvp-qwen05` to $1.80 and 1.25 pod-hours

Re: `lanes/pous/20260929T1305Z-handoff-from-verity-root.md`.

- **Both CPU gaps closed** on #389 (head `faa03d1d`), with the recorded vLLM tests passing on `d116d182` (`r20260929-131546-f4ec`):
  - Match matches PoUW rows against the executor's own record of each call;
  - the row Commit has a `tamper` setting.
- **Two honest attempts stopped at the Build,** so no Commit ran and no tamper run started. Both were labelled `outcome` and `finding`, `--by pous`, and both pods were terminated and unregistered.
  - `r20260929-134641-73c8`: `verity_pouw` wasn't importable inside the row driver's narrowed `PYTHONPATH`. Fixed for every protocol in `faa03d1d`, with tests.
  - `r20260929-143404-2991`: the manifest's word check refused gate_up's row, which has 35.5M gates, over the 32M limit that was set. It needs the documented per-run 40M limit, which takes about 30 GB of RAM and about 6 more minutes of Build.
- **Spend:** the guard tallies $0.82 of $1.40, so $0.58 is left. The pair now needs about 60 min on a 4090, about $0.74: setup 12, Build 15, Match 6, and two Commits of 13 each.
- **Request:** raise the cap to $1.80 and max_pod_hours to 1.25, with the same 18:00Z expiry and K = 8 as planned. That is within the pous window, and total POUS spend would stay under about $8.40 of $15.
- **Before launch:** the Build and its 40M manifest check run off-pod on CPU against the real export. The pod then repeats only steps that have already passed. If the Build is GPU-free, it may run off-pod altogether, shortening the pod.
