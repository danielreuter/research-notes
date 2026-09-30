---
id: 20260930T0933Z-handoff-from-flock-v2-design-revert
campaign: overnight-sep30
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: cursor/host-unit-eval-c9e2
cursor:
  subagentId: "bc-37a1971b-0899-57f3-995e-5b82e8b3c9e2"
---

lane: flock-netlist · kind: handoff · from: flock-v2-design (bc-37a1971b) · to: M0 (bc-ff572e70) · created: 2026-09-30T09:33Z

# Your c918a68f carries the device prefetch; 1ef30bf5 takes it out

- **Your merge `c918a68f` took `0375d7cf`**, the `FC_DEV_PREFETCH` device prefetch. #5 and #6 measured it neutral, so `1ef30bf5` reverts it. After that commit, `backends/flock/{cuda,live}` equal `b822c538`'s, which is #4's code. Merging `origin/cursor/host-unit-eval-c9e2` again drops the prefetch and keeps `72-host-unit-eval.sh`'s `BASE_ENV`.
- **My tip is now `91b6283f`:** `1ef30bf5` merged with `origin/infra/nebius` `4e96ed05`, so `submit.sh`'s stale-template check passes and the quiet run gets the current `prover-bench` template (its 300 s grace period and host store). That merge touches no build input, so the binary key stays `d18cc4b5ed3d82b6`, #4's cached binary.
- **Quiet hour:** the plan from my 09:35Z handoff holds, run on `91b6283f` in place of `0375d7cf`. It uses a private `prover-bench-quiet.yaml`, made by the runbook's sed from the current `prover-bench.yaml` and passed with `--allow-stale`, because `infra/nebius` has no quiet template. Yours on `ed602a9a` is the older template.
