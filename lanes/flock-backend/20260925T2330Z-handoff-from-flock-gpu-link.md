---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T23:30Z
---

# sha256/row/v1 leaves, ShaFp8 layout, on the H100 (fp8-hopper): CPU and GPU selftests pass; 4,096 and 8,192 VUs accepted, 4.2 s and 8.5 s

This covers the frame-v3 **SHA-256** line for H100 E4M3. The layout is ShaFp8, the same one as the 4090 fp8-ada SHA
line (23:15Z). The lowering is the reviewed fp8-hopper one (pin 904ca664).

- **Binary:** `flock-pure-gpu` from `cursor/flock-gpu-link-797a` @ ad0aa41d, built with SM=90. It includes the
  host-witness reuse across both reps.
- **Evidence:** H100 80GB HBM3 with a loopback verifier. Run r20260925-232133-996e, art:29438e24.
  - CPU and GPU selftests pass every case at 8 VUs (m24) and 64 VUs (m27).
  - 4,096 VUs (m33): 4.16–4.21 s end-to-end, about 980 VU/s. Rep 0 proves in 3.6 s and rep 1 in 0.47 s. 246 rounds,
    549 KB proof per rep, 1.24 MB sent up.
  - 8,192 VUs (m34): 8.4–9.1 s end-to-end, about 960 VU/s. Rep 0 proves in 7.3–8.1 s and rep 1 in 0.92 s. 270 rounds,
    580 KB proof per rep.
  - **Rep 0 is host-witness bound.** Rep 1 (0.47–0.92 s) is roughly the GPU cost. Rep 0 also builds the SHA-256 witness
    and the unit witness on the host CPU. A device SHA-256 witness would bring both reps close to the rep-1 time.
- **Pod:** 2et04vl8xj3ei6 is terminated. No flock-gpu-link pods are still up.
- **red-team-flock:** nothing new beyond the 23:15Z and 23:23Z SHA notes and the fp8-hopper grant of 23:20Z.
