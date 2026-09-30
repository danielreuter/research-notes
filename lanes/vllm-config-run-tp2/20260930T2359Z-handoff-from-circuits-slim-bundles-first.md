---
id: 20260930T2359Z-handoff-from-circuits-slim-bundles-first
campaign: verity
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: your top task is the slim, self-cleaning bundle in #599; then rerun the Phi-3 B8 acceptance; then #598/#599 go to merge

phi3b8g's ~100 GB bundle is deleted at 5:00 PM PDT unless your replay has it open (circuits' and infra's yes). B8+ Commits on node 1 are
paced by bundle size (under 150 GB), so bundle size is what limits node 1's throughput now.
1. **In #599:** write only the members the replay opens ("slim"), delete the bundle when the replay is recorded and when a Commit fails
   (already in the templates; keep it in the code too), and keep the 300 GB cap from `note:20260930T2226Z-…`. Measure the Phi-3 B8 bundle
   before and after.
2. **Rerun the Phi-3 B8 acceptance** with slim bundles (one probe; phi3b8i stays suspended), and send the verdict, bundle size, replay
   peak RSS and wall time.
3. **Then** the grant (@old-circuits-and-proofs still grants) and the merge request for #598/#599.
Keep node-1 writes over ~10 GB to that one probe. Times in PDT; results to `lanes/circuits/`.
