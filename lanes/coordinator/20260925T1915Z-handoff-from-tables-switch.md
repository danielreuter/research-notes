---
lane: coordinator
kind: handoff
from: tables-switch
created: 2026-09-25T19:15Z
---

# MERGE-READY tables-switch @ 25a26e3b: parity command, steward `published = "views"`, switch digest, CHANGELOG (builds on PR #32, already merged)

**Tip:** `lane/tables-switch` @ `25a26e3b`. It already merges origin/main `a1ccdecd` (PR #32), and it adds no Flock column of its own.
The frozen `tables` and `drilldown` renders are byte-identical to main's on a store refreshed from R2 at 19:05Z (7,847 manifests):
tables 249,848 B, drilldowns 52,683 B.

**Tests (on the merged tree):**
- `backends/numerical/tests/bench`: 281 passed, 6 skipped.
- `tools/research/tests/test_notes.py`: 60 passed, 1 failed. The failure is
  `test_relaunch_saves_the_work_supersedes_binds_the_successor_and_prints_its_launch_message`, and it fails the same way on
  main `a1ccdecd`. It's pre-existing and unrelated to this change.
- `tests/test_repository.py` has two pre-existing failures on main (the DISCREPANCIES.md size cap and the proof-blob limit).

**What changed:**
- `views --parity --take-snapshot --record` takes the `tables --snapshot`, compares, and stores the check as a
  `tables-parity/v1` artifact (a new kind in `research.store.kinds`). The artifact holds every cell's artifact and both ratios,
  with refs to the snapshot and the cells. It exits 1 on a difference. `tables.take_snapshot` is shared with `tables --snapshot`.
- `views --published` swaps the PREVIEW banner for the published one, and nothing else changes (tested).
- `notes.render_lines`: a `[[render]]` entry with `published = "views"` writes `views --published` as `<stamp>-tables.md` and
  `tables` as `<stamp>-tables-frozen.md`. The drilldowns are unchanged. Any other value of `published` gives `RENDER-FAILED`.
- `python -m verity_numerical.bench.switch --root <store>` is the switch digest: the change-of-method label, the parity line,
  then each frozen Table 2 number beside its replacement (the family's new cell on each scheme line) and the first reason it
  left. New cells with no predecessor are listed after.
- `backends/numerical/CHANGELOG.md` is new, and `backends/AGENTS.md` has the updated render paragraph.
- Table 1 now notes on the A-GKR and Flock family rows that route (a) stays in A-GKR's column. I agree with that placement: its
  backend name is `verity-gkr …` and its prime side is A-GKR. A test pins PR #28's route (a) name to A-GKR.
- `kb/TABLES.md` is edited in place (updated line bumped): Flock in the family term; the parity, digest and after-switch
  render commands. **When you next republish `docs/tables-spec-draft.md` over kb, carry these lines, or they'll be lost.**

**Parity on the R2-refreshed store (VM, 19:10Z):** ok, 15 of 15 cells, same artifacts and ratios. Snapshot `tables-2026-09-25`
is `art:23049a6d942de6468557b983207b8541d10685fd1876aee8baad7ed9022c5b5c`, and the parity record is
`art:af3ddc986e1511bf9abd862608dcde0029aa1ff23b0bd2173ac36b635f97f8a5`. Both are VM-local and not pushed, and both ids are
content-addressed, so the control pod reproduces them if its store holds the same cells. The digest preview is at
`lanes/tables-switch/evidence/switch-digest-vm-1909Z.md`. All 15 old cells leave Table 2: the A-GKR and bare B-Ligero cells on R,
the in-proof hash cells on M. They're replaced by the 10 new B-Ligero cells (SHA-256, BLAKE3 and Poseidon2 rows); A-GKR has none.

**The 6 PM PT recipe (control pod, after this merge and after moving `/workspace/steward/verity` to the new main):**

~~~sh
S=/workspace/steward/verity; ST=/workspace/steward/store; OUT=$RESEARCH_NOTES/renders/daily; stamp=$(date -u +%Y%m%dT%H%MZ)
cd $S && eval "$(research env --source $S)"
research data refresh --store $ST --payloads instance-equiv/v1 bench-result/v1
python -m verity_numerical.bench.views --root $ST --parity --take-snapshot --record > $OUT/$stamp-parity.txt   # exit 0 = parity; stderr: "parity recorded as art:P (snapshot tables-<date> art:S)"
research data push --store $ST art:S art:P                                                                      # preserve both
python -m verity_numerical.bench.switch --root $ST > $OUT/$stamp-switch-digest.md                            # the digest to post
python -m verity_numerical.bench.views  --root $ST --published > $OUT/$stamp-tables.md
python -m verity_numerical.bench.tables --root $ST --format md > $OUT/$stamp-tables-frozen.md
python -m verity_numerical.bench.drilldown --root $ST --format md > $OUT/$stamp-drilldowns.md
~~~

Post `$stamp-switch-digest.md` with the parity art id. If parity exits 1, don't switch: the differences are in `$stamp-parity.txt`.

**The `steward.toml` edit (in the notes root), made after the switch, and only once the render source tree has this merge**
(an older tree's `views` rejects `--published`):

~~~toml
[[render]]
at = "13:00Z"
source = "/workspace/steward/verity"
out = "renders/daily"
store = "/workspace/steward/store"
published = "views"
~~~

**For Daniel or you, not decided here:** rule K requires `hardware.gpu.name` to equal the line's device. Flock's prover so far
runs on CPU pods, so a CPU-run Flock result fails K on every line. flock-backend is told in
`lanes/flock-backend/20260925T1912Z-handoff-from-tables-switch.md`, which also carries the record contract, pinned by
`test_a_pure_flock_record_fills_the_flock_column_without_renderer_changes`.
