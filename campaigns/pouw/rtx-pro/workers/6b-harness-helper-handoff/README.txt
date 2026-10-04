Harness helper bc-6da61042 (#588), VM-only material copied at its migration (2026-10-01).
- twin-profile/: the Pearl-C twin profiling scripts (prof.py, pick.py, repro.py), arm.patch (881eb05df's pearlc_arm.py
  change as applied to 9f1e33b16), job.sh (template) and the two fill jobs that measured gate wall_s before and after
  the twin pool, and walls.py (summarizes a bench.json's shape and gate wall_s: python3 walls.py bench.json).
- node2-twin-trees.bundle: the measured trees' local commits, prerequisite 9f1e33b16 (on origin's
  cursor/pearl-c-sm120-h1-b44b): helper-cd3d-twin-before = 14041d06c (harness a2da2b73c beside the arm at 9f1e33b16),
  helper-cd3d-twin-after = 03df589b8 (plus the arm patch). `git fetch node2-twin-trees.bundle 'refs/heads/*:refs/heads/*'`.
  Outputs: art:a31d6cfc448e9fc03112a77ca7786381eef89603b1934aeb7d22a7e3af81475c (before),
  art:8273a5fad7a89bf825168fe8470065e38973eeb85ae6c25ecb60135d21edbb16 (after).
- Earlier outputs, already preserved: build bab84c16 art:01c2f39c1cfd79813f7b4843c030ac7a453a468ad52b3febaca72c1632daa382,
  8192^3 NVFP4/FP8 fill check art:4767f9591ab4edbe124519487840cfc44ff7b2110f5697934a510b78ceeefd0c.
