---
cursor:
  subagentId: "bc-21aca6c8-631a-51fd-8553-ad0d0947ad11"
---

# F1 custody test: PASS (10:53–11:04 PM PT, Sep 24; 05:53–06:04Z)

The run was launched from a cloud VM, and the launcher's side was lost mid-run. The run finished anyway. Its attempt and logs are on
R2, `preserved` passes from a machine that never saw the run, and the pod guard terminated the pod by itself. Code: `main` `2994bd25`.

| Step | Evidence |
|---|---|
| Pod | `research pods create --name vy-f1-custody-test --cpu cpu3c --vcpu 2 --disk 20 --register --project verity --guard 5`. This gave pod `qkt0vxvrkuc0sf` ($0.06/h), registered into a scratch `machines.d` (`guard = 5`), not the live notes. |
| Launch 05:53:47Z | `research run --on vy-f1-custody-test --project verity --custody-r2 --custody-ttl 1h --campaign cloud-migration-f1 -- sh -c '30 × (echo tick; sleep 10); echo finished > result-marker.txt'`. This is run `r20260925-055347-d34a`. The guard daemon started on the pod. |
| Launcher lost 05:55:09Z | The launcher's local runs dir and store were deleted mid-run. This is a stand-in for deleting the VM: an agent can't delete its own VM. |
| Run finished 05:58:52Z | The attempt shows state `done`, rc 0, host = the pod. The pod-side publish wrote `.custody` at 05:59. |
| Preserved from another machine | With a fresh store and runs dir, `research data preserved r20260925-055347-d34a` exits 0. The attempt manifest is on R2, and the artifacts `run_record` (13 files), `telemetry.events` and `telemetry.resources` are all PRESERVED (sha256-readback). |
| Logs on R2 | The run record holds `stdout.log` (ends `tick 30`), `stderr.log`, `launcher.log`, `job.json`, `status.json`, `resources.jsonl` (1.67 MB), and `result-marker.txt` (`finished`). |
| Guard | `state.json` read `verdict idle, unfetched []`: the `.custody` marker counts as custody. The pod was gone (404) by 06:04:17Z, 5 idle minutes after the run ended. No manual terminate was needed. |
| No credential left | No process environment on the pod held `AWS_SECRET_ACCESS_KEY`. The only file match was the custody `store.toml`, which holds env var names. |

Gap found and fixed in the runbook: `research data custody <run>` needs the run directory, so it can't serve as the check from
another machine. The check from another machine is `research data preserved <run>`, which is what F1 specifies. Step 10's F1 item
now says so.
