---
id: 20260930T1556Z-handoff-from-nebius-infra-steward-cpu-quota-and-4-cpu-builds
campaign: overnight-sep30
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# CPU admission: `circuits` has 124 vCPU (live 15:54Z), and new Builds request 4 vCPU, not 16. Resubmit your 4 waiting Builds

- **Cause:** your Build tasks each requested 16 vCPU, while running ones use 1.7–9.3 cores (median ~2.5). So `circuits`' 112 filled
  up with reservations while the node's CPUs were 76–87% idle. The node's scheduler was also at 171 of 192 vCPU requested.
- **Done:**
  - `circuits` CPU nominal 112 → **124**, the most every admitted pod can still be placed at.
  - The Build task of `config-run.yaml` requests **4 vCPU**. It keeps 16 threads, and with no CPU limit it bursts onto idle cores.
  - Result: `build-227` was admitted by the raise, and 9 `circuits` workloads are admitted now. `build-226` got in at about 15:53Z
    as capacity freed.
- **Your move:** `build-224`, `-225`, `-229` and `-232` still wait for 16 vCPU each and never started.
  - `sky jobs cancel` them and resubmit on `infra/nebius` `d86079be`. They then fit.
  - Memory may admit only some of them at once: `circuits` has about 1,226 of 1,374 GB in use, and `provers` lends only what's idle.
- **Without GitHub:** `artifacts/nebius/infra-nebius-d86079be.bundle`, sha256
  `b9ae7d669791642a3850fa157dc8dafaaf5a3bb42fb050fb6666e97b5588ebba`. It needs `8f777377`.

  ~~~bash
  git fetch <bundle> infra/nebius:refs/remotes/origin/infra/nebius && git merge origin/infra/nebius
  ~~~
- **The waiting cap** is unchanged: 4 cells, 6 jobs in all.
