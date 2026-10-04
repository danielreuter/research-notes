---
id: lean/20261004T0430Z-friction-disk-hold-test-hangs-on-a-full-host
campaign: infra
lane: lean
kind: friction
status: open
repo: danielreuter/verity
origin: bc-19c498a8-628e-5c04-8f61-fe785a24741b
---

# The research suite hangs, with no end, whenever its host's disk is over 80% full

`tools/research/tests/test_remote_local.py::test_a_queued_run_with_a_disk_request_is_admitted_on_the_machine_ahead_of_its_allocation`
launches a real `research disk-hold --gb 0.001`, and `research/disk.py` admits nothing while the host's filesystem is over
`HOLD_PCT` (80%), then waits until it falls to 75%. On my agent VM (254 GB disk, 81% used by Lean build trees) the test sat
for 1,890 s, holding up the research suite of #1053's `research queue ready --local`, and would have waited forever.
It finished only once I deleted 16 GB of my own `.lake` trees. A `check` pod past 80% would hang the same way.

What I did instead: freed disk by hand. The fix I'd suggest: let the test set the thresholds (an env override that
`disk.main` reads, or a `--hold-pct` flag `remote` passes only from the request), so the test asserts admission without
reading the host's disk.
