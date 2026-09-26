---
lane: agkr-real-k
kind: report
created: 2026-09-26T08:06Z
status: open
---

CHECKPOINT d602c576 (08:39Z) [open] tip d602c576: K=2048 cell relaunched after 2 setup fixes (flock-gpu-link patch, CARGO_TARGET_DIR): ver r20260926-083651-9a59, prover r20260926-083700-e919 (pod tests: cargo 39+4, pytest 60 ok; flock-link selftest 49/49 at K=2048 and K=8192); gate at 1024 VUs running
CHECKPOINT efb71424 (08:31Z) [open] code efb71424 pushed (K param, real-K pins, commit pins = B-Ligero roots, A-route-a driver + cell.sh); K=2048 cell running: ver r20260926-082825-17ce on vy-agkr-real-k-ver, prover r20260926-082839-8d9e on vy-agkr-real-k-a100 (both US-MD-1 A100, no CPU stock there)
CHECKPOINT e3a2d81d (08:06Z) [open] started (agent bc-90879fa8-ea65-5d51-8e4d-ddeb832bf806, branch cursor/agkr-real-k-f806 from main e3a2d81d): survey done; A-GKR circuits uniform in K, flock-link K-generic (16-bit words); implementing K param + pins + A-route-a bench.cell driver
