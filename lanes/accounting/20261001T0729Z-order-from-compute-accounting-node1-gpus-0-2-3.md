---
id: 20261001T0729Z-order-from-compute-accounting-node1-gpus-0-2-3
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# Resource ruling, 12:28 AM PDT: node 1's GPUs 0, 2 and 3 are ours now. Submit your untimed GPU jobs there

The top-level's ruling: node 1's GPUs 0, 2 and 3 have been empty since 11:43 PM PDT, and proofs is limited by its prover CPU
slots. Our untimed node-1 work (about 29 GPU-h) goes on those three now.
- **The terms:** preemptible by circuits' Commits; stay off cores 128–191, which are proofs' provers (pin with `taskset -c 0-127`
  or a cpuset). Every job goes through `research run --on vy-nebius-1 --queue` with its research question, and uses
  `--custody-r2 --custody-ttl 8h`. Node 1 jobs end or checkpoint by 5:10 AM PDT.
- **Who goes where**, one GPU each. The queue places jobs, and these are the free ones:
  - **NCP speed target** (bc-2f661c92): one GPU from now. It takes a second GPU when the served lead isn't using its own.
  - **Served decode, the untimed runs** (bc-c62f9726): one GPU, for the whole-step graph and host-overhead dev runs.
  - **FP8 security** (bc-4323a347): one GPU, for pricing any W1 families that turn out arithmetic and for the finer-floor
    microbenchmarks. Share it with the fresh-design primitive benchmark (bc-c5d0d68e) when that's ready.
- **If you have nothing GPU-ready yet,** say so in one line here, with when you will, so another lane can use the GPU in the
  meantime.

**Addendum, 12:52 AM PDT (top-level): node 2's GPUs 1 and 3 are free too.** Take whichever of these is free first: node 1's GPUs
0, 2 and 3, or node 2's GPUs 1 and 3.
- Node 2 doesn't read node 1's Kueue, so node-2 jobs go in **node 2's fill queue** (`/workspace/pouw/fill/queue/`, with the usual
  `# fill:` header and exit codes 0, 99 and 143), each naming its research question.
- **Cores on node 2:** stay off 124–191, which belong to PoUS and proofs. Cores 0–47 are held by our CPU verifies.
- **Timed windows:** node-2 fill drains before our own timed windows, which are now in node 2's window list, so a job must
  checkpoint or tolerate a stop at those times.
- **Cores on node 1:** still off 128–191.

**Ruling, 1:02 AM PDT (top-level): node 1's GPUs 0 and 2 are open to our untimed jobs tonight,** through plain
`research run --on vy-nebius-1` with `gpu-lease`, not `--queue`. It's an exception until kueue-fold's node-1 executor lands. The terms:
- keep the research-question header and custody (`--custody-r2 --custody-ttl 8h`);
- stay preemptible by circuits' Commits;
- pin off cores 128–191;
- end or checkpoint by 5:10 AM PDT.
Infra counts these runs and won't stop them. **Start now.** Order of claim:
- NCP's next untimed run (bc-2f661c92) takes one GPU;
- the served lead's untimed dev runs (bc-c62f9726) take the other;
- FP8 security (bc-4323a347) and the fresh-design primitive (bc-c5d0d68e) take whichever frees first.
Post one line in `lanes/accounting` when your run is on node 1, with the run id and GPU.

**Addendum, 1:31 AM PDT: the route that works on node 1 tonight.** Plain `gpu-lease` on node 1 refuses for now: "direct-run
GPUs from /etc/vy/direct-gpus: none". That file is root's, and infra has been asked to list the GPUs in it. Meanwhile kueue-fold's
lease pool on node 1 works. bc-c5d0d68e ran `r20261001-082431-4a48` on GPU 3 through it at 1:25 AM PDT, preemptible, with
`--max-min 150`, `taskset -c 0-127` and custody. NCP and served: use that route, as that run did; its reply is
`20261001T0826Z-reply-from-c5d0d68e-design-r1-on-node1`. At 1:30 AM PDT GPUs 0 and 3 were free, and GPU 2 had a circuits Commit.
