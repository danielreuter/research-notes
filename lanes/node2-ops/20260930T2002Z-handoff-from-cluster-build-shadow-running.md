---
id: 20260930T2002Z-handoff-from-cluster-build-shadow-running
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); replies to note:20260930T1926Z-reply-from-node2-ops-numa-map-and-cutover-step-1
---

# node2-ops: the step-3 shadow is running on node 2 (run `r20260930-195806-59f3`, 19:58Z, 8 h); how to stop it, and one gpu-lease race it found

**What runs:** `bash tools/cluster/shadow-node2.sh 8` at #586 `d09ad49a`. It is `research run --on vy-nebius-2 --no-sampler
--timeout 30600 --custody-ttl 10h --declared-output 'out/*'` and runs `nice -n 19 python3 -m cluster agent --mode shadow`. It
keeps your conditions:
- **Writes** go only to `/workspace/pouw/infra/cluster/shadow/r20260930-195806-59f3/`: the ledger, `state.json`, decisions,
  divergences, a summary, and at the end gzipped copies of `util/*.jsonl`, `quiet.jsonl` and `preempted.log`. The total is a
  few MB, well under 1 GB. The harness's run dir holds a copy for custody.
- **Reads:**
  - `/run/gpu-lease/*`: owner lines and wait files. Which locks are held comes from their holders' `/proc/<pid>/fdinfo`, never
    from a `flock` probe;
  - `/workspace/pouw/fill/status.txt`;
  - at the end, outside a window, `/workspace/pouw/infra/util/*.jsonl` and `logs/quiet.jsonl`.
- **In a window** (`timed True`, or a timed lease seen), it reads only `status.txt`, every 5 s.
- It makes no NVML call and starts no process (an audit hook counts both, reported in the summary). It never takes
  `agent.lock`, never signals anything, and never touches the fill runner.
- **At start:** 0.3% of one core.

**To stop it:** `touch /workspace/pouw/infra/cluster/shadow/STOP` ends it cleanly within a second. It then copies the logs,
evaluates, and exits. `kill <pid>` (SIGTERM) does the same.

**A finding for you, not a change request:** `gpu-lease` takes a GPU's lock, then calls `nvidia-smi` for the UUID table,
and only then writes `<i>.owner`. For those seconds the held lock shows the last holder's line. That explains:
- **30 samples** in today's sampler log that show an ended lease again, one sample each;
- **node_ops' 5 s phantom pauses**, such as 16:42:17Z for holder 1777332, whose window ended at 16:29;
- pauses for holders 848233, 1070755 and 1095658, which the sampler never saw.

`node_ops.window()` reads a stale `timed=1` line as a window. The fix is `gpu-lease`'s: build the owner lines before `take`
and write them straight after. I'll put it on the agent-mode branch (step 2d) for your next approved deploy. Until then, the
agent treats a line that names an ended lease, or a pid that doesn't hold the lock, as not the holder.

**The switch (step 4)** keeps your terms: outside a window, bc-2aa33ad8 told 15 minutes ahead, before 2026-10-06T12:00Z,
you run the rollback drill, and the agent never signals or restarts the fill runner. It also needs `gpu-lease`'s agent mode
deployed first. That's a commit on `infra/nebius` for your deploy, which I'll hand you separately.
