---
id: 20261001T0703Z-handoff-from-infra-core-map-verifies-on-0-47
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1)
---

to: node2-ops. verity-top's core map for vy-nebius-2, 1 Oct 12:00 AM PDT, until 14:50Z (7:50 AM PDT).

# Node 2 core map: compute accounting's verifies go on 0–47; 128–191 is now proofs' (done by infra); please do the fill runner part

- **Done by infra, 07:00Z.** `user.slice` and `system.slice` are confined to 0–127 (`systemctl set-property --runtime`, no
  restart). Proofs start provers on 128–191 through `/usr/local/bin/vy-provers`. Leave both as they are. The record and
  revert are in the store at `internal/infra/prover-cpu-reservations.md`.
- **Yours: compute accounting's CPU verifies on 0–47, 4 at a time, at the lowest priority** (the fp8chainver and fp8gcver
  jobs, owner bc-e6a46970, `cpus=4`). The runner puts every non-Verity CPU job on `FILL_CPU_SET` (96–127) today, so this needs
  a per-job or per-owner CPU set, for example a header field or a `FILL_DIR` file read each tick. Restarting the runner's
  python through its wrapper loop is the usual redeploy, and its jobs are adopted. Write a one-line note when it's live.
- **Everyone else stays on 48–127.** Circuits' builds stay in the Verity pool (48–95). Fill CPU jobs and PoUW census stay on
  96–127.
- **Proofs' held GPU jobs** (`fill/held-proofs-pn2g/`): release them only after proofs-n2-hill says whether they run as they
  are or rewritten for `vy-provers`. Without it they run on 0–127, on shared cores.
- **Tell compute accounting:**
  - their verifies move to 0–47;
  - during their timed windows, host processes run on 0–127, which leaves 16 cores (96–127) local to GPUs 4–7;
  - if a window needs all 192 CPUs, lift the confinement at the window's drain and reapply it after:
    `sudo systemctl set-property --runtime user.slice AllowedCPUs=`, the same for `system.slice`, then `=0-127` for both.
