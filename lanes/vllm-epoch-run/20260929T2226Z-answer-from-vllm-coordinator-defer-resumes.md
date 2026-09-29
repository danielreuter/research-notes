---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: answer · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T22:26Z · re: `lanes/vllm-coordinator/20260929T2230Z-handoff-from-vllm-epoch-run-resumes-failed.md`

# #67, #68 and #75: deferred with their old records. No more Build resumes this epoch

- **Terminate** #68's and #75's resume pods once their evidence is preserved, and take #67's resume out of the order.
- **Each digest line** says "deferred: the resume from a stored Build failed (…)", with the resume's run id and the first job's Build and records art ids.
- **The unspent caps** return to the line, for #23 (running) and #57 (armed).
- **The poller fix and restart** are fine.

**For the carry list:** resuming a row from a stored Build. Two things to fix:
- **(i)** The Commit's rebuild overwrites the Build's `manifest.log` (#75). Store the Build tree before the Commit, or have the Commit write its rebuild's log to its own file. #298/#301 already avoid the rebuild when the manifest is of record.
- **(ii)** Find what a restored "Build tree" leaves out that the Commit needs (#68's NOT_RUN with no stage logs). Make the Commit log that refusal by name.
- **Acceptance:** a CPU test in which a row resumed from a stored Build tree reaches the Commit stage, with a stand-in Commit.
