---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: nebius-infra (steward bc-fd19a2fe) · kind: handoff (design, coordinate) · from: vllm-coordinator · created: 2026-09-30T16:09Z · Daniel 16:05–16:07Z

# Daniel approved fully decoupling GPU generation from CPU checking: separate queues, separate workers, more CPU if that's the bottleneck

**The pipeline per vLLM deployment** ("cell" is now "vLLM deployment"):
1. **CPU `build` task:** `row stage build … --config-run 1`, as now. It needs no GPU (#536).
2. **GPU `commit` task:** `row stage commit … --config-run 1 --replay-deferred`.
   - It runs engine start-up, warm-up, the committed run, the weights pin and the commitment.
   - It then writes a **replay bundle** to shared disk and exits. No replay.
   - **GPU batching:** consecutive Commits with the same engine key (the same model, engine arguments, `--max-num-seqs`, code and environment) run through **the existing hot worker** (`pipeline/hot.py`), one warm vLLM process back to back. The GPU queue should therefore **order admissions by engine key**, e.g. a model's B1 deployments, then its B8 ones.
3. **CPU `replay` task:** `row stage replay …` (new).
   - It reads the bundle, the Build's Program and the checkpoint.
   - It replays the 460 units, and **opens every weight slice it consumes against the committed weights root**.
   - It writes the final `config_record.json` and the Attempt.

**What I need from you:**
- **Queues:** Commits only in `circuits`' GPU quota. Builds and replays in a CPU queue with no GPU. Size the CPU side so replay never backs up: batch-8 replays take 6–16 min of CPU each. Tell me the CPU you can give it and the per-task requests you'd use.
- **Templates:** a three-task `config-run` (build → commit → replay), with the replay task keyed to the Commit's bundle path on the node's shared disk. Also a bundle retention/cleanup rule; a batch-8 bundle is several GB.
- **Engine-key ordering** for the GPU queue: from the job's metadata, or a small admission hint the submit side sets. Your call.

**Code:** the TP2 lane (vllm-config-run-tp2, bc-35ab914e) builds `--replay-deferred`, the bundle and `row stage replay` in `integrations/vllm/`, and will send you the bundle layout and the stage commands. Don't wait for it to start the queue work.
