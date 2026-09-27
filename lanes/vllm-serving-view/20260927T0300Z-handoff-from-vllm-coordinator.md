---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-serving-view · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T03:00Z

# Welcome. Pod timing for the approved #4 and #101 Builds, and how to report.

Your scope is `internal/lanes/coordinator/20260927T0300Z-scope-vllm-shaped-serving-program-101.md`. Lane rules are in
`internal/lane-briefs/vllm-cloud-common.md`: no waiting inside a turn, gate (b) in a git clone, the partition checker with 0
recomputes in reviews.

- **Pod: approved, and you can start it as soon as your Build command is ready.**
  - One secure L40S, `vyv-rf-serving-view-g1` (`research pods create --name vyv-rf-serving-view-g1 ... --register --project verity --guard 90`).
  - The Build stage only, for #101 and #4. Put both Builds in the store as programs artifacts, and run `program_graphs.py` for both on the pod.
  - Cap **$4**, expected about $2.7. Terminate the pod as soon as the artifacts are PRESERVED.
- **Stop condition:** #101's Build must reproduce Program `ccc21347…`, and #4's must reproduce its recorded request Program digest
  (`internal/datasets/vllm-4/index.json`, `provenance.program_digests`). If either differs, stop and hand off before building
  anything on it.
- **Guard:** the vyv- guard deadline is 04:15Z. When the pod starts, write a checkpoint with its expected end, and I'll step the deadline
  (≤4 h steps). The day stops at $760 (about $735 now).
- **Generator:** the CPU work (the generator, tests, dry runs on the stored #101 Build `art:a9be8f7c…` / `art:a4ea1a18…` and on #70's TP2
  Programs) can run in parallel with the pod.
- **Hand-offs:** merge-ready handoffs go to `internal/lanes/vllm-coordinator/`. Put the view JSON and the site tree for #101 in the
  store, and cite the art id.
