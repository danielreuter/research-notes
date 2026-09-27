lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-27T07:46Z

# Fast check ready as draft #134 (stacked on #100): the upstream agreement is required for backends/flock/, and it's cheap when warm

- **The PR:** `cursor/fast-check-4d78` at f632ead5, draft #134 with base #100's branch. I'll retarget it to main once #100 lands.
- **Upstream built once:** stored (art:5a3f8e47, rustc 1.98.1, plus the inputs at art:b2178129) and pinned in
  `backends/flock/verifier/upstream.json`. It agrees 412/412 across all 8 sets.
- **The path rule:** research merge requires `lean-agreement` for any diff under backends/flock/, and elsewhere it's a named
  skip. Record with `uv run python tools/check/check.py --record --on POD`, which sends the build when it's needed; trains take
  `--send`.
- **Measured on a loaded 16-vCPU pod:**
  - cold with the agreement: 21.8 min, 21.3 of it the agreement;
  - warm, same tree: under 1 s;
  - warm, a flock change outside the verifier: 2.7 min;
  - a train of 3: 5.6 min end to end.

  The serial check was 35 min without the agreement.
- **Two things due:**
  - #118 (`eb90718f`) needs a rebuild and re-pin, about 5 min on a pod. A test enforces that the pin covers every version.
  - The agreement's cold cost is `agree.py`'s sequential sessions. I've suggested parallelizing them to flock-verifier.
- **Report:** the store's `internal/lanes/circuit-checks/20260927T0745Z-report-fast-check.md`.
- **Pod:** vy-circuit-checks-cpu4 is warm (toolchains and caches) and shuts itself off after 90 idle min.
