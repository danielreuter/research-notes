---
lane: verify-flock-pure
kind: handoff
from: coordinator
created: 2026-09-25T21:00Z
---

# Verify whichever H100 pure-Flock runs flock-backend publishes (it's re-measuring with PR #30 @ 48045063), and the RTX 4090 cell if one lands

flock-backend re-measures the H100 cell with flock-gpu-link's faster binary (8,192 VUs in 1.23 s) and adds a 4090 fp8-ada cell
(SM=89 build). Replay and label the published H100 run (the new one if it lands by about 23:30Z, else the current one) before
your 00:45Z deadline. The 4090 cell is a bonus: label it if its runs arrive in time. Report to lanes/coordinator/.
