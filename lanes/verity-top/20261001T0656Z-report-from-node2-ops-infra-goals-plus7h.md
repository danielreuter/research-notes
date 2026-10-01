---
id: 20261001T0656Z-report-from-node2-ops-infra-goals-plus7h
campaign: verity
lane: node2-ops
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), timer infra-goal-plus7h (11:40 PM PDT); read-only counts at 06:53Z
---

CHECKPOINT none (13:10Z) [open] 6:10 PDT: node 1 batch b27b69c1c (C6 via #655+#638, lean import, #671, #664, #672, #674, #673, #675) handed to infra for check with lean-agreement; slot d c382dd846 still checking; 20 open PRs
CHECKPOINT none (12:54Z) [open] 5:54 PDT: node 1 cutover done (offline 5:40-5:46, quotas on); TS2 landed, main da9a9cfe, 20 open PRs; slot d stack past pytest; node 1 batch C6+#672+#664+#671+lean import+#673 next; quiet-hour holds kept to 6:30 for proofs' timings
CHECKPOINT none (12:39Z) [open] 5:38 PDT: T663 landed (main bde974431), 29 open PRs; node 1 cutover starting 5:40; node 2 offload cap to 25 min approved; node 2 disk 48%, served passes pruned after preservation, no deletes of held data
CHECKPOINT none (12:23Z) [open] 5:23 PDT: node 1 queues held for 5:40 cutover; #672, #664 ready for node 1 after 5:55 with C6, #671, lean import; slot d checking c382dd846; 28 open PRs; queue-placement option A chosen
CHECKPOINT none (12:09Z) [open] 5:08 PDT: Boolean IR floor hit (#672 ready, head 80703ab0e, node 1 after 5:55); slot d checking c382dd846 (r20261001-120046-c50b); C6 pin confirmation going to lander via infra; cutover 5:40 go
CHECKPOINT none (11:52Z) [open] 4:52 AM PDT: 4:50 check collecting; node 1 stacks failed on #557 x #664, #664 out, slot d 5:00 rebuilt without it; cutover on schedule
CHECKPOINT none (11:37Z) [open] 4:37 AM PDT: main d8865092, 28 open; node 1 checks of c0097b93b and 97c7ed118 due ~4:35; slot d 5:00 armed for dcc7cc57d (+#667); 4:50 check next
CHECKPOINT none (11:21Z) [open] 4:21 AM PDT: Boolean IR on main (d8865092), 28 PRs open; node 1 checking 97c7ed118 (lands the rest), slot d 5:00 takes #667 + Boolean PR 1
CHECKPOINT none (11:06Z) [open] 4:05 AM PDT: main still ef6a3e74, T654 due; lander didn't start slot b, infra asked to check c0097b93b itself; slot d 5:00 stack 97c7ed118 built
CHECKPOINT none (10:50Z) [open] 3:50 AM PDT: 31 PRs open; slot d checking ecf7d9e36, slot b train c0097b93b posted to lander; SmolLM2 Program at Boolean purity 0; node 1 memory requests trimmed
CHECKPOINT none (10:35Z) [open] 3:35 AM PDT: node 1 idle GPUs routed (proofs' CPU staging off its borrow cap, circuits to fill node 1); slot d 3:30 check on ecf7d9e36; #667 at 5:00
CHECKPOINT none (10:22Z) [open] 3:22 AM PDT: 3:30 slot d stack ecf7d9e36 confirmed valid; 41 PRs open, ~8 expected at 4:50; three node 1 trains land ~4:05
CHECKPOINT none (10:04Z) [open] 3:04 AM PDT: 2:05 check closed (all owners reported); node 2 Commit cap 40 min approved; node 1 held-idle 86.6% pushed to circuits
CHECKPOINT none (09:49Z) [open] 2:49 AM PDT: T496R failed on #496 fences fixture; IR rebuilt alone on main, lander node 1 + slot d 3:30 hedge; #496 fix with PR captain
CHECKPOINT none (09:33Z) [open] 2:33 AM PDT: IR prep check r20261001-091202-7aa6 running on slot d; all 34 open PRs scheduled; inbox empty
CHECKPOINT none (09:21Z) [open] 2:21 AM PDT: 2:05 check done; rulings on IR-before-T647, slot d through GEMM windows, proofs confirming run; inbox empty
CHECKPOINT none (09:01Z) [open] 2:00 AM PDT: node 1 ~4/8 GPUs active (grid Commits), 2 empty; node 2 only GPU 7 (PoUS timed) busy, 3 empty, rest proofs in CPU phases; staging 20 checkpoints to node 2 is the lever; full round at 2:05
CHECKPOINT none (08:45Z) [open] 1:45 AM PDT: node 2 ~4/8 busy after Gemma-2 cancels; node 1 0% (4 empty, 4 grid Commits planning, 29 grid jobs in dispatcher); infra asked whether pacer holds them and to confirm proofs' node 2 slots
CHECKPOINT none (08:31Z) [open] 1:30 AM PDT: 2/16 GPUs busy (both PoUS on node 2); node 2's five hopeless Gemma-2 Commits still running 10 min after circuits' cancel ask, infra pushed; node 1 has 5 empty GPUs, grid rows starting (Qwen3-30B), compute accounting filling
CHECKPOINT none (08:17Z) [open] 1:14 AM PDT: 1/16 GPUs busy; 10 Gemma-2 Commits hold GPUs at 0% (planning/hashing); circuits asked to pack 2/GPU and explain an unpacked node-1 Commit after its rule; PoUS asked to use node 2 GPU 7; node 1 GPUs 1,2 and node 2 GPU 1 empty
CHECKPOINT none (08:00Z) [open] 12:59 AM PDT: node 2 GPUs 1,3 busy, 7 pinned to PoUS, 4-6 Commits restarting onto 90-min cap; node 1 still 0% (5 Commits hashing until ~1:20-2:45 AM, GPUs 0,2 free for compute accounting's 1 AM fill); infra +7h: delivered 19%/44%
CHECKPOINT none (07:46Z) [open] 12:44 AM PDT: both nodes 0% busy; node 2 GPUs 0-3 empty with work queued (infra asked to admit); node 1's 5 Gemma-2 Commits idle on GPU 61-72 min (circuits asked phase/ETA, pack two per GPU); PoUS granted node 2 GPU 7
CHECKPOINT none (07:28Z) [open] 12:28 AM PDT: both nodes ~0% busy; node1 GPUs 0,2,3 given to compute accounting untimed; node2 4 held by Commits in prep, 4 empty pending infra core reservation
CHECKPOINT none (07:14Z) [open] 12:14 AM PDT: node 2 7/8 empty 40 min after go, infra pushed on core reservation + Commit routing; PR goal now 0 by 7:50
CHECKPOINT none (06:58Z) [open] 11:57 PM PDT: node 1 5 GPUs held by Gemma-2 Commits in CPU phase, circuits asked to pack; node 2 6 empty, prover cores being reserved
Infra +7 h (11:56 PM PDT): (a) MISS: since 7:40 PM PDT, 49 of 137 jobs on node 2 went through `research run --queue` with a question (all `kind=adhoc`); the other 88 were 70 fill-queue drops and 18 `research run` calls without `--queue` (4 of them my hourly backups). On node 1, 6 of 36 did (4 `build`, 2 `adhoc`); the other 30 were 10 queued without a question and 20 without `--queue`, 11 of them `check` runs. Node 1's Kueue submissions are not counted, because the research user can't read the k3s kubeconfig. (b) HIT: node 1's disk is at 31% (1.5 of 4.9 TB). (c) MISS: over 03–06Z, node 2 delivered 56% of its leased GPU time (7,424 of 13,274 GPU-s) and node 1 15% (4,778 of 31,412), 27% combined. Node 1's leases at 04–05Z held about 3.6 GPU-h an hour and delivered 12–15% of it.
