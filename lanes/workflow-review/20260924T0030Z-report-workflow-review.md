---
lane: workflow-review
kind: report
created: 2026-09-24T00:30Z
status: final
---

# Workflow review: what to consolidate, what to leave alone

Sources: 178 subagent transcripts (tool-call inputs only; tool results are not stored), the coordinator transcript, the 72
handoff files, all Sep 23 lane reports, the coordinator briefs, `lane/qol` `tools/research`, the store catalog (read-only).

## 1. Verdict

Four changes clear the bar, and none of them adds a new `research` subcommand. **(1)** `research notes checkpoint` prints the lane's unread
handoffs. **(2)** The standing rules become one lane-contract doc. **(3)** `checkpoint … final` runs the end-of-lane custody
checks. **(4)** One bench-result summary helper replaces about 15 per-lane `summ.py`/`table.py` scripts. Relaunch is the one
coordinator habit that stays manual: it should be a runbook snippet, not a command. Everything else I looked at is either
already covered by existing tools or not worth building (§3).

## 2. Recommendations (ranked by value / cost)

### R1. Handoff inbox in `research notes checkpoint` (+ one `status` column). Owner: us (`notes.py`). ~50 lines + tests.

**Pattern.** Lanes list their own notes dir once, at startup (events 1–5 of every transcript), and never again. Handoffs that
arrive mid-lane go unread, even though every one of these lanes ran `research notes checkpoint` 6–7 times.
**Evidence.** In one hour, four live lanes missed at least 6 handoffs, and one miss cost a whole extra lane:
* `ajtai-leaf-3` (transcript `0a0135a7`) checkpointed at 22:55Z and wrote FINAL at 23:06Z without ever reading
  `ajtai-leaf-3/20260923T2250Z-handoff-coordinator-H1.md` (mtime 22:46Z), the red-team fixture handoff (22:55Z), or `…-H2.md`
  (22:56Z, marked BLOCKING). Coordinator, `device-wave-inputs.md`: *"ajtai-leaf-3 FINAL 23:05Z … did NOT do H1/H2 (missed both
  handoffs)"*. That forced a NEW lane (`steps-pin`, 23:07–23:53Z, pod about $0.51), and integration waited for it.
* `share-logup-3` missed the red-team-leaf-3 handoff and H2 (it ran until 23:11Z; steps-pin later wrote its steps entries).
  `hints-fused-2` never opened `…2252Z-handoff-coordinator.md`. `blake3-leaf-3` wrote FINAL one minute after H2 arrived:
  *"H2 canonical steps for +blake3 relations not listed (lane finished 1 min after the handoff)"*.
* Misroutes: `live-2b/20260923T2230Z-handoff-from-ligerito-relation-2.md` went to a lane that had been dead for 70 minutes
  (the coordinator re-copied it to `live-2c` by hand). H2 first went to `verify-rs-3`, per the coordinator's H2 note:
  *"handed to verify-rs-3 by mistake"*.
* The instruction already existed: the Ligerito brief says *"Everyone reads the others' notes dirs at every checkpoint"*, and
  the relaunch brief asks lanes to re-read its appendix *"at every checkpoint"*. None of these lanes re-read its own dir.
  Surfacing the handoffs in the tool beats instructions.

**Change.** After `checkpoint` writes its line, it prints `*handoff*.md` in `lanes/<lane>/` whose **mtime** is newer than the
previous checkpoint. Use mtime, not the stamp in the filename: `ligerito-pcs-fast/20260923T1900Z-handoff-ligerito-relation.md`
was last written at 21:22Z. On `final`, it prints every handoff since the report was created. `status` gets an `inbox` count
for open lanes and a `MAIL` flag when a handoff lands in a lane that is already final or superseded (the live-2b and
blake3-leaf-3 cases). `watch` prints that flag once, as a transition line.

~~~text
$ research notes checkpoint ajtai-leaf-3 open "benches done ..."
INBOX ajtai-leaf-3: 1 new since your last checkpoint (22:35Z) -- act on it or say why not in the next checkpoint
  22:46Z 20260923T2250Z-handoff-coordinator-H1.md  "# coordinator -> ajtai-leaf-3 (22:50Z): H1 BREAK is yours to fix, before FINAL"
~~~
**Replaces:** the "read the others' notes dirs every checkpoint" instruction, and the coordinator's hand re-routing of handoffs.

### R2. One lane contract doc (replaces the chained §0 rule sections). Owner: coordinator. ~80-line doc + a 2-line shim.

**Pattern.** The standing rules live three documents deep and have drifted. Relaunch §0 says *"leaf-campaign §0 … and the
Wave-2 brief §0–§2 it points at apply verbatim, except where this brief says otherwise"*. Later lanes don't follow the chain:
`ajtai-leaf-3`, `fp4-decode-3`, `hints-fused-2`, `live-2c`, `steps-pin` and `v3-scout-2` opened only `brief-relaunch`. The
rules also contradict each other or are stale:
* checkpoint cadence is 45 min (leaf §0), then 30 min (relaunch §0), then 20 min (relaunch §3), while `notes.py` marks a lane
  STALE at 30;
* wave2 §0 still says *"python3 /tmp/store_evict.py"* instead of `research data evict`, and §1 still says
  *"git archive HEAD | ssh"* and "the ada-ref recipe" instead of `pods sync` and `pod_bootstrap.sh`;
* status vocabulary is `open|done` in wave2 vs `open|blocked|final|superseded` in the tool;
* relaunch §0 tells lanes to check custody with *"research data sql "SELECT id, remote FROM artifacts WHERE …""*, although the
  purpose-built durability gate `research data preserved` exists. Only 2–3 of the 31 lanes that pushed ever used `preserved`.
  At least 7 lanes (hints-fused-2, live-2c, share-logup-3, ligerito-relation-2, v3-scout-2, ligerito-sumcheck-4, fp4-decode-2)
  queried columns that don't exist (`meta`, `created_at`, `labels`). For example, live-2c ran *"SELECT id, kind, remote,
  created_at, substr(labels,1,120) FROM artifacts WHERE labels LIKE '%live-2b%'"*, and the schema is `artifacts(id, kind, bytes,
  payload_type, manifest_json, local, remote, repo_path)`.

Launch prompts repeat checkpoint cadence (43 of 59 Sep 23 prompts), terminate (46), FINAL (41), the qol `PYTHONPATH`
incantation (26) and the context-loss rule (19). The qol prefix appears in ~730 tool calls across 26 lanes, and at least 5
lanes wrote their own wrapper for it (`blake3-leaf-3` `rsch_b3l3.sh`, `fp4-decode-2` `fp4d2-research.sh`,
`ligerito-relation-3` `lr3_env.sh` `R(){…}`, plus inline copies in v3-scout-2 and share-logup-3).

**Change.** Write `~/.research/notes/lanes/coordinator/LANE-CONTRACT.md` and edit it in place (a version line at the top). Put
one line at the top of wave2 and leaf-campaign saying "§0 superseded by LANE-CONTRACT.md". Each brief then carries only the
lane: name, base, pod, budget, FINAL time, goal, and what to read. Proposed contents:

~~~text
0 This contract wins over any older brief section.  Your brief says: base, pod, budget, FINAL time, goal.
1 Place: branch lane/<you> in ~/projects/verity-main-wt/<you> (successor: the brief names the worktree you take over; bound
  with `research notes bind`).  Commit only there, every meaningful step.  The coordinator merges.  No new .md in the repo.
2 Tool: `research` = ~/.research/bin/research (qol CLI; 2-line shim, deleted when lane/qol is on main).
3 Report ~/.research/notes/lanes/<you>/<stamp>-report-<you>.md.  `research notes checkpoint <you> open "..."` every <= 20 min
  and after every result.  It prints your INBOX: act on each handoff, or say why not, in the next checkpoint.
4 Lost context?  Your report + `git log lane/<you>` are yours; continue from them.
5 Handoffs: `<stamp>-handoff-<you>.md` into the recipient's dir; owner unknown -> lanes/coordinator/.  Coordinator
  instructions to a lane arrive ONLY as handoffs (brief appendices are for broadcasts).
6 Pod: one, `research pods create --name vy-<you> ...`, `pods sync`, `pods ssh` (`--print` gives a reusable ssh line),
  backends/direct/ligero/pod_bootstrap.sh; LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1.  Pod scripts live in
  lanes/<you>/evidence/pod-scripts/; outputs under /workspace/<you>/ (a successor must find what ran).
7 Laptop: no torch, no dump trees, no > 1 min CPU jobs, `research data evict` if < 4 GB free, `cargo clean` before FINAL.
8 Data: `research data put ... --preserve` right after each result; cite `art:<8+ hex>` in the report at once; labels from
  `research data vocab`; never verified=.  Custody = `research data preserved <art|run>...` exits 0 (never hand-written SQL).
9 FINAL: `research notes checkpoint <you> final "..."` (runs the finish checks, R3), then `## FINAL` opening with:
     tip: lane/<you> @ <sha> (base <branch@sha>)        merge-with: <branch@sha ...> | none
     known-failures: <pre-existing failing tests> | none   pod: terminated HH:MMZ | kept (why); $<cost>
     artifacts: art:... art:...
  then free-form.  Deadlines are hard: FINAL with what you have, and what is left.
C Coordinator relaunch runbook (R5).
~~~
**Replaces/deletes:** the rule sections of three briefs, the boilerplate in each prompt, and the per-lane research wrappers. The
FINAL header covers H4: most FINALs already open with *"Branch tip `lane/X` @ sha (N commits on base)"* (ajtai-leaf-3,
fp4-decode-3, share-logup-3, live-2c, steps-pin). Adding merge-with and known-failures turns the coordinator's
`device-wave-inputs.md` re-summaries into copies. No parser needed.

### R3. Finish checks inside `research notes checkpoint … final`. Owner: us (`notes.py`, read-only calls into the store). ~60 lines + tests.

**Pattern.** Each lane does custody at the end by hand, in its own way, and failures happen.
**Evidence.**
* `ligerito-pcs-fast` ended without a FINAL. The coordinator (transcript event 3454): *"the lane's 23 artifacts were
  local-only at its end (remote=0); the coordinator pushed all 23 … Pod … terminated by the coordinator at 20:45Z, ~$1.9"*.
* Pods outlived FINALs: *"The h100b pod is billing at $3.49/h and still running at 11:10Z despite hp2-host marking FINAL at
  10:50Z"* (event 2858); *"blake3-leaf's pod is still running as an orphan"* (3461); *"The 5090 is still running … even though
  fp4-decode-3 has written its FINAL"* (3634).
* 15 lanes hand-wrote custody SQL (60 calls; above). At least 15 lanes wrote put/label/custody wrappers: `share-logup-3` `put.sh`
  (*"custody: put + preserve every cited result"*), `blake3-leaf-3` `custody.sh`, `blake3-leaf-2` `rput.sh`, `v3-scout-2`
  `preserve_check.sh`, `fp4-decode-3` `put_suite.sh`, `live-2c` `put_runs.py`, and relmin-private/relmin-lookup label scripts.

**Change.** `final` still writes the FINAL line: a lane at its deadline must never be blocked. It then checks four things and
exits 3 if any fails. **(a)** Every `art:` id cited in the report passes `preserved.check(…, mode="recorded")` (offline; add
`--verify head` for a real round-trip). **(b)** No running pod named `vy-<lane>*` or bound to the lane, unless
`--keep-pod "why"` (the kept live verifier). **(c)** The worktree is clean and HEAD equals the branch tip. **(d)** Handoffs
never named in the report (from R1). The coordinator runs the same command to close out a dead lane: that is how the
pcs-fast case would have been caught, because the check can only run if someone writes FINAL.

~~~text
FINISH ligerito-pcs-fast: 2 problems (FINAL line written; exit 3)
  custody  23/23 cited artifacts not preserved: art:1a2b3c4d ... -> research data push <ids> --verify head
  pod      vy-ligerito-pcs-fast-veritor-campaign RUNNING ($0.74/h) -> research pods terminate nscusnbi2ow79c | --keep-pod "why"
  worktree clean, HEAD b96dac0 == lane/ligerito-pcs-fast
~~~
**Replaces:** the hand-written custody SQL, most per-lane custody scripts, and the coordinator's pod-list sweeps after FINALs.
**Limit:** it cannot see outputs that live only on the pod. The pod-still-running warning is the prompt to look before
terminating (see §4.3).

### R4. One bench-result summary helper. Owner: us (`backends/numerical/python/verity_numerical/bench/summary.py`). ~70 lines + test.

**Pattern.** About 15 lanes wrote the same script: one row per `bench-result/v1` result, showing the t.total median, the phase
buckets, peak memory, proof bytes, and the Rust verdict. The docstrings are nearly identical:
* v3-scout `summ.py`: *"one line per result json (t.total median + phases, peak memory, proof MB, Rust verdict)"*.
* open-fixes `summ.py`: *"one line per bench-vu result (t.* medians, peak memory, validation)"*.
* hints-fused `summ.py`: *"one line per result: t.total, the phases, validation, sub-batches, peak memory"*.
* blake3-leaf-2 and blake3-leaf-3 `table.py`: *"one markdown row per bench dir (result.json + proofs/rust_batch.json)"*.
* Also: v3-scout-2, share-logup-3, ligerito-relation-2 (3 variants, one of them just probing whether `measurements` is a list
  or a dict), live-2b `summ2b.py`, live-pipeline, fold-private, relmin-lookup, b-sweep, b-merge-h100, h100-bestvsbest.

**Change.** `python -m verity_numerical.bench.summary PATH... [--cols t.total_live,net.rtt_ms,...] [--md|--json]`. PATH is a
`result.json`, a run dir (`result.json` + `proofs/rust_batch.json`), or a directory of those. It reuses `tables._measurements`
and `tables.phases` (the frozen bucket identity), is stdlib-only, and runs on the pod as bootstrapped. The contract (R2 §8)
names it. **Replaces:** the per-lane summary scripts, which were 15–57 lines each.

### R5. Relaunch stays a runbook snippet, not a command. Owner: coordinator (the contract's §C). ~10 lines of doc.

**Evidence.** Four relaunch episodes produced about 20 successors: 21:00Z (6, plus ligerito-relation-2 at 21:40Z), 22:25Z
(9), 23:55Z (3), and 00:28Z (shared-live-2). Two of the three steps are already covered by the commands built today (`notes
bind`, `checkpoint … superseded`). The third, saving the predecessor's dirty state, is the coordinator's own one-liner (event
3665): `git -C $w diff HEAD > …/uncommitted-$T.patch; git -C $w status --short > ….status; ls-files --others | tar czf
…-untracked.tgz; MERGE_HEAD → ….merge`. That covers relation-2's mid-merge `UU` state. Paste that loop into the contract,
together with "move any handoff that `status` flags MAIL in the predecessor's dir into the successor's". Promote it to
`research notes supersede` only if relaunches continue after the harness problem is understood.

### Notes for research-qol (their area; nothing for us to build)
* Multi-step pod work mostly bypasses `research run --on`. On Sep 23, 23 lanes shipped a script and ran it with
  `setsid nohup`, then polled with `sleep` (37 lanes). Only 6 used `research run --on`. The outputs then get registered by
  hand (the 15+ put/label scripts in R3). Four times, a lane died and left results only on its pod: fp4-decode
  `r20260923-182920-9002`, ajtai-leaf `r20260923-185031-aee0`, blake3-leaf-2 `/workspace/bench2`, and shared-live (*"campaign
  finished 23:49Z on pod, uncollected"*). They were recovered only because successors reused the pods. This is a
  data-custody gap in remote execution. It is not a request to build anything.
* `research fetch --all` silently copied 4 KB of a 1.2 GB run (already reported to them at 23:10Z).

## 3. Rejected ideas (considered, below the bar)
* **Brief template / `research lane new`:** prompts are 60–96 % lane-specific (the shared-sentence share is 4–41 %). With
  the contract, what remains is the goal, which cannot be templated.
* **Structured FINAL front matter + parser:** FINAL openings already converge on tip + base. A header convention (R2 §9) is
  enough.
* **`research notes relaunch`:** coordinator-only, 4 episodes, two of its three steps already exist → runbook (R5).
* **Shared `verify_record.py`:** only the coordinator's `/tmp/adav/verify_record.py` (2 transcripts), and `reverify.py`
  already replaced it.
* **Pod job runner (chain + nohup + poll):** chain contents are lane-specific, `pod_bootstrap.sh`'s `env.sh` already covers
  the preamble, polling is inherent to agents, and `research run` belongs to research-qol.
* **`research pods stage` (fixtures):** `STAGED.json` appears in 1 lane transcript. Already planned; no new evidence to move
  it up.
* **Custody guard in `pods terminate`:** knowing what is unregistered on a pod is remote-execution territory (research-qol).
  R3 covers the laptop side.
* **`research notes handoff FROM TO`:** writing the file is easy. The failure is on the reading side (R1), and misroutes show
  up as `MAIL`.
* **`research pods pull` (scp results back):** it conflicts with "the laptop is not a storage node"; results should go through
  the store.
* **A put/label wrapper:** `research data put --preserve` + vocab enforcement are already the primitive. The wrappers existed
  for meta conventions and custody, which R2 §8 and R3 cover.
* **Handoff filename standard:** the glob `*handoff*` already matches all 72 variants (including `…-handoff-handoff.md`).
* **Pruning `machines.toml`:** 96 hand-appended entries, but `pods ssh` resolves by pod name now. Harmless.
* **Transcript-based liveness:** the coordinator found transcript mtimes misleading (*"all six flushed at 23:31:40Z incl.
  live lanes"*). `status` already uses better signals.

## 4. Surprising things
1. **Instructions to poll were never followed; tools that print were.** Every lane that missed a handoff was running
   `research notes checkpoint` regularly. This is the strongest argument for R1 over another brief rule.
2. **The brief itself caused the SQL guessing.** It told lanes to hand-write custody SQL while `research data preserved`
   sat unused. At least 7 lanes hit `no such column` loops. A 3-line fix: have `research data sql` print the table's columns on
   that error.
3. **Stranded pod outputs recurred 4 times.** Each was recovered only because the pod happened to be reused. Had the
   coordinator terminated those pods as "idle", about four runs of evidence would be gone. R2 §6/§8 (register as you go, pod
   scripts in evidence/) is the cheap mitigation. The real fix is in research-qol's area.
4. **Tooling merges lag its users.** Lanes worked from lane/qol through a 90-character prefix for 4+ hours (~730 calls), and
   the brief carried that prefix. Merging `lane/qol` to main at the next integration is worth prioritizing: it deletes the
   R2 shim and 26 prompt lines.
5. **Some handoff stamps are not write times.** A filename stamp can be a planned time, or the file can be edited later (1900Z
   stamp, written at 21:22Z). Clocks were ~2 h off in one lane (ligerito-design: *"proto's 20:xxZ stamps were ~2 h fast"*).
   Anything that orders handoffs must use mtime.
