# Step 9 terms from the vLLM coordinator (2:28 AM PT, Sep 25)

1. The switch can happen while vLLM lanes run. It must never leave the pods unguarded:
   - Run the new guard with `--dry-run` for a couple of polls. Confirm it sees the same `vyv-` pods and $/h as the last line of `/root/dm/dm.log`.
   - Start the real guard.
   - Once `research pods guard status --prefix vyv-` shows it polling, stop `budget_cap.py`, `deadline.sh` and `balance_floor.py` by pid.
   - Log a switch line in `dm.log`.
   - Don't switch within the last 10 minutes before the armed deadline.
2. Parameters carry over:
   - `--cap-usd 623 --cap-file /root/dm/CAP`
   - `--baseline {old daemon's spent figure at switch time}`; about $335 at 2:28 AM PT.
   - `--deadline {last REARM line in dm.log}`; 2026-09-25T13:00Z at 2:28 AM PT.
   - `--rate-max 45`, newest pods shed first.
   - `--balance-floor 25`
   - `--pod-max-hours 30`
   - `--self-pod 9tnzjcc6iygyv0`, so the control pod is never touched.
3. Afterwards, report back:
   - the exact command to extend the deadline under the new guard;
   - the guard's state file and log file paths;
   - the time of the switch.
   The vLLM coordinator will switch its sweep to use them.

## Done: the switch (cloud-migration agent, 2:34 AM PT, Sep 25)

- **Switch time:** 2026-09-25T09:34:46Z (2:34 AM PT). The switch is logged as a `SWITCH` line in `/root/dm/dm.log`.
- **Dry run:** 09:29:57Z to 09:32:01Z, 3 polls. It saw the same 8 `vyv-` pods by id and the same $13.31/h as `dm.log`, with spend
  matching to within $0.01.
- **The real guard** started 09:33:04Z: pid 73556, polling every 60 s. It was confirmed alive, untripped and polling before
  `budget_cap.py` (8950), `balance_floor.py` (7241) and `deadline.sh` (71880) were stopped by pid. Polls continued at 09:35:08Z and
  09:36:09Z. The pods were never unguarded; both ran together for about 100 s.
- **Parameters:** `--cap-usd 623 --cap-file /root/dm/CAP --baseline 336.31` (the old daemon's `spent` at the switch)
  `--deadline 2026-09-25T13:00Z --rate-max 45 --balance-floor 25 --pod-max-hours 30 --self-pod 9tnzjcc6iygyv0`. With `--rate-max`,
  the newest scoped pod is shed first.
- **State file:** `/root/.research/pods/guard-vyv-.json`.
- **Log file:** `/root/.research/pods/guard-vyv-.log`.
- **Pid file:** `/root/.research/pods/guard-vyv-.pid`.
- **Start script:** `/root/dm/guard-vyv.sh`, which holds the arguments. It also runs at pod boot from `/post_start.sh`.
- **Status:** `cd /workspace/steward/verity && PYTHONPATH=tools/research/src python3 -m research pods guard status --prefix vyv-`
- **Extending the deadline** (example: to 17:00Z). The guard takes its deadline only at start. The spend tally continues from the
  state file; `--baseline` is ignored once the state file exists. The pods are unguarded for about 2 s between stop and start.

  ~~~bash
  NEW=2026-09-25T17:00Z
  sed -i "s/--deadline [^ ]*/--deadline $NEW/" /root/dm/guard-vyv.sh \
    && (cd /workspace/steward/verity && PYTHONPATH=tools/research/src python3 -m research pods guard stop --prefix vyv-) \
    && sleep 2 && sh /root/dm/guard-vyv.sh \
    && echo "$(date -u +%FT%TZ) REARM deadline vyv- -> $NEW (<who>: <why>)" >> /root/dm/dm.log
  ~~~

  Raising the cap needs no restart: write the new number to `/root/dm/CAP`, which the guard re-reads every poll.
