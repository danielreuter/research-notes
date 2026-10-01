---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits, cc n2-commits · created: 2026-10-01T04:00Z

**Checkpoint:** 492 deployments labelled, counting each by its latest label, with node 2 kept apart: 170 pass, 15 fail, 292 unsupported, 10 held. Node-2
Commits: 4 pass (g091, n082, n083, n084), held from the record until the cov-g217 gate. 5 are queued, and bundles waiting are 0 GB.

- **My feeder did nothing useful from 02:41 to 03:41Z.** Every pass hung in, or died on, a health check of the old SkyPilot API tunnel (`curl
  127.0.0.1:46580`), although no SkyPilot-route deployment is queued any more. A hung pass's output was lost to buffering.
  - Fixed: the feeder touches SkyPilot only when such a deployment is queued, and logs line-buffered.
  - Commits kept running meanwhile, under the dispatcher and the pacer. The labels caught up at 03:41Z.
- **TP2 with the token-budget fix works at head_dim > 64:**
  - p036 (Mistral-7B), p104 (Qwen2.5-7B), p092 (Qwen2.5-1.5B), p024 (Phi-3-mini) and p047 (Qwen3-4B), TP2 B1 256/32, each pass 460/460 summed over
    the ranks;
  - so do the head_dim-64 rows p000, p012, p004 and p016;
  - OLMoE and Qwen3-30B-A3B B1 are building, with the B8 rows behind them.
- **Gemma-2 B32 hits the template's commit watchdog.**
  - m003 (greedy) and n043 (top-p) were stopped (rc 86) after 903 s and 915 s with no commit.log output. That was Gemma's slow host evaluation after
    the control pass, not a hang: Gemma's slowdowns are ×55 to ×184.
  - They're resubmitted once with `COMMIT_STALL_S=3600`, and the stopped attempts are marked superseded.
  - So far k06, m006, n035 and n031 pass.
  - A Gemma-2 B32 Commit will hold its GPU for a long time. Say if you'd rather it wait.
- **@n2-commits: Commits are bouncing between the nodes.**
  - g043, g073, g092 and n129 were each moved to node 2, failed there within about 40 s (rc 1, about 02:26-02:38Z), then were resubmitted to
    node 1. g073 was moved once, the other three twice.
  - Node 1 decided them: g043, g073 and n129 pass 460/460, and g092 fails (EOS).
  - Node 2's failed attempts land in the row's own run record. My feeder now labels the attempt that the outcome came from and supersedes any
    earlier one. It also takes the node from the Commit's host as well as the record attempt's, since the node-2 marker file stays in a row
    even after its Commit came back.
- **A third EOS fail-closed case:** g092 (TinyLlama B16 1k greedy, request r15). The others are g160 and n105, all three under the 01:45Z finding.
