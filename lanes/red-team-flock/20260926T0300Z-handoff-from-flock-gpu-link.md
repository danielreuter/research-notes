---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:58Z
---

# Fp4 on the 5090: GPU selftests pass at 0bb25e8a

- **Evidence:** run r20260926-025307-9297, art:f1ee8a75. CPU and GPU selftests pass at 8 and 64 VUs.
- **Fix between 7b3ba797 and 0bb25e8a:** the device path copied the chunk chaining values into the host publics buffer
  even though Fp4 publishes none, and that host buffer was empty. It is now null when `n_cv` is 0. The statement and
  the verifier are unchanged.
