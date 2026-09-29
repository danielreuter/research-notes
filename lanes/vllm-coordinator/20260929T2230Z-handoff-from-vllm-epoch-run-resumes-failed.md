---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff (resumes failed) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-29T22:30Z

**The Build resumes do not work as built. Both in-place resumes failed after their Build step, and I have held #67's resume, which is the same approach.**

- **#75** (`r20260929-214119-f482`, $1.43): the Build reuse and Match (FAIL on a FAIL row, as expected) went through. Then the strict word check FAILed: "manifest.log has 0 Q_word lines, fewer than the 4 components". In the first job the same check passed 4/4. So the Build's `manifest.log` was most likely rewritten by the first job's Commit before the cut (the Commit rebuilds the manifest on its query path). The Build tree was stored after that, so a restore from the store would carry the same file. `finish` stored everything and terminated the pod; the new Build/records/capture arts are `art:9f4b8f9d…`, `art:b9fffd92…` and `art:6267276b…`.
- **#68** (`r20260929-212049-6e37`, about $2.3): the Build reuse, Match (PASS) and strict word check (32/32 PASS) all passed. Then the Commit ran 896 s and ended NOT_RUN, with 0 runs, every check NOT_RUN and manifest-verify not-run. Its `commit/` dir holds only `versions.json` and `source_identity.json`, with no stage logs, so the cause is not visible from here. It may be something the Commit expects that the "Build tree" (the row dir without match/, commit/, vu-export/) leaves out, or state the first job left behind. Its watcher will finish it (store, record stage, HOLD, terminate).
- **#67:** its resume is held (taken out of the poller's order), since it would restore the same kind of Build tree.

**For you:** defer #67, #68 and #75 with their old records, or have the resume investigated first (the tooling is in my lane: `resume-bin/`, `fu.py resume-here`). The preserved evidence of all their jobs stays in the store. I recommend deferring tonight, and adding "resume a row from a stored Build" to the carry list, with a CPU test that a resumed row reaches a Commit.

**Also:**
- #23 launched at 22:06Z on 2× L40 SECURE ($1.64/h, 572 GB, cap $18).
- The poller exited at about 22:22Z when only gated rows were left. It is fixed and restarted, and #57 stays armed; `main` does not contain `a246eb78` yet.
- Committed spend is $214.98.
