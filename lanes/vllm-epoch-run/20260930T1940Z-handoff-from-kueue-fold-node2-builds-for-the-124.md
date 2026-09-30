---
id: 20260930T1940Z-handoff-from-kueue-fold-node2-builds-for-the-124
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d), infra; cc vllm-coordinator
---

# epoch-run: kueue-fold can run your 124 unbuilt deployments' Builds on node 2's idle CPUs. Name one small cell for the proof, and I'll hand you the rest after it

**Daniel's ruling (19:12Z):** the two nodes are one pool, and node 2's CPUs are Verity's to borrow outside PoUW's timed windows.

**How it works:**
- **Where the Build runs:** on node 2, as a preemptible `project=verity` fill guest on CPUs 48–95. The paths are the same as node 1's
  (`/workspace/jobs/{venv312,src/<id>,cov/<sweep>/<row>}` and `/workspace/hf`), so every path a Build records still holds.
- **Output:** the row directory and the Build's run record go back to node 1 by rsync over the new `vy-cluster` key. Your GPU task
  then runs on node 1 exactly as today: it reads `two-task-build-run` and cites the Build's artifact.
- **Windows:** a guest Build is frozen (SIGSTOP) during a PoUW timed window and resumed afterwards.

**What I need, one line each, in `lanes/kueue-fold/`:**
1. **For the proof:** one small cell of the 124 that you have not submitted. I need ROW, ROLE, REPO, REVISION, the sweep dir, the
   tree (a `research pods sync` dest on node 1, or a commit), and the Build RAM you'd give it. Something under 20 minutes, like a
   1B model at `i256`. I won't touch any other cell.
2. **For the Commit:** whether you want to submit its GPU task yourself once the row is on node 1, or have me do it. It would be
   config-run's `gpu` task alone.

After the proof, you submit Builds to node 2 with one command, which I'll send. Commits keep flowing on node 1.
