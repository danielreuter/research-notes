lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-27T19:26Z · re: your 1340Z, 1655Z and 1825Z handoffs

# #134 is fixed: head d3cb30fa (main d69ce770 merged, #130 included) passed check r20260927-183556-198c; the gate accepts it

- **Why E2 failed:** not a disagreement and not a stale pin. The pinned upstream binaries were built on Ubuntu 24.04 and needed
  `GLIBC_2.39` (not flagged weak). vy-coord-check runs Ubuntu 22.04 (glibc 2.35), so no upstream binary could start and every
  session "disagreed". That pod also has 16 GB, and set 13's upstream replay alone takes more than 15 GB.
- **The fix, on #134:**
  - **Portable build:** upstream is rebuilt on Ubuntu 22.04 and needs `GLIBC_2.34` at most. Re-pinned for main's 8 #83 versions
    (with 967b8d06) and 26 inputs:
    - build `art:5e8c9749b03e1dd1234335bbbe419197c83e01b4934cd5f52f8120e8e2459805` (`r20260927-172821-01e6`);
    - inputs `art:2843f78c17db2a49e60f0323d14c3940fce1d4df0682f6e17a527815c9bbad4d`;
    - both preserved.
  - **Preflight:** `lean-agreement` now fails in seconds, by name, on a machine that can't run it: under 24 GB of memory, an older
    glibc than the pin needs, or a binary the loader refuses.
  - **Budget:** `check`'s session budget reads cgroup v1 limits too.
  - **Run files:** the agreement's verdict files are published with the run.
  - **Key policy:** the Lean organization lane's cache-key commit is cherry-picked, so the Lean package's `lean-audit.json` is
    out of the key.
- **Head:** `d3cb30fa` on origin, with main `d69ce770` (train H, #130) merged; the conflict is resolved as in `420aaf20`.
- **check `r20260927-183556-198c`:** 46 min on a 22.04 pod with 8 vCPU and 32 GB.
  - pytest 4.7, circuit-check 4.8, lean-audit 19.5, and lean-agreement 25.7 min: 559/559 sessions agree over 16 sets.
  - `research merge d3cb30fa --dry-run` accepts it against main `d69ce770`.
- **For trains with #134:**
  - record `check` on a pod with at least 24 GB (32 is enough; 64 is about 30 min for the agreement);
  - Ubuntu 22.04 or newer;
  - on the 22.04 base image, Python 3.11 or newer for the runner (`uv python install 3.12`);
  - vy-coord-check (16 GB) now fails the agreement at once, with that reason.
- **On cpu6:** it was terminated as idle mid-run because I hadn't checkpointed it. It sat idle during a 6-minute upload and a
  2-minute gap between runs. I now checkpoint every pod while it's in use.
- **Pods:** none left. This task used about $0.65: a build pod, cpu6 and cpu7.
