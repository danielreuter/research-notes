---
id: 20261001T0908Z-handoff-from-circuits-build-speed-658-ready
campaign: circuits-build-speed
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-build-speed (bc-d2d56312-a75e-56c6-a829-45a5135a3752)
---

2:08 AM PDT: [#658](https://github.com/danielreuter/verity/pull/658) (`cursor/build-speed-4k-8c79` @ fbca39681) is ready (`research queue ready 658`) and needs the vLLM grant. It is a one-constant change in `pipeline/build.py`: `instances.json.gz` is written at gzip level 6, not 9, so its text is unchanged. On B1 4096/512 that cuts compression from 236 to 71 CPU s (r20261001-084923-9988), and the request derive's file write from 703 to 504 s under load (r20261001-074411-4cd5 vs r20261001-074411-7330). Program, correspondence, descriptor and instance-text digests are equal, and so is every reference-row digest (r20261001-074554-5e33 vs r20261001-074554-bd27). It merges cleanly with `main` and with #639. #639 is untouched at 1c2487ef8.
