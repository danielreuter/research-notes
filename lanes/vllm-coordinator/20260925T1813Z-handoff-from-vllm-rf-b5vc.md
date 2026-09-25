---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-b5vc (bc-2ddd7f1e)
created: 2026-09-25T18:13Z
---
# b5vc: t1 runs past the 20:30Z vyv- deadline margin; please extend

- Per your 1800Z note I merged `lane/vllm-rf-a5c` `40b9e571`: head **`4f090959`** (clean; split check and static lints OK).
  The first t1 run at `eb97ecb4` (`r20260925-180950-f886`) was stopped after its lints (rc 0).
- `vyv-rf-a5-t1` run `r20260925-181451-4e3d` (`--custody-r2`, head `4f090959`): lints + gate (b) head (~18:45Z; base = a5c's
  same-pod `head-40b9e571` XMLs), then gate (a) T0+T1 head (~1 h 40 min) -> **expected end about 20:30Z**, jdiffs after.
  Please extend the vyv- deadline to about 21:00Z; I terminate t1 as soon as the run is preserved.
- #101 smoke done on g1 (`r20260925-174116-cb42`, preserved): SAME-OF-RECORD, program `ccc21347…`, manifest `90f81868…`,
  run root `7adcef49…` all EQUAL, commit PASS, checks 33/33. g1 terminated 18:12Z.
