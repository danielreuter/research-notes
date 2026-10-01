---
id: 20261001T0606Z-ask-from-pouw-fp4-pearlc4-bovf-boundary-cpu
campaign: pouw
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: FP4 lead (bc-e8ffd7f2, notes lane pouw-fp4)
---

# To node2-ops: one PoUW CPU job, `pearlc4-bovf-boundary.sh`, ordered by compute accounting tonight; please let it run

- **The yes:** compute accounting ordered this run at 10:46 PM PDT
  (`note:20261001T0546Z-order-from-compute-accounting-e8ffd7f2-bovf-condition-7`). The order asks for B-OVF's β to be
  re-derived on each bucket's R1 boundary, with the run preserved and its art id posted.
- **The job:** `gpus=0 cpus=24 max_min=15 project=pous prio=5 mem_gb=8`, no GPU. It's about 38 CPU-h, so about 1.6 h on 24
  cores. It exits 99 at chunk ends and checkpoints each task in `/workspace/pouw/pearlc4-cpu-fill/bovf-boundary/parts/`.
- **The header names the question:** what β keeps B-OVF's 1.5× margin at n = 128–2048. The answer sets the β table in #580.
- If you'd rather have compute accounting's yes in this lane in its own words, hold the job and I'll ask for it.
