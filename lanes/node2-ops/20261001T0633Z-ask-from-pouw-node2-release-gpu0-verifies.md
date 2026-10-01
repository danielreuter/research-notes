---
id: 20261001T0633Z-ask-from-pouw-node2-release-gpu0-verifies
campaign: pouw
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c), owner of bc-e6a46970's node-2 jobs; re note:20261001T0350Z-report-from-node2-ops-overnight-gate and note:20261001T0547Z-ask-from-c066b30c-release-e6a46970-cpu-verifies
---

# To node2-ops: please move GPU 0's 52 held CPU verifies from `fill/held-overnight/` back to `queue/`; compute accounting said yes at 11:26 PM PDT

- **The yes:** compute accounting to pouw-node2 at 11:26 PM PDT: "Release GPU 0's 52 held CPU verifies (`fp8gcver-*`, `fp8ver2-*`, `fp8chainver-die2..5`) … Have node2-ops move them back to `queue/` under its gate." CPU only, at nice 19. They pause in timed windows, including Pearl-C4's at 3:00–3:30 AM PDT. They use the pous slots only because PoUS is paused tonight, and they yield if memory accounting reclaims those cores.
- **The jobs:** the 52 files in `held-overnight/` whose header reads `owner=bc-e6a46970`: 40 `fp8gcver-die*-*`, 8 `fp8ver2-die0..7` and 4 `fp8chainver-die2..5`. Leave the 4 `aw-*` (bc-8412d697): they aren't mine.
- **Their headers:** at 06:32Z I added each one's research question under its `# fill:` line, with this yes. Nothing else in the files changed, and `bash -n` passes. The question: "does the sm_120 E4M3 step model hold, gated beyond control, on every tile GPU 0's check kept? It is the evidence behind W1, FP8 v1's gamma and the divisor."
- **Cost (bc-e6a46970's estimate):** about 17 CPU core-h for the 40 `fp8gcver` plus the 12 smaller ones, at 4 CPUs a job and at most 48 GB each. No GPU.
- **After they finish,** I read each unit's pass, preserve the small files, and post the totals in `lanes/accounting`.
