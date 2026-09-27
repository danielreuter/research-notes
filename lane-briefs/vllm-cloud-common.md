---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# vLLM refactor lanes on cloud VMs: shared rules (coordinator bc-ecac3029, 2026-09-25 16:20Z; fixture keys 16:58Z)

Every `vllm-*.md` brief in this directory points here. Read this after `cloud-lane-setup.md` section 1 and before your
own brief. Where this page and `cloud-lane-setup.md` differ, this page wins for vLLM lanes. Where it differs from
`$RESEARCH_NOTES/lanes/vllm-refactor/WAVE2_BRIEF.md` or `LANE_BRIEF.md`, this page wins too.

## Context
- At 16:03Z (9:03 AM PT) the laptop restarted and every vLLM lane session ended. All branches were pushed at 16:04Z.
  The pods kept running under the vyv- guard, and several hold in-flight runs. You succeed one ended lane: adopt its
  branch head, its pods and its recorded results. Don't redo recorded work.
- Coordinator: vLLM coordinator, Cursor agent `bc-ecac3029` (cloud). It never merges into `main`; it forwards merge
  requests to the root.
- **The notes mirror is stale.** Lane STATE.md files under `$RESEARCH_NOTES/lanes/vllm-rf-*/` stop at about 14:30–15:04Z
  and lack the 16:04Z restart banner. Your brief lists what the coordinator saw on the pods at 16:10Z. For anything
  later, look on the pod.

## Environment
- Do `cloud-lane-setup.md` section 1. The repo is `/workspace`. Run the CLI as
  `PYTHONPATH=tools/research/src python3 -m research ...` (uv isn't installed on these VMs).
- SSH: if `research pods ssh <pod> -- true` fails for want of a key file, run
  `mkdir -p ~/.runpod/ssh && printf %s "$RUNPOD_SSH_KEY_B64" | base64 -d > ~/.runpod/ssh/runpodctl-ssh-key && chmod 600 ~/.runpod/ssh/runpodctl-ssh-key`.
  Never print a credential.
- **Pods: section 4's "never touch `vyv-*`" is for research lanes. Yours are the vyv- pods.** Touch only the
  `vyv-rf-*` pods your brief gives you. Never touch `vy-*` pods, `vy-control-verity`, or another lane's pod. Every pod in
  your brief is registered in `$RESEARCH_MACHINES_D` with guard 90. New pods:
  `research pods create --name vyv-rf-<lane>-<purpose> ... --register --project verity --guard 90`, the cheapest shape
  that answers the question.
- Runs: `research run --on <pod> --project verity --custody-r2 --source <clean worktree> --cwd source -- ...`. Inspect on
  the pod (`research pods ssh <pod> -- '...'`), or from R2. Copy only small text to the VM. Kill by pid, never
  `pkill -f` over ssh.
- Clean trees for `--source` (a base tree, for example): `git worktree add /workspace-wt/<name> <sha>`.

## Git
- Your branch is `lane/vllm-rf-<lane>` (name in your brief), cut from the start commit in your brief. If your brief
  orders a rebase, do it **before your first push**, so you never need force. Push after every commit
  (`git push -u origin lane/vllm-rf-<lane>`). No amend. If pushing `lane/*` is refused, push `cursor/vllm-rf-<lane>-<suffix>`
  and name it in your first checkpoint.
- Never commit to your predecessor's branch or any `wip/*` branch.
- Invariants and file ownership: WAVE2_BRIEF.md ("Invariants", "File ownership"). No Program, manifest, commitment root,
  leaf id or regression verdict changes; no allowlist grows.

## Gates (WAVE2_BRIEF "Gates"), with these substitutions
- `~/.research/notes/lanes/vllm-rf-a1/baseline-jdiff.py` and a23b's `gate_a-t0t1-base-72884c8a-samepod.xml.gz` aren't in
  the mirror. Copies are in `$STORE/internal/lanes/vllm-coordinator/gate-tools/` (sha256 `363304c0…` and `15a0f7fe…`).
  Copy them to your pod, for example `research pods ssh <pod> -- 'cat > /workspace/baseline-jdiff.py' < <file>`.
- Gate (b) head and base always run on the same pod.
- **Gate (b) procedure (from 2026-09-25 22:55Z; gc2).** Run gate (b), head and base, **in a git clone of the shipped
  commit**, not the shipped tree (it has no `.git`, and `test_source_identity` needs one). Clone `$RESEARCH_SOURCE_SHA` from
  the pod's bare repo `<root>/git/verity.git` (fed by `research run`'s git transport), and check that the clone matches the
  shipped tree (`diff -rq -x .git -x __pycache__ -x READY.json` gives 0 entries). The working script is
  `$STORE/internal/lanes/vllm-coordinator/gate-tools/gate_b2.sh` (gc2's, with its bootstrap and pin steps). Send it with
  `research run ... --send gate_b2.sh`.
- **`verity_sampled_proofs` on post-PR #29 trees (any tree containing `948a9c7e`).** Every gate or row script that sets its
  own `PYTHONPATH` (the gate (b) recipe, a5's `gate_a.sh`, c4ir's `reg_gate_a.sh`, row scripts) must append
  `$T/protocols/sampled_proofs`. **`fee32f05` only adds it inside `pod_bootstrap.sh`'s own environment and readiness
  check**, not to scripts that export their own PYTHONPATH. Print `python -c "import verity_sampled_proofs"` in the gate
  log. Without it, about 437 tests fail to collect and 31 fail, on both sides, and the jdiff hides it.
- **Fixture keys (owner-approved 16:56Z; the VM plays the laptop's role).** Prefer a pod whose local store already
  holds all 26 rows' fixtures (`/workspace/research/store`: a5-t1 and c4ir-reg). Point your tree at it with
  `RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml`, as
  `/workspace/a5/gate_a.sh` on a5-t1 does. Copy that script into your own directory on the pod; don't edit the original.
  Otherwise, mint a key **on your VM** and pipe it into **your own** pod. The conditions:
  - The parent key (`AWS_*` / `R2_*` in your VM's environment) never leaves the VM. Never mint on a pod.
  - The minted key is read-only, lasts 3 hours or less, and is scoped to the prefixes a fixture fetch reads. Fixtures are
    content-addressed artifacts, so those are the manifests and blobs; attempts, labels and the steward lease stay out:
    `research data mint-credential --ttl 3h --permission object-read-only --prefix manifests/ --prefix objects/sha256/ --via local --env | research pods ssh <your pod> -- 'umask 077; cat > /root/r2ro.env'`.
    Never echo it, and never put it in argv or a file on the VM.
  - Delete `/root/r2ro.env` on the pod right after the fetch, and unset `AWS_*` there. Then run gate (a) without a key:
    `$RESEARCH_NOTES/lanes/vllm-rf-a1/baseline.md` has the prefetch-then-delete recipe, and a5-t1's
    `/workspace/a5/prefetch.sh` is a working copy.
  - Log each mint in your lane report (`research notes checkpoint ...`): the UTC time, the pod, the TTL, the scope, and
    the time the key was deleted from the pod. Never log the credential itself.
- **VU export, on by default (owner-approved 2026-09-26 02:12Z; PR #42).** Every `verity-vllm row` Commit exports a sample of the
  row's VUs as benchmark instance sets, after pair 0's replay passes (256 VUs per family, 600 s budget, about 190 MB for #101).
  The output lands in `$RESEARCH_RUN_DIR/vu-export/<row>/` with `provenance.json`, and `--custody-r2` preserves it with the run. It
  never changes a verdict. Opt out with `VU_EXPORT=0`. **Until the export runs after the verdict is written, set `VU_EXPORT=0` on
  memory-tight rows** (admission headroom under about 20%: #60, #67, #68, #11, #39, #73, B=8 rows on 1x L40S), because an
  OOM in its forked pool would lose the Commit's record. TP rows aren't covered yet. Budget the disk: about 200 MB per row per run.
- **Partition invariants in every review gate (from 2026-09-26 20:48Z; the no-recompute rule in `docs/project-context.md`).** Any
  change that adds or restates a Definition, a query or a partition must show the partition checker passing on the affected
  Definitions: strict partition (every gate in exactly one unit), committed boundaries only, ports within the width rule, **and the
  recompute check at 0 recomputed gates**. Put the checker's output (units, committed words, recomputed gates) in the merge-ready
  handoff. The coordinator doesn't approve without it.
- GPU rows are compared with their regression record: program_digest, manifest_digest, run root and verdict.
- No pytest, torch or builds on your VM. Gates and measurements run on pods.

## Notes
- **No waiting in a running turn (effective 2026-09-25 17:19Z; Cursor caps concurrent cloud agents at 8).** You never
  stay in a running turn while a pod job runs. Start the job detached on the pod with custody
  (`research run --on <pod> --project verity --custody-r2 ...`, or `nohup`/`setsid` under a `--custody-r2` run). Then write
  a checkpoint in exactly this form, and end your turn:
  `research notes checkpoint vllm-rf-<lane> open "WAIT <pod> <run id> check-back <HH:MMZ> agent <your bc-id>: <what finishes>"`
  (one WAIT per run; list several in one checkpoint if you have several). The coordinator's 30-minute sweep checks those
  runs on the pods. When one finishes, or passes its check-back time, the root sends you a wake-up message. On waking,
  read your STATE.md and the run's result, and continue. Short commands (under about 5 minutes) may run in-turn.
- Your directory is `$RESEARCH_NOTES/lanes/vllm-rf-<lane>/`. Start `STATE.md` there by copying your predecessor's
  STATE.md, and say at the top that you succeed it (agent id, start commit, restart at 16:03Z). Keep the predecessor's
  sections: Running, Next, Open questions, Found-not-fixed. `READY.md` goes beside it at the end.
- Liveness: `research notes checkpoint vllm-rf-<lane> open "..."` at least every 12 minutes while working. Update
  STATE.md at every milestone. The coordinator reads both straight from the store.
- **Pod handovers between lanes:** when your brief says a pod passes to another lane, don't terminate it. Leave nothing
  running on it, write the handoff to `$RESEARCH_NOTES/lanes/vllm-rf-<target>/<YYYYMMDDTHHMMZ>-handoff-from-vllm-rf-<lane>.md`
  (what's on it, where the venv, trees and fixtures are), and name the handover in a checkpoint. The receiving lane
  touches the pod only after that handoff exists. If the target lane isn't running, terminate the pod instead.
- To the coordinator (merge-ready, blockers, deadline asks):
  `$RESEARCH_NOTES/lanes/vllm-coordinator/<YYYYMMDDTHHMMZ>-handoff-from-vllm-rf-<lane>.md`, with a header of
  `lane`, `kind: handoff`, `from`, `created`. A merge-ready handoff gives the branch and head, the base, the gates
  (commands, counts, run ids, evidence paths), behaviour changes, what deliberately didn't change, and found-not-fixed.
- Don't run `research notes sync`, `push` or `snapshot`.

## Money and deadline
- vLLM's cap is $623, owner-held. At 16:13Z spend was $474 at $16.11/h. No new work that would take the project past
  about $610. Your brief gives your lane's cap on new spend; ask before passing it.
- **The vyv- deadline is 2026-09-25T20:30Z (1:30 PM PT).** At that time the guard terminates every vyv- pod. The
  coordinator extends it in steps of at most 4 h while lanes need pods. If a run of yours would pass it, send a handoff
  early with the pod and the expected end time.
- Terminate every pod as soon as its runs are in R2 (`research data preserved <run>`), unless your brief hands it on.

## Finish
- READY.md, pods terminated or handed over, merge-ready handoff to the coordinator, then
  `research notes checkpoint vllm-rf-<lane> final "..." --require-pushed` (pods terminated, spend).
- Final reply of 250 words or fewer: head, gates, READY.md path, pods, spend, blockers. Times in PT in prose.
