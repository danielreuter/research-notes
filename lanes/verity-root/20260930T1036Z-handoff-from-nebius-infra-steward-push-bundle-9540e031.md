---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
id: 20260930T1036Z-handoff-from-nebius-infra-steward-push-bundle-9540e031
campaign: overnight-sep30
lane: verity-root
kind: handoff
status: open
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> root: please push bundle `9540e031` to `infra/nebius` (my GitHub token is dead); three commits on `4e96ed05`

**Bundle:** the Project store's `artifacts/nebius/nebius-infra-bootstrap-cache-short-checks-9540e031.bundle`, 9,425 bytes (sha256
starts `8e79833b38f2607d`). `git bundle verify` says it is okay, and it requires `4e96ed05`. Branch in it:
`cursor/nebius-bootstrap-cache-e910`.

~~~sh
git fetch <bundle> cursor/nebius-bootstrap-cache-e910 && git checkout infra/nebius && git pull origin infra/nebius
git merge --no-edit FETCH_HEAD          # infra/nebius may have moved past 4e96ed05: merge, don't rebase
uv run tools/check/suites.py research repository && git push origin infra/nebius
~~~

**The commits:**
1. **`f3e0bf63`:** vLLM jobs share one copy of a tree per content (`sky/job_tree.sh`), so their native taps compile once per tree
   rather than once per pod. A bootstrap that already passed for a tree, its arguments and the venv is skipped without the host-wide
   lock (`sky/vllm_bootstrap.sh`).
   - **Why:** the GEMM lane's captures 110, 111 and 119 each waited 8–14 min on the lock behind GPU cells' ~3-min tap rebuilds.
   - **Measured on node 1:** a repeat capture skipped the lock, 49 s from submit to finish, against 65 s for the first run.
   - **Templates:** `config-run`, `config-run-row` and `port-capture` use it. `port-capture` still runs `$CMD` from a private copy.
2. **`fb923c3a`:** `check_slot.sh --short` gives short lane checks two shared slots on the check CPUs at `nice 10`, so they don't queue
   behind trains. Node 1's `/workspace/research/check-slots` is written (`32-63 64-95 8-31`).
3. **`9540e031`:** `submit.sh`'s freshness fetch never prompts for credentials, and its test no longer reaches GitHub. With a dead
   token, the research suite hung on a password prompt for 14 min.

**Tests:** `suites.py research repository` passes on `9540e031`: 2 suites, 6.3 min. New tests cover the job tree, the stamp skip
(no lock opened) and the short slot. If your merge conflicts in `sky/jobs/*.yaml`, keep both sides' changes and take my
`SRC=$(bash … job_tree.sh …)` and `vllm_bootstrap.sh` lines.
