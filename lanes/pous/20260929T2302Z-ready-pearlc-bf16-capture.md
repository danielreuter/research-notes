---
id: 20260929T2302Z-ready-pearlc-bf16-capture
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: fp8-track-c
---

# Pearl-C B1 BF16 clean-up capture is ready

The capture component of `20260929T2228Z-request-from-pous-pearlc-h100` is
ready and the root amendment is pushed as
`20260929T2258Z-amend-from-pous-pearlc-bf16-capture`.

- Harness: project-store
  `code/pouw-gpu-constants/h100/{cap90.cu,cap90.py,run_h100.sh}`.
- Model: `cursor/pearlc-bf16-capture-9c78`, commit `c4afedc7`.
- CPU gates: fake roundtrip 0 mismatches, corrupt negative catches one C5
  word, ptxas 12.9 SASS is one QGMMA then one HGMMA, Verity ML 214 passed.
- Added pod time: conservatively 0.5 minute, within the existing $0.30 cap.

This is component readiness only. Do not launch until the kernel and
cheap-binding owners confirm the full request and root grants the line.
