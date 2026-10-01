---
id: 20261001T0205Z-reply-from-old-accounting-full-backlog
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: old-accounting (bc-b729c175)
---

# Old-accounting's full open backlog, in plain language (as of 6:50 PM PDT, 30 Sep)

For compute-accounting (bc-e90634dd), to turn into Daniel's one doc. Sources: `notes.md`, `archived.md`, node 2's `server.md`, the
worker status files, `lanes/accounting/` replies since about 5:45 PM PDT, and the open-PR list (148 open). Plain terms used below:
γ is the most a cheating prover can save, as a share of the honest work, and the goal is γ ≤ 1%. "Rated" means the independent
assessor (bc-d7d4b0d1) has graded the assumption from A (best) to D (unusable). "Slowdown" is the proved run's time over plain
FP8's time at the same shape; the goal is toward 1×. "Node 2" is the 8-GPU RTX PRO 6000 server; "fill" is preemptible background
work on it, paused during timed windows. "Window" is a timed whole-node run. `-h1`, `-h2` and `-h3` are the hashing formats the
proof uses to commit to a matmul's outputs, `-h3` the strongest and costliest; the served path uses `-h2`. "Pins" are Lean theorem
statements recorded in the proof store; "GO" is the red-team's (bc-22298e90) approval of a statement.

Format: id or short name | what it is | owner | status | last touched | blocked on | keep/drop view

## γ ≤ 1% security: FP8 (v1, v2-hot)

v1 headline | v1 is the only FP8 design whose cheating saving is under 1% (0.519% with packed storage), checked against all 4,180 known fast-matmul schemes and rated B | bc-3006c44a | done-but-unmerged (its code rides the next merge train) | 5:30 PM PDT | the merge train | keep: the served MVP's γ rests on it
v1 register-copy check | a 40-second run testing whether copying values through registers lets a cheater beat v1 (the worst case would be 1.28%) | bc-3006c44a | queued | before 6:00 PM PDT | a free slot on node 2 | keep: cheap, and the one open threat to v1's headline
v2-hot fix (2) | a GPU test of seven "late-start" cheating patterns that decides whether v2-hot (a faster v2 variant) can do without an extra charge; its charged version already fails (γ ≥ 0.951% packed) | bc-0f3f8a2f | running since 6:35 PM PDT (about 25 GPU-min, then about 2 CPU-h of judging) | 6:41 PM PDT | nothing | keep: small and decisive; the assessor's samples suggest it fails, and then v2-hot is parked
v2-hot padded re-search (a) | a 48 CPU-hour search on padded matrix shapes for v2-hot's one remaining open condition, paused during timed windows; ends about 9:45 PM PDT to midnight | bc-0f3f8a2f | running since 6:02 PM PDT | 6:41 PM PDT | stops at once if fix (2) fails | keep only while fix (2) is alive; drop the moment it fails
v2-hot charge searches | the searches that measure v2-hot's extra charge (Δ) and keep raising its lower bound, continuing through all 256 steps of the computation on a VM's CPU | bc-3006c44a | running | 6:00 PM PDT | nothing | drop: the charged route is already dead, so a higher floor changes no decision
v2-hot 16,384-wide run | a GPU 3 run on wider units that would let v2-hot's figure at 16,384³ be cited | bc-0f3f8a2f | parked (on hold, nothing written or queued) | 6:41 PM PDT | fix (2) passing, then a new order | drop unless fix (2) passes: Daniel's shape is 8,192³
v2-hot 65,536 CPU run | the assessor's queued CPU run closing v2-hot's long tails at very wide sizes; queued 2:34 PM PDT, not started by 6:00 PM PDT | bc-d7d4b0d1 | queued | 6:02 PM PDT | the queue-keeper (bc-829aa649) | drop: wrong shape, and v2-hot fails at 8,192³ unless fix (2) passes
v2-hot no-charge lemma | the written argument that v2-hot needs no extra charge, drafted and built, restaged only if fix (2) passes | bc-b58c6093 | waiting on fix (2) | 6:02 PM PDT | fix (2) | keep, conditional on fix (2)
v2-hot ratings | the assessor's rating of the padded re-search's result | bc-d7d4b0d1 | waiting on (a) | 6:02 PM PDT | (a) finishing | keep only if fix (2) passes
v1-hot | a hot variant of v1, its proofs staged and reviewed (100 pins), kept in reserve | bc-b58c6093, bc-876ca543 | parked | 6:03 PM PDT | Daniel's adoption call | keep parked: costs nothing while idle
W1 off-pipe pricing | every FP8 design's weakest rating is C because some sm_120 instructions (texture filtering, L2 and bulk reductions, predication, a full instruction inventory) were never priced; about 30 GPU-min of microbenchmarks could lift it to B | bc-9221952f (Grok 4.7 worker, by Daniel's 6:00 PM PDT change from GLM 5.3), rated by bc-d7d4b0d1 | waiting on the writer (spec posted 6:37 PM PDT; no partial code exists) | 6:37 PM PDT | bc-9221952f starting | keep: it caps "firm under rated assumptions" for every FP8 line
ε₈ ruling | an assessor ruling on one of the small error terms in the FP8 bound | bc-d7d4b0d1 | waiting on the assessor | before 6:00 PM PDT | unknown | keep: part of rating the bound
int8-Strassen replay | the assessor's replay of a known integer fast-matmul trick against the bound | bc-d7d4b0d1 | queued | before 6:00 PM PDT | a free slot | keep if small: it tests the bound directly
plain v2 re-check | re-checking one of plain v2's assumption-table entries on padded shapes (the job is staged, not queued) | bc-0f3f8a2f, bc-d7d4b0d1 | parked | 6:12 PM PDT | nothing | drop: plain v2 is rated D and over 1%; compute-accounting refused it as filler
finer staircase floors | a finer CPU job for the per-row lower bounds on fast-matmul cost, held | bc-d9842080 | parked | 5:27 PM PDT | nothing | Daniel decides: useful only if it moves v1's or v2-hot's verdict
assumptions-table lead | the table's lead still reads v2-hot at 0.689% charged, which the full-catalogue result has overturned | bc-69c09d42 | waiting on bc-69c09d42 | 6:03 PM PDT | nothing | keep: Daniel's doc must not show a dead figure
beacon on the served path | the drand beacon is rated A for audits, but served runs can't cite it until the vLLM path passes verified rounds | bc-e90634dd | waiting | 1:36 PM PDT | a served-path beacon test | keep

## γ ≤ 1% security: FP4 (Pearl-C4)

FP4 TT_OUT grant | the assessor granted FP4's core assumption at C at 6:36 PM PDT, for NVFP4 widths of 4,096 and up, so FP4's γ figures (0.71732% and 0.61102%) can come off hold | bc-d7d4b0d1 | done | 6:36 PM PDT | nothing | keep
FP4 small widths | FP4 widths 128–4,095 stay ungranted until the verifier enforces the per-width credit discount (B-OVF) | bc-71c6ab78 (porting to #580) | running | 6:40 PM PDT | GPU 5's port to #580 | keep: closes FP4's scope and lifts the panel's small-n flag
FP4 γ Lean set | FP4's γ figures, already written in Lean (59 pins), merge once the fix's Lean definitions are reviewed | bc-876ca543 | waiting on review | 6:03 PM PDT | bc-22298e90 | keep
B-OVF strong search | an 8 CPU-h search at widths 256 and 512, one of the assessor's two open FP4 conditions | bc-a8466279 (queued by bc-2aa33ad8) | queued since 3:22 PM PDT | 6:10 PM PDT | a CPU slot; it imports torch, so the MKL warm-up check applies | keep: needed for small-width FP4
V-EX coverage | a node-2 job checking that honest FP4 tiles on real models never trip the cap (112 tile results so far on the 3B capture), the other open condition | bc-a8466279, captures from bc-f5bf55c8 | running since 4:44 PM PDT | 6:28 PM PDT | nothing | keep: honest-coverage evidence behind FP4's rating
rotated-weights re-read | two FP4 figures (the 10× factor's honest cost, and zero voluntary rows on 3B and 7B) were measured on unrotated weights and should be re-read on rotated ones before anyone cites them for a registered model; CPU only | bc-a8466279 | waiting on an order | 6:02 PM PDT | compute-accounting | keep: cheap, and keeps FP4 citations honest
layout-after-salt break | a possible cheat on narrow weights (worth 0.5–1.2 points of γ) that the assessor found; the domain lane is checking it | bc-a8466279 | running | before 6:00 PM PDT | nothing | keep: a live threat to FP4's rating
70B FP4 coverage | a CPU-only fill job (version 4) for 70B honest coverage | bc-f5bf55c8 | waiting on bc-2aa33ad8 to queue it | 6:01 PM PDT | bc-2aa33ad8 | Daniel decides: supports 70B only
V/O + head-interleave rule | Daniel's 5:52 PM PDT ruling written into #580: these keyed weight transforms register only inside the 8-block rotation, with tests | bc-71c6ab78 | done-but-unmerged (#580 at `639128c8`, 1,691 tests pass) | 6:37 PM PDT | #580's merge | keep
70B must fold γ | 70B registrations must fold γ into the cast | bc-6289d8b0, bc-a8466279 | done-but-unmerged | 6:04 PM PDT | #580 | keep
approved-weights debits | two of the approved-weights lane's CPU fill jobs (adversarial-activation debit, 19 of 27 cells; real-activation debit with γ folded, 5 of 6 chunks) | bc-8412d697 | running, slowly | 6:00 PM PDT | nothing | Daniel decides: they finish a report section, not a headline
MXFP4 | the other 4-bit format, rated D on honest coverage | bc-d7d4b0d1 | parked | Sep 30 morning | nothing | drop for now

## Lean proofs

RowSeed (M3) | the Lean proof that per-row random seeds are safe: 27 of 28 statements GO; the 28th now names its per-row draw condition as an assumption (Daniel's ruling, restaged 6:27 PM PDT) and is back for review | bc-5382063c (driven by bc-824e54a2), reviewer bc-22298e90 | waiting on the red-team's re-GO | 6:34 PM PDT | bc-22298e90 | keep: needed before `-h3` can be decided
RowSeed replay audit | the kernel replay check of RowSeed, deferred because the Lean VM is short of memory | bc-5382063c | parked | 6:34 PM PDT | memory (could run on node 2) | keep: must pass before RowSeed is pinned
D-NF pins review | the red-team's GO on the FP4 domain-rule pins, now that their kernel replay passed (5:59 PM PDT) | bc-22298e90 | queued | 6:06 PM PDT | nothing | keep
D-NF replay evidence | the replay's outputs sit in the store's `fill-out/` and still need putting into the evidence store | bc-824e54a2 | waiting on bc-824e54a2 | 6:06 PM PDT | nothing | keep: evidence custody
FP8 twins to the store | 182 FP8 γ pins (in-loop twins, chain-only, v2's chain cap), red-team GO, waiting on the M2a store merge | bc-876ca543 | done-but-unmerged | 6:03 PM PDT | the next Lean store merge | keep
v2-hot Lean (M2b) | v2-hot's protocol proof (132 pins) and its node-2 Lean build | bc-824e54a2, bc-876ca543, bc-b58c6093 | parked (held) | 6:03 PM PDT | fix (2) and v2-hot's grant | drop if fix (2) fails
new-crypto Lean workers | the new-crypto coordinator's other workers: the store merger (bc-3cdbf3c1), FP4 staging (bc-ae19a858), the forming-credit and certificate proofs (bc-5a715b19), Lean integration (bc-7a7109a0); none holds a goal-critical job | bc-824e54a2 | waiting on grants and reviews | 6:01 PM PDT | the items above | keep only what feeds a pin above
monotonicity lemma | a small lemma for BF16-widened activation rows, queued after TT_OUT rev2 | bc-5a715b19 | queued | Sep 30 | TT_OUT rev2 | Daniel decides
Lean organization and CI | the plan for repo-wide Lean layout and CI | bc-79934c4e | waiting on the coordinator's CI answers | Sep 29 | the research coordinator | Daniel decides: not on tonight's path

## Served slowdown toward 1× (MVP, hashing, windows)

goal 2: window 7 totals | window 7's served run with graphed FP8 in the run, verified at 6:37 PM PDT (prefill and decode accepted, both tampered controls rejected): decode 3.402× over graphed FP8 and 1.263× over eager FP8, prefill 1.617×; it serves v1 only, so its γ is v1's 0.519% | bc-dd22acf8, bc-ccd30e80 | done | 6:37 PM PDT | nothing | keep: tonight's goal (2), met
goal 3 row chain | publish the like-for-like graphed decode row beside the eager row on verity/pouw-overhead, due 11:40 PM PDT: appended as attempt 109 (decode 3.4024× over graphed FP8, 1.2629× over eager, prefill 1.6174×) and labelled at 6:42 PM PDT; labels pushed to the store at 6:43 PM PDT, so only @console's next poll remains | bc-2aa33ad8 (done), bc-824e54a2 (done), @console | running | 6:44 PM PDT | @console's next poll | keep: tonight's goal (3)
#610 verify | the cheaper `-h2` hashing form (the "s" form) plus the decode trims: both prefill passes accepted; decode and the must-reject controls due about 7:15 PM PDT | bc-b139c29c | running | 6:36 PM PDT | nothing | keep: feeds window 8
window 8 | the next timed served run, carrying the trims and the "s" form if #610 verifies by 9:30 PM PDT; its row replaces window 7's if verified by 11:40 PM PDT; READY line due 9:10 PM PDT | bc-b139c29c, bc-ccd30e80 | queued | 6:39 PM PDT | #610's verify | keep: moves decode toward 1× (untimed decode about 3.8× → 3.3× over graphed FP8)
6:30 PM PDT repeat | a repeat timed run that doubles as the A/B test for running CPU fill beside timed windows; may start as late as 7:00 PM PDT | bc-2aa33ad8 | waiting on window 7's verify workers (148 were running at 6:23 PM PDT) | 6:23 PM PDT | window 7's verify jobs clearing | keep: decides whether CPU fill can share the node without biasing timings
divisor window | a 10–15 min timed window (about 0.25 GPU-h) to confirm the honest baseline is our own plain FP8/FP4 GEMM, which would raise FP8 prefill slowdowns about 2.6%; no γ changes | bc-2aa33ad8 (harness bc-0de2d624 staging it) | waiting on compute-accounting's yes | 6:35 PM PDT | compute-accounting | keep: makes every slowdown figure honest
decode divisor gaps | timing each library's best as a dependent chain at decode, and failing a run that drops the frozen FP8 names (#491); code and CPU only | bc-0de2d624 | queued | 6:12 PM PDT | nothing | keep
whole-step graph | recording the whole proved decode step once as a CUDA graph and replaying it, which removes per-launch overhead; planned for tomorrow's first free window | bc-ccd30e80 | queued | 6:39 PM PDT | a free window | keep: the next big decode lever
`-h2` served flag and lint | the served-path switch, a vLLM size lint and an untimed served run for the "s" form | bc-b139c29c | queued | 6:36 PM PDT | #610 | keep
`-h2` hash bench | an untimed screen of `-h2` hashing cost at all 13 panel shapes on every die (about 8.7 GPU-h of fill) | bc-7442ca43 | running as fill since 3:43 PM PDT (status not refreshed since 4:35 PM PDT) | 4:35 PM PDT | nothing | Daniel decides: the biggest GPU fill tonight; it maps hashing cost but doesn't move a headline by itself
attempt 104's missing row | @console's publisher omits attempt 104's decode row although its labels are on the store; asked why | @console | waiting on @console | 6:04 PM PDT | @console | keep: small, panel correctness
hashing forms on the served path | GPU 1's other hashing forms on the served path, kept `-h1`-only in a draft | bc-dd22acf8 | parked (draft #600) | 2:07 PM PDT | nothing | drop
#578's deferred schedule | the vLLM migration's deferred stream schedule, never profiled or timed | bc-f4e8ae34 | parked | 6:01 PM PDT | nothing | Daniel decides: could cut decode time, unmeasured

## Node 2 and infrastructure

goal 1: canary and scheduler | the canary landed within spread on a like-for-like baseline (−0.08%; verdict 6:20 PM PDT), so node 2 stays on the central scheduler; compute-accounting is closing it with @infra | bc-2aa33ad8, @infra | done | 6:22 PM PDT | nothing | keep
CPU fill and CPU lending | background CPU work on CPUs 0–47 and lending CPUs 48–95 to other lanes, kept on one memory bank, judged by the 6:30 repeat | bc-2aa33ad8 | waiting on the 6:30 repeat | 6:23 PM PDT | the repeat | keep: idle CPUs, but only if timings stay clean
canary custody | the canary's records were made without a backup copy; bc-824e54a2's watcher preserves its outputs once staged | bc-2aa33ad8, bc-824e54a2 | running | 6:01 PM PDT | nothing | keep: evidence custody
GPU 3 custody | GPU 3's eight unbacked runs are now preserved | bc-0f3f8a2f | done | 6:41 PM PDT | nothing | keep
MKL race check | every lane checks its CPU code for a race in torch's math library (MKL) that can corrupt the first parallel call, and adds a one-line warm-up; two torch CPU fill jobs (bc-f5bf55c8, bc-a8466279) checked first | all lanes | running | 6:10 PM PDT | lanes replying | keep: it can silently corrupt verifier results
GPU 2's node-2 access | GPU 2's VM lost node-2 access, which pushed the canary behind window 7 | bc-7442ca43, @infra | waiting on @infra | 6:00 PM PDT | @infra | keep if GPU 2 has real work; else drop
GPU backlog watermark | compute-accounting's queue-keeper keeps at least 12 GPU-h of approved work ready, plus the node-1 overflow list | bc-829aa649 (for bc-e90634dd) | running | 6:00 PM PDT | nothing | Daniel decides: his rule says an idle GPU beats a padded one
ranked slices | the RTX PRO coordinator owed ranked slices of overnight work (the first 10 GPU-h by 4:30 PM PDT) | bc-2aa33ad8 | unclear whether delivered | 3:43 PM PDT | nothing | keep only real γ or slowdown work
node 2 hard stop | node 2 stops at 7:55 AM PDT on 7 Oct; results must be preserved before then | everyone on node 2 | running | 6:28 PM PDT | nothing | keep
merge train | #449, #548, #534, #556 and #602 go to the next merge train together | research coordinator | queued | 6:00 PM PDT | the next train | keep: lands v1's and FP4's code
#449 follow-up | a fix raising the kernel-name limit in the CPU test stub, held until #449 lands | bc-9914c188 | parked | 6:03 PM PDT | #449 on `main` | keep: small
Nebius spend | about $96 of root's $450 overnight ceiling (rate inferred, no bill visible); RunPod $0 of the $200 cap (5:19 PM PDT) | bc-824e54a2, Verity root | running | 5:19 PM PDT | nothing | keep watching

## Old-accounting's own items (bc-b729c175)

advisor relay | copy replies from the six VMs that can't push to research-notes (via this outbox) into the lane, and wake idle workers with pointers to compute-accounting's orders every 10 minutes | bc-b729c175 | running | 6:42 PM PDT | RESEARCH_NOTES_TOKEN for those VMs | keep until the tokens arrive, then drop
token broker rollout | every PoUW lane moving to Verity's GitHub token broker and confirming it in its status file | bc-b729c175 | running | Sep 30 afternoon | lanes confirming; the broker covers only the verity repo | keep: stops token leaks
restructure | Daniel's 5:52 PM PDT ruling that every old PoUW worker takes orders only from compute-accounting; handover sent at 6:00 PM PDT and acknowledged by every worker read here | bc-b729c175 | done | 6:00 PM PDT | nothing | close the checkbox
overnight objectives | Daniel's Sep 29 overnight objectives (three morning deliverables) | bc-b729c175 | stale | Sep 29 | nothing | drop: tonight's three goals replace them
decisions log and workflow inputs | the decisions-taken log and seven brittle spots kept for the next workflow update | bc-b729c175 | parked | Sep 29 | the next workflow update | Daniel decides
colleague handoff | the POUS and PoUW colleague overview in Notion, current to 8:30 PM PDT Sep 29 | bc-d3651a9e | waiting on Daniel's edits | Sep 29 | Daniel | Daniel decides
Slack coordination | Slack tooling (#592) with Daniel's seven handles; a fresh `groups sync --apply` makes it live | bc-838f9732 | done-but-unmerged | Sep 30 | a sync run | Daniel decides
console panels | all 11 panels published to /admin/live and refreshed every 5 minutes | bc-26712550 | waiting on Daniel to confirm they render | Sep 30 | Daniel | keep
kernel tooling | 326 tried techniques and 251 sm_120 gotchas published; #590 (runs publish their own records) to be handed to the harness owner | bc-1a23b70c | done-but-unmerged | 6:05 PM PDT | #590's handoff to bc-0de2d624 | keep #590; the rest is done
vLLM integration API | the vLLM linear-site API (#567) and its four-step migration, all green, waiting for a train | bc-f4e8ae34 | done-but-unmerged | 6:01 PM PDT | #567 merging | Daniel decides: plumbing, moves no number
deployment audit | #472 merged; #473 (PoUS band certificate) and #471 (ncp-v2, stacked on #433) need recorded checks this VM can't run | bc-f9184c6e | waiting on a recorded check | 6:03 PM PDT | a VM with `research run` | Daniel decides
Pearl-C on vLLM (#462) | the CPU half of Pearl-C for the vLLM option, paused; its 4.6 MB fixture needs registering | bc-9914c188 | parked | 6:03 PM PDT | a machine with store access | drop tonight
H100 clean-up capture | the H100 run was withdrawn and its capture notes handed to the RTX PRO coordinator | bc-e4a2abca | done | 5:59 PM PDT | nothing | close the checkbox
fallback designs | counting-proved FP8 designs (about 625× and 460× slowdown with hashing) kept as the proven fallback; hardness-shaped matrices NO-GO at 8,192³ | bc-b729c175 | parked | Sep 29 | nothing | keep parked as insurance; no work

## PoUS and network (handed to memory-accounting bc-15ada664 and network-accounting bc-ecea50f6)

POUS band MVP | the PoUS-only harness (#474) and two vLLM PRs (#460, #463), paused by Daniel; the red-team's NO-GO on two small fixes is recorded | bc-13eada34 | parked | Sep 30 | Daniel resuming PoUS | drop tonight
efficient PoUS crypto (P2) | P2 proved in an abstract model at 23.7 GB/s on an L40S, but its new assumption isn't accepted | bc-61023cab | parked | Sep 30 | the assumption decision | drop tonight
band pins on `main`? | notes say the band pins (#428) and P3's pin (#431) landed via Lean train TLR, but bc-f9184c6e says neither is on `main`; both PRs show open | bc-87c3b40e, bc-4b3abaed | waiting on a check | 6:03 PM PDT | someone checking `main` | keep: a five-minute check
band v6 P3 rounds | a Lean follow-up for the band scheme, ready locally | bc-87c3b40e | parked | Sep 30 | PoUS paused | drop tonight
PoUS red-team | the red-team's PoUS Lean reviews, every staged set GO so far | bc-22298e90 | waiting on new sets | Sep 30 | nothing | drop tonight (its PoUW reviews above are keep)
public-encoder variant | a PoUS variant with a public encoder, milestone 1 proved at k = 111 | bc-c0ee31ee | parked | Sep 29 | nothing | drop tonight
PoUS problem statement and trusted layer | the `pp` and ε bounds are still open; the trusted layer holds 46 pins | bc-15ada664 | parked | Sep 29 | PoUS paused | drop tonight
network timing channel | timing-channel Lean (#461) and the warden reference (#326) both landed | bc-6b78649f | done | 3:43 PM PDT | nothing | close the checkbox
resource ontology | the physical–logical resource vocabulary, decided at defaults; its Glossary edit lands with the first resource-accounting code | bc-e79791ab | parked | Sep 29 | first resource code | drop tonight
spot-check theory | sampled-proofs theory extracted to Lean, all on `main` | bc-e7e2bf3a | done | Sep 29 | nothing | close the checkbox
sampled-proofs circuit | the PoUW circuit is on `main`; #372 kept for a rebase, #380 and #391 in the proofs plan | bc-75d1b678 | parked | Sep 29 | proofs plan | drop tonight
composable vLLM options | options on `main`; the PoUW circuit gate (#367) held by root | bc-23d60f13 | parked | Sep 29 | root | drop tonight
errored PoUS proofs | five Lean lanes errored with partial work: DenseMeets pilot (bc-6dc0937d), P3 inverse-query decode (bc-802bddf4), ChainExPostFacto (bc-8bd87c53), dense concrete-H (bc-35b053cc), band v6 pr_EvR (bc-32004ac6) | bc-15ada664 | parked (half-done) | Sep 29 | PoUS resuming | drop tonight
other parked PoUS | POUS vLLM integration (bc-e64762ea), P3 primitives (bc-b8c188a5, superseded by the band), A2/A5/A7/M1Meets, NVFP4 scale flatness (bc-b7cd617f, stopped), the research-notes coordinator channel, campaign notes in the public repo | various | parked | Sep 29 | nothing | drop

## Open PRs (verity; 148 open)

#449 / #548 | Pearl-C's FP8 scheme and kernel, and Pearl-C4 (FP4) on top, green | bc-9914c188, bc-71c6ab78 | done-but-unmerged | 5:01 PM PDT | next merge train | keep
#534 / #556 | FP4 domain rules and the base-split fix, green | bc-a8466279 | done-but-unmerged | 5:16 PM PDT | next merge train | keep
#602 | drand quicknet as the beacon, rated A | bc-a8466279 | done-but-unmerged | 5:33 PM PDT | next merge train | keep
#580 | Pearl-C4's verifier enforcement and registration rules | bc-71c6ab78 | running | 6:32 PM PDT | the B-OVF port | keep
#596 / #593 / #610 | served `-h2` with CUDA-graph decode; the trims; the "s" form | bc-ccd30e80, bc-b139c29c | done-but-unmerged (#596's merge request filed) | 5:46 PM PDT | after the Pearl-C chain | keep
#572 / #591 | `-h2` as a switch in the sm_120 pipeline (check passed, merge request filed); the "s" form's kernel | bc-b139c29c, bc-18346d9c | done-but-unmerged | 5:37 PM PDT | after the Pearl-C chain | keep
#555 / #549 / #547 / #544 / #541 / #537 / #533 / #532 / #510 / #475 / #468 / #464 | hashing-format and placement experiments behind the panel's numbers | bc-b139c29c | done-but-unmerged | Sep 30 | the research coordinator | Daniel decides: keep what the served path uses, close the rest
#567 / #573 / #576 / #578 / #585 | the vLLM linear-site API and its migration | bc-f4e8ae34 | done-but-unmerged | 11:11 AM PDT | #567 first | Daniel decides
#491 / #590 / #588 | the shared bench harness, self-recording runs, plain-GEMM baselines | bc-0de2d624, bc-1a23b70c, bc-6da61042 | done-but-unmerged | 6:30 PM PDT | the research coordinator | keep: they record runs honestly
#577 / #595 / #627 | the kernel-engineering skill and its rewrite; the lean-proofs skill | bc-1a23b70c, Verity root | done-but-unmerged | 6:39 PM PDT | review | Daniel decides
#507 / #545 / #492 / #570 / #543 / #529 / #525 / #530 / #451 | attacker searches, FP4 census, W1 price capture, FP8 and NVFP4 plain baselines, FP4 captures | bc-0f3f8a2f, bc-dbc19788, bc-e6a46970, bc-fb55a759, bc-36186951, bc-f5bf55c8 | done-but-unmerged | 6:31 PM PDT | the research coordinator | keep: the evidence behind γ and the divisor
#471 / #473 / #433 / #435 / #389 | ncp-v2 and the PoUS band certificate from the deployment audit, and the older NCP serving stack | bc-f9184c6e | waiting on recorded checks | 6:03 PM PDT | node 1 after tonight's trains | Daniel decides: off tonight's goals
#625 / #626 / #618 / #614 / #613 / #612 / #496 | cluster scheduler fix, cluster status, credential guard for git URLs, a wake check, the console publisher, a Slack norm, shared Nebius server code | @infra, Verity root | done-but-unmerged | 6:41 PM PDT | the research coordinator | keep #625 and #618 (a scheduler bug and a credential guard)
#600 / #589 / #564 / #540 / #462 | MVP drafts and earlier MVP steps | bc-dd22acf8, bc-9914c188 | parked | Sep 30 | nothing | Daniel decides: likely close
#474 / #463 / #460 / #428 / #431 | PoUS harness, vLLM decode kernels, PoUS pins | bc-13eada34, bc-87c3b40e, bc-4b3abaed | parked | Sep 30 | PoUS paused | drop tonight (check #428/#431 against `main`)
#494 / #453 / #332 / #436 / #295 | Nebius pings (never meant to merge), H100 capture, Pearl baselines, older PoUW benches | various | parked | Sep 30 | nothing | drop: close or leave
#240 / #359 / #303 | research-notes approach registry; process-design skill; README framing | bc-51d80f1e, bc-63c7f09e | waiting on CI / the next train | Sep 30 | the research coordinator | Daniel decides
vLLM sm_120 bindings (#565, #566, #582, #557, #546, #539, #535, #524, #523, #516, #515, #502, #487, #486, #480, #477, #476) | exact sm_120 kernel definitions for the vLLM path | vLLM sm_120 lane | done-but-unmerged | Sep 30 | review | outside PoUW's two goals
other lanes' PRs (#97–#459 flock, one-stage, research tooling; #598, #599, #601, #606, #611, #619–#624 vLLM replay and identity fixes) | work outside PoUW | other lanes | done-but-unmerged or parked | 5:56 PM PDT | their owners | not ours

## Pending asks to Daniel

rotate the notes-repo token | a GitHub token for the notes repo leaked into the RTX PRO coordinator's transcript about 5:30 PM PDT | Daniel (via @infra) | waiting on Daniel | 5:30 PM PDT | Daniel | Daniel decides: rotate now
store credentials for bc-2aa33ad8's VM | lets the RTX PRO coordinator push its own labels instead of relaying through bc-824e54a2 | Daniel | waiting on Daniel (asked 5:53 PM PDT) | 5:53 PM PDT | Daniel | Daniel decides
RESEARCH_NOTES_TOKEN for six VMs | lets six worker VMs push replies themselves instead of through old-accounting's outbox | Daniel | waiting on Daniel | 6:01 PM PDT | Daniel | Daniel decides
deploy website e984b46 | shows the eager decode row separately on the console | Daniel | waiting on Daniel | 4:54 PM PDT | Daniel | Daniel decides
NEBIUS key rotation | the Nebius service key leaked at least four times today in agent logs; Daniel said rotate later | Daniel (via @infra) | waiting on Daniel | 3:36 PM PDT | Daniel | Daniel decides
delete three models from node 1 | the circuits lane's proposal to free disk on node 1 | Daniel | waiting on Daniel | 6:00 PM PDT | Daniel | Daniel decides
`-h3` | whether the stronger hashing form `-h3` is allowed, after RowSeed's review | Daniel | waiting on RowSeed's re-review | 5:52 PM PDT | bc-22298e90 | Daniel decides
time model and dither | two open protocol choices from the assumptions table | Daniel | waiting on Daniel | 5:52 PM PDT | Daniel | Daniel decides
console renders | confirm the 11 published panels render at /admin/live | Daniel | waiting on Daniel | Sep 30 | Daniel | Daniel decides
Nebius budget alerts | raise the Nebius budget alerts | Daniel | waiting on Daniel | Sep 30 | Daniel | Daniel decides

## Promises owed

#610 verdict | decode and control verifies for the "s" form and trims | bc-b139c29c | running | 6:36 PM PDT | nothing | due about 7:15 PM PDT
6:30 repeat result | the repeat's value against the pilot's 1.8043×, its spread and the CPU load | bc-2aa33ad8 | waiting on window 7's verify workers | 6:23 PM PDT | verify workers | due after a start no later than 7:00 PM PDT
fix (2) verdict | v2-hot's late-start verdict | bc-0f3f8a2f | running | 6:41 PM PDT | nothing | due when judging ends (about 2 CPU-h after the GPU half)
window 8 READY | READY or BLOCKED line for window 8 | bc-ccd30e80, bc-b139c29c | queued | 6:39 PM PDT | #610 | due 9:10 PM PDT
goal 3 publish | the like-for-like row live on the console | @console | running | 6:44 PM PDT | @console's next poll | due 11:40 PM PDT
W1 results and rating | the off-pipe microbenchmark report, then a one-line rating and its effect on v1 | bc-9221952f, bc-d7d4b0d1 | waiting on the writer | 6:37 PM PDT | bc-9221952f | open, no time set
v2-hot charge final bound | the final lower bound on v2-hot's extra charge once both searches finish all 256 steps | bc-3006c44a | running | 6:00 PM PDT | nothing | owed, but see the drop view above
v2-hot restaging | restaging v2-hot's pins on the derived-charge form "within the hour" if that route is chosen | bc-876ca543 | parked | 6:03 PM PDT | a route decision | moot: that route is dead
