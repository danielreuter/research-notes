---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: flock-soundness
kind: handoff
from: coordinator
created: 2026-09-28T19:52Z
---

# coordinator -> flock-soundness: kernel-replay audits of the soundness package on #316 and #318 PASS; #274's check is still running

All three runs are on `vy-coord-check4` (16 vCPU, about 1 TB RAM), recorded, and charged to the research line.
Each audit is `bash tools/lean/setup.sh backends/flock/verifier/lean/soundness && python3 tools/lean/audit.py --build
backends/flock/verifier/lean/soundness`, which compares against the recorded pins and runs the kernel replay.

| PR | head | run | result |
|---|---|---|---|
| #316 (N1 option (b), on #304) | `81c6bd25` | `r20260928-190015-a156` | **PASS**: 7,083 declarations in 102 modules; 20 pinned theorems; axioms `propext`, `Classical.choice`, `Quot.sound`; build 1,196 s |
| #318 (R10 salted leaves) | `8fe41c93` | `r20260928-190115-b3c6` | **PASS**: 6,182 declarations in 97 modules; 19 pinned theorems; the same three axioms; build 1,192 s |
| #274 (S5) `check` | `98494662` | `r20260928-190215-cc0c` | **failed in pytest (2,637 s), on 3 tests that aren't #274's:** `test_notes.py` relaunch (fails daily 19:00–20:00Z, on main too; fixed by #322), `test_telemetry.py::test_tele_run_reads_a_timeout_change_from_the_control_file_and_records_it` (timing, on a heavily loaded host), and `test_lean_rope.py::test_rope_data_is_the_export_and_the_pinned_rows` (your branch predates main's RoPE fix `a828335c`) |

#316's run wrote its reports to the pod's temporary directory. #318's are in its run's `lean-audit/`. `research fetch --all <id>`
on the control pod brings them over.

#274 itself is also in train D3 (`de4118fc`, check `r20260928-193411-c5c9`), so it lands with D3 if that check passes.
