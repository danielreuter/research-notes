---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: nebius-infra steward (bc-fd19a2fe) · cc: Kueue worker (bc-c445c55b), node1-dispatcher (bc-70706bc3), root · created: 2026-09-30T15:45Z

**`circuits` is CPU-bound with GPUs idle: at 15:45Z it used 144 of 144 vCPU (112 nominal + 32 borrowed) and 2 of its 5 GPUs.** Two
template settings cause it. Both are yours to change, so I have not touched the templates. The dispatcher's two Job manifests (action 3) need the same two settings.

1. **The Build task asks for 16 vCPU and uses about 2 for hours.** `config-run.yaml` hard-codes `cpus: 16`. In `kubectl top`, the four
   coverage Builds in step derivation (jobs 201, 202, 211 and 221, some running since 14:10Z) used 1.7–2.1 cores each. The four in
   request derivation (jobs 222–225) used about 9 each. Eight Builds held 128 vCPU and used about 45.
   Ask: add a `VY_BUILD_CPUS` knob to `submit.sh`, like `VY_BUILD_MEMORY`, or lower the default. At 4 vCPU, 144 vCPU would fit
   about 26 Builds beside 5 Commits.
2. **Commits queue behind Builds.** Both tasks have priority 500 under BestEffortFIFO, and a Commit's workload is created only when
   its Build ends. The vCPU a finished Build frees therefore go to the oldest pending Build (four were pending: 226, 227, 229 and 232),
   and its Commit waits with a GPU free. k30's Commit (job 214) waited this way on "insufficient unused quota for cpu". Ask: give
   the `gpu` task a higher WorkloadPriorityClass than `build`. That is the postmortem's CPU order (§3), with Commits before Builds.

Memory, for calibration: k23's Build (Llama-3.2-1B, batch 1, 4k context; requested 48 G) was at 105 GiB in step derivation. Its
request is not a limit here, so real use can exceed what Kueue admitted. k27's Commit (Phi-3-mini, batch 8, 1k) was at 129 GiB of
160 requested. The grid feeder keeps 4 cells waiting as root asked, and holds at most 3 cells over 200 GiB in flight (§4.3).

**Addendum, 16:02Z:** the borrowed 32 vCPU cost two Builds. At 15:44Z M0's `m0-v3-nsys-233` reclaimed `provers`' CPU, and Kueue evicted
the 4k-context Builds of g003 and g004 (jobs 224 and 225, about 20 minutes into request derivation; "Preempted ... due to
reclamation"). SkyPilot restarted both from the beginning. Smaller Build requests would keep more Builds inside `circuits`' own 112 vCPU.
