---
id: 20260930T2310Z-finding-from-n2-commits-rc12-replays-mixed-template-chains
campaign: verity
lane: kueue-fold
kind: finding
status: open
repo: danielreuter/verity
origin: n2-commits (bc-698052e1), for kueue-fold and circuits; asked by the infra coordinator (bc-17cc41f1) at 4:00 PM PDT
---

# Node 1's rc-12 replays are chains that straddle the 2:15 PM PDT template refresh; no second template copy is in use

Every failed replay (task 2) in `/workspace/jobs/dispatch/done.jsonl` fits one pattern, 12 of 12:

- Its **Commit** (task 1) was dispatched before the refresh, on `config-run@9c6a41948938`. That is the two-task template, with no
  replay task and no `REPLAY_DEFERRED`, now at `/workspace/jobs/dispatch/infra/nebius/sky/jobs.bak-20260930T2115Z/config-run.yaml`.
  So it replayed on the GPU and sealed no bundle.
- When the Commit ended, `dispatch.py` reloaded the template by name (`TEMPLATES / "config-run.yaml"`, i.e.
  `/workspace/jobs/dispatch/infra/nebius/sky/jobs/config-run.yaml`) and found three tasks. It chained the **replay** on the refreshed
  template. That replay resolves `REPLAY_DEFERRED=auto` from the tree (which has `VLLM_REPLAY`) to 1, looks for a bundle and exits 12:
  "0 replay bundles named in commit/verdict.json".
- The Commit had passed on the GPU, e.g. `cov-g163`: `config PASS replay 460/460 equal`. These rc 12s are spurious: the row's
  result is there, but the dispatcher records the item as failed.

| key | Commit Job, dispatched (UTC), template | replay Job, dispatched (UTC), template | rc 12 at |
|---|---|---|---|
| cov-g172 | `nd-vllm-epoch-run-f53f4a4305-gpu-0`, 20:28:43, `9c6a41948938` | `…f53f4a4305-replay-0`, 21:56:22, `c43dba74fa68` | 22:23:43 |
| cov-g104 | `…012f61aafc-gpu-0`, 20:31:50, `9c6a41948938` | `…012f61aafc-replay-0`, 21:26:01, `c43dba74fa68` | 21:39:34 |
| cov-g159 | `…ed33395c9d-gpu-0`, 20:34:58, `9c6a41948938` | `…ed33395c9d-replay-0`, 21:22:53, `c43dba74fa68` | 21:37:28 |
| cov-g127 | `…41d023533d-gpu-0`, 20:37:02, `9c6a41948938` | `…41d023533d-replay-0`, 21:50:03, `c43dba74fa68` | 22:01:37 |
| cov-g163 | `…061b439d50-gpu-0`, 20:38:06, `9c6a41948938` | `…061b439d50-replay-0`, 21:39:34, `c43dba74fa68` | 21:40:37 |
| cov-g144 | `…aad5c043f4-gpu-0`, 20:40:09, `9c6a41948938` | `…aad5c043f4-replay-0`, 21:50:03, `c43dba74fa68` | 22:01:37 |
| cov-g139 | `…53e6ca0596-gpu-0`, 20:42:14, `9c6a41948938` | `…53e6ca0596-replay-0`, 22:08:58, `c43dba74fa68` | 22:24:47 |
| cov-g203 | `…130d4c4a53-gpu-0`, 20:48:30, `9c6a41948938` | `…130d4c4a53-replay-0`, 21:54:16, `c43dba74fa68` | 22:22:39 |
| cov-g150 | `…da1e0354a7-gpu-0`, 20:49:33, `9c6a41948938` | `…da1e0354a7-replay-0`, 22:07:55, `c43dba74fa68` | 22:23:42 |
| cov-g095 | `…f6268108de-gpu-0`, 20:52:40, `9c6a41948938` | `…f6268108de-replay-0`, 22:05:48, `c43dba74fa68` | 22:23:43 |
| cov-g119 | `…d6ab937e4a-gpu-0`, 20:55:50, `9c6a41948938` | `…d6ab937e4a-replay-0`, 22:13:11, `c43dba74fa68` | 22:23:42 |
| cov-g133 | `…a5875fa899-gpu-0`, 21:09:21, `9c6a41948938` | `…a5875fa899-replay-0`, 22:56:40, `9117b675808a` | 22:57:44 |

(All keys are `vllm-epoch-run/…`; Job names are `nd-vllm-epoch-run-…`. Source: `/workspace/jobs/dispatch/log.jsonl`, `submit` and
`end` events.)

- **No second copy is in use.** `dispatch.py` reads only `HERE/sky/jobs/`. The `jobs.bak-20260930T2115Z/` and
  `sky.bak-20260930T2120Z/` directories are backups. Today's `config-run.yaml` hashes to `56358e661222` (edited 23:03Z), after
  `c43dba74fa68` and `9117b675808a`.
- **Still exposed:** one pending Commit on `9c6a41948938`, `vllm-staging-bug/fix-g211`. cov-g089, cov-g153 and cov-g167 were also
  on it; they are held on node 2 now, and node 2 Commits force `REPLAY_DEFERRED=1`.
- **Possible fixes (kueue-fold's call):**
  - The replay task decides from the Commit's `commit/verdict.json`: no `replay_deferred.bundles` means it exits 0, as it does for
    `REPLAY_DEFERRED=0`.
  - Or the dispatcher chains an item on the template sha it started with (the `template@sha` in its submit event).
  - The 12 rows above can be relabelled from their Commit records.
