# ops-tools part A ready to merge: lane/ops-tools @ 0b0768ed (pods by ownership, IDLE-POD/ACCOUNT/RUNWAY alerts, relaunch, reaper, gc-worktrees)

- Merge `lane/ops-tools @ 0b0768ed` (base main b761c3a9). It touches only `tools/research/src/research/notes.py` and its tests
  (notes 40 passed; the whole research suite 305 passed at d0fb21cc). Part B (pod health, bootstrap threads, bench guard) comes
  later on the same branch: merge only A tonight.
- Watcher after the merge (the shim runs main):

~~~sh
research notes watch --every 2 --stale-min 12 --pods --since-hours 8 --exclude 'vllm*' --snapshot    # add --reap once you trust it
~~~

  Notify on `STALE|IDLE-POD|RUNWAY|FINAL-POD|REAPED|REAP-FAILED|MAIL`. `ACCOUNT` prints every pass; it is not an alert.
  `IDLE-POD <lane> <pod> <N>m`: an open lane's pod has 0 % GPU, no work process, no live verifier for >= 5 min (`--idle-min`).
  `RUNWAY <h>h` under 3 h (`--runway-h`), repeated per half hour lost.
- Relaunching a dead lane: `research notes relaunch <lane> [--as <succ>] [--why TEXT]` saves the work, supersedes, binds, and
  prints the launch message to paste. The default name is `<topic>-<N+1>`. Bind new lanes with
  `--brief <path> --final 06:30Z --budget '$5'` so the successor's message carries them.
- `--reap` terminates the pods of FINAL lanes that have no open successor, after 10 min, and logs each one to `~/.research/notes/reaper.log`.
  Kept pods: `checkpoint ... --keep-pod WHY`, or `research notes bind <lane> --keep-pod WHY` for a lane that is already final.
  At 04:06Z no finished lane owned a running pod.
- Live, first pass 04:06Z: `IDLE-POD wave-5090-2 vy-wave-5090-ro 12m ($0.99/h)`; `ACCOUNT $107.44 at $18.80/h, runway 5.7h; lane
  pods $10.08/h (12), other pods $8.35/h (6)`. `vy-live2b-verifier-ro` ($0.44/h, up since 20:58Z) carries no lane name, so it
  counts as "other". Is it kept on purpose?
- `research notes gc-worktrees` (list only; `--apply` removes): 0 removable now. 6 finished lanes' worktrees are dirty: ajtai-leaf,
  ligerito-relation, live-2b, red-team-leaf-2, red-team-ligerito-2, share-logup-2. Look before discarding them.
- `status` now shows one row per topic (`wave-4090-2 #2`) and every pod a lane owns, with $/h and busy/serve/idle. `--all` shows predecessors too.
