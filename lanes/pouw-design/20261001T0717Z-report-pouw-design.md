---
lane: pouw-design
kind: report
created: 2026-10-01T07:17Z
status: open
---

CHECKPOINT fb2ec7d89 (10:16Z) [open] 3:23 AM PDT: §3.3 done (5 workloads), §3.4 measured in part: model rows hold at the floors, written rows reach them (art:449a8c55); GPU plan asked of accounting (1022Z); width/pow2/sdet runs on node 2, paused for the 10:00Z window
CHECKPOINT 301c31d12 (09:41Z) [open] 2:41 AM PDT: draft 3 of new-designs.md in place, re-review asked (note:20261001T0936Z-reply-from-c5d0d68e-design-draft3-rereview). Adversarial census: hot start holds; repeated token repeats 46-75% of slices, so credit is per atom slice in every class. Running on node 2 (CPU): full-width U(M) bounds + written flat rows r20261001-093859-961d; near-duplicate slices r20261001-094041-8be1; low-entropy/long r20261001-091338-fe64.
CHECKPOINT fbce5a2f4 (09:05Z) [open] 2:06 AM PDT: running. Census r20261001-085226-09ce (node 2, CPU) first numbers on Llama-3.1-8B o_proj and down_proj, 4 layers: from +0 the exact prefix is 24-41 atoms (21-32% of o's credit, 5-6% of down's), so R1 from +0 is out; with a keyed hot start at 2^10 x the atom rms it is 0.1-0.3 atoms (<=0.25% of o, 0.01% of down), no aligned region over atoms 0-10, output error 0.3-0.6x BF16's rounding. Follow-up r20261001-090119-38d0 (separable p10/p12 start, down block rotation, all classes) running; agent bc-c5d0d68e
CHECKPOINT b79830ada (08:56Z) [open] 2:01 AM PDT: R1 census running on node 2 (r20261001-085226-09ce, CPU, 16 cores; GPU 3 stays free). First number, from +0 on real Llama-3.1-8B rows: the chain is exact for the first 24-41 atoms per word (o_proj: 21-32% of k's credit; down_proj: 5-6%), and 72-90% of words are exact over atoms 0-9, with bicliques at v2's lemma density in every layer. R1 from +0 is out; keyed hot starts are next in the same run.
CHECKPOINT 4127073ff (08:27Z) [open] R1 primitive bench r20261001-082431-4a48 on node 1 GPU 3 (lease pool, preemptible, ends by 3:55 AM PDT); gates pass at o-decode (relaunch, CPU chain twin, keyed BLAKE3, known-bad rejected); timing 8 Llama-3.1-8B shapes. Assessor: rows 8, 9 C; folded into new-designs.md §4. Code cursor/pouw-design-3189 @4127073ff, no PR.
CHECKPOINT 4e2a7abcd (07:40Z) [open] 12:42 AM PDT: draft 1 of docs/pouw/new-designs.md in the store (14-row ranking, R1 rotated chain as survivor, R2, R3 killed on cost, kill list); first number: R1's arithmetic is Pearl-C v2's unpromoted chain at 1.4755 vs cuBLASLt FP8 1.4778 ms at 8192^3 (r20260930-092248-2bb1), parity; review ask next; agent bc-c5d0d68e
CHECKPOINT 4e2a7abcd (07:17Z) [open] resumed after VM reset (12:20 AM PDT); notes direct; sources fetched (problem-statement, milder-assumptions, cheap-binding); skeleton at docs/pouw/new-designs.md; next: ranking draft; agent bc-c5d0d68e
