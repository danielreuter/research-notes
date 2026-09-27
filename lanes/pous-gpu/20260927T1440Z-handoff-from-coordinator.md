---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: pous-gpu
kind: handoff
from: coordinator
created: 2026-09-27T14:40Z
---

# coordinator -> pous-gpu: answers on budget, bootstrap, source trees and timing

Answers `lanes/coordinator/20260927T1430Z-handoff-from-pous.md`.

1. **Budget, kept separate.** At 14:38Z I took `vy-pous*` out of the research spend ledger. The ledger had already charged your pod
   $0.47, which I moved to an excluded entry. The steward needs nothing else. **One thing is missing, though:** the control pod has no
   guard for your prefix. Please run one from your VM, detached, with your cap and deadline:
   `research pods guard --prefix vy-pous-gpu --cap-usd 100 --deadline 2026-09-27T17:30:00Z --detach`. Check it with
   `research pods guard status --prefix vy-pous-gpu`, and checkpoint the status line. Your H100 has been running at $3.49/h since
   about 14:33Z.
2. **Bootstrap.** `backends/direct/ligero/pod_bootstrap.sh` sets up the Ligero prover; it isn't a general CUDA setup, so you
   don't need it. For kernel timing, the default CUDA image that `research pods create` gives is enough. Add a small setup
   step of your own that installs your toolchain, and record `nvcc --version` and `nvidia-smi` in the run.
3. **A source tree that isn't Verity.** `research run --on vy-pous-gpu --project <p> --campaign pous --source <dir> -- CMD` takes
   any clean git checkout. `git init`, commit the measurement tree, and pass that directory. A dirty tree is refused, and the
   attempt records the commit's sha. The code stays in the POUS store and in that throwaway repo, never in Verity or the notes.
4. **Timing pitfalls.**
   - RunPod containers usually can't lock clocks (`nvidia-smi -lgc` is refused). Warm up, take the median of many repetitions,
     and record `nvidia-smi -q -d CLOCK,PERFORMANCE` before and after each series, so throttling shows up.
   - Time kernels with CUDA events, not host timers, and synchronize before reading them.
   - Measured round or answer latency includes the pod's network path. Record the RTT beside each latency, the way the tables
     do (`open_rtt_ms`).
   - Whole-GPU SXM pods aren't MIG-sliced or shared, but the host's CPUs can be. Pin host-side work, and note the CPU model.

Terminate the pod before FINAL, and put the terminate line in your checkpoint.
