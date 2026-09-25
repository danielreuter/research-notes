---
lane: ajtai-leaf-2
kind: report
created: 2026-09-23T21:00Z
status: superseded
---

CHECKPOINT 0b40ae8a (05:54Z) [superseded] closed by coordinator 2026-09-25 05:55Z for the cloud switch-over: no sign of life >24 h; branch lane/ajtai-leaf-2 pushed to origin; uncommitted work (if any) saved in evidence/uncommitted-0554Z*
CHECKPOINT b67c019 (21:10Z) open — stage-4 run r20260923-185031-aee0 RECOVERED + pushed (art:c4046648…, remote): on d40399f cargo
27+7+16 ok, both gates 0 failures, fixtures written, but 8 conformance failures (scheme `name` = "ajtai" and NO x/W role separation,
which the conformance suite requires) -> its pins are superseded. Carried the predecessor's role idea but NOT its mechanism: a per-role
constant `-role*b_256` in the Linear rows breaks every pad column (witness 0; stage-A r20260923-210032-123c "witness violates
constraints: linear hash.ajtai.r1.out[*]"); now a KEY PER ROLE (x: b_0..b_255, W: b_256..b_511; B n x 512, no constants), Rust key
check per block. Also found: d40399f's bench_vu_rel referenced `R` before assignment (every bench died, bare included) -> fixed; and the
hashed runner IGNORES `--pipeline` (pipeline_depth forced to 0: all previous "+hash/+ajtai at --pipeline 4" numbers were unpipelined vs
a pipelined bare). Stage A r20260923-210731-1c99 running (fixtures -> pins -> full cargo test -> gates -> benches -> pytest). Next:
a pipelined `HashedRelationRunner.prove_vus_many`.
CHECKPOINT d40399f (20:58Z) — started. Briefs (relaunch §0/§1.2, leaf-campaign §0/§3.4/§9), predecessor report, red-team-leaf FINAL read.
Worktree `~/projects/verity-main-wt/ajtai-leaf-2` on `lane/ajtai-leaf-2` @ d40399f. Predecessor's 2 uncommitted files read (role
element `b_256` in `ajtai.py`, unfinished: placeholder B digests, no Rust side, written 19:05Z AFTER the stage-4 run started 18:50Z;
Ajtai fixture tests in `relations.rs` with placeholder pins). Next: recover stage-4 run r20260923-185031-aee0 from the pod.

# Lane ajtai-leaf-2 — finish the Ajtai leaf (pins, fixtures, gates, benches at `--pipeline 4`)

## Log
* 20:53Z start.
