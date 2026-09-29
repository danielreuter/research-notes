---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
id: 20260928T2220Z-request-from-backend-sweep-register-vyb101n-run
campaign: backend-sweep
lane: coordinator
kind: handoff
status: closed
repo: verity
origin: backend-sweep (bc-ea1c2c4f)
to: research coordinator (bc-8ece7cde)
---

# Please register `vyb101n-run` in the notes repo's machines.d; this VM can't push

- **Why:** this cloud agent's GitHub token has expired, so `research notes push` fails here.
- **The pod:** it's live for Daniel's approved #101 top-8 non-GEMM run on #327. It's covered meanwhile by:
  - the `vyb101n-` guard ($0.60 hard cap, $25 balance floor, deadline 23:30Z, 1 h pod max);
  - the pod's own backstop at 23:18Z;
  - the run script, which terminates it once both runs are preserved.

Please add `machines.d/vyb101n-run.toml` with:

~~~toml
# machine vyb101n-run: written by `research pods register`; one file per machine (research.pods.registry)
provider = "runpod"
pod_id = "5h2r6b37aplfl3"
project = "verity"
guard = 30
registered_by = "cursor"
registered_at = "2026-09-28T22:18Z"
~~~

**Closed:** `5h2r6b37aplfl3` was terminated at 22:31:34Z after its runs were preserved, so no registration is needed now.
