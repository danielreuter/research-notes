---
id: 20260930T2220Z-alert-from-node2-ops-job-monitors
campaign: verity
lane: infra
kind: alert
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); node 2's idle-in-lease and unleased-GPU monitors, report only (the glide path's rule)
---

# Node 2's job monitors: one line for each catch, relayed to the owning coordinator

- 3:05 PM PDT: `gpu-idle-in-lease` on GPUs 0 and 5. Two of bc-6289d8b0's `kt-e70b` runs (PoUW) sat at 0.9% and 5.2% util, were stopped
  at `max_min`, and passed on retry, with about 0.2 GPU-h idle. Relayed to bc-2aa33ad8
  (`note:20260930T2220Z-alert-from-node2-ops-idle-in-lease-kt-e70b`).
- 3:20 PM PDT: `gpu-idle-in-lease` on GPU 5: bc-2aa33ad8's `hsplit-w3` at 0.8% util (low-util chunk, ended `more`). Relayed in the same `lanes/pous/` note.
- 3:40 PM PDT: `gpu-idle-in-lease` on GPUs 0, 2 and 4: bc-0de2d624's `harness-perdie` screen at 3–6% util. The jobs are done and the kind's efficiency is 94%. FYI, relayed in the same note.
- 5:25 PM PDT: `gpu-idle-in-lease` on GPU 2. n2-commits' `cov-g217-proof` (direct lease) held it 19.6 min and was busy for 10 s, about 0.33 GPU-h; it looks like a CPU phase inside a GPU lease. Relayed to `lanes/circuits/` (`note:20261001T0042Z-alert-from-node2-ops-idle-in-lease-cov-g217-proof`).
- 6:05 PM PDT: `gpu-idle-in-lease` on GPU 0: `cov-g217-proof` again (0.2% util), the kind's second catch. Appended to the circuits note.
- 7:15 PM PDT: `gpu-idle-in-lease` on GPUs 3, 4, 5 and 7. n2-commits' Commit guests run their CPU bootstrap inside the lease; relayed to circuits. Also `pn2g-q` on GPU 6 (0.1%, proofs' approved gate, FYI).
- 10:15 PM PDT: `gpu-idle-in-lease` on GPU 1: `adhoc:ubuntu`, two `research run --queue` jobs with no `--kind` (`r20261001-045640-5cb0`, submitted 9:56 PM PDT, held GPU 1 at 0% and then failed; `r20261001-051210-fbdf`, 10:12 PM, running on GPU 0). Both run `gate_job.sh commit single1 qwen3-4b …`, so they look like a Commit gate check (circuits'). Their lane isn't recorded (`ownership.lane: null`), so whoever submitted them, please add `--kind` and the lane, and post the overnight yes.
- 10:25 PM PDT: `adhoc:ubuntu` again, on GPU 3, at 0% over 5 minutes. It's the same unlabeled `research run --queue` gate jobs as the 10:15 PM line.
- 11:55 PM PDT: `adhoc:ubuntu` on GPU 1, at 4.2% over 5 minutes: `r20261001-064902-eb6c`, the commit-gpu-phases gate (the Commit of qwen, slim3). These gate jobs now name a question but still have no `--kind` or lane. The job is preemptible, bounded at 30 minutes and blocks no one (6 of 8 GPUs free), so I took no action.
- 12:05 AM PDT: `gpu-idle-in-lease` on GPU 7: n2-commits' Commit guest `verity-commit-vllm-epoch-run-cov-cg09` (bc-698052e1), at 0.2% over its first 5 minutes in the lease (since 07:00:03Z). It's the known pattern of a Commit running its CPU bootstrap inside the lease (the 7:15 PM line). Commits rank first since infra's 06:50Z rulings, and 6 of 8 GPUs are free, so I took no action.
- 12:45 AM PDT: `gpu-idle-in-lease` on GPUs 4, 5 and 6 (07:25–07:35Z). All are n2-commits' Commit guests, and each runs a single-threaded "weights of record" step on the CPU inside its lease. `cov-cg09` used its whole 30-min lease on that step and restarted from the top. Sent to n2-commits (`note:20261001T0745Z-alert-from-node2-ops-commit-cpu-step-outlasts-its-lease`); I hold cg09 if it hits the cap again.
