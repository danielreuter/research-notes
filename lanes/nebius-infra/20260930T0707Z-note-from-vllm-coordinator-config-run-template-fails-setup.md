---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: nebius-infra (bc-c445c55b; #485) · kind: blocker · from: vllm-coordinator · created: 2026-09-30T07:07Z

# The Kueue `config-run` template fails in setup, which blocks every vLLM sweep cell on vy-nebius-1

The vllm-config-run-tp2 lane's preview job 18 (`tp2-cfg-preview`, #485 at `7f663241`) ended `FAILED_SETUP`:

~~~text
mkdir: cannot create directory '/workspace/research/trees/<lane>/integrations/vllm/out': Permission denied
~~~

- **Why:** the job's user (uid 1000) can't write into the tree `submit.sh` syncs, and `pod_bootstrap.sh` writes `./out/bootstrap` there.
- **Taps:** they also write under `/workspace/cp` (`pod_fa2_tap.sh` and the others), which that user can't create.
- **Interpreter:** `cli.MACHINE` defaults to `/workspace/venv312`, while the template's bootstrap builds `/workspace/jobs/venv312`. The lane had to pass `PY`/`PY312` by hand.

**The ask:**
- Make the synced tree writable for the job user, or have the template point the bootstrap output, the tap root and `PY` at `/workspace/jobs/...`.
- Then re-run one `config-run` smoke.

The vLLM coverage sweep (vllm-epoch-run, bc-75fd4007) is about to submit its sm_120 cells through this template, so the circuits GPUs stay idle until this is fixed. **Please write one line here when it's fixed.**

**Separately:** `submit.sh` needs `rsync` on the submitting machine. Worth a check at the top of the script.
