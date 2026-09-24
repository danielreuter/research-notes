---
lane: merge-postwave
kind: handoff
from: coordinator
created: 2026-09-24T17:32Z
---

# coordinator -> merge-postwave: main moved to f08314ae; merge it (instead of e7d4a978) as your first merge; your pod now has guard = 90

main now = e7d4a978 + lane/pod-runs + origin's vllm-cleanup-2 (72884c8a; 977 files, mostly integrations/vllm relayout).
If you already merged e7d4a978, just add one more merge of main f08314ae. The CLI (`~/.research/bin/research`) now runs
f08314ae: `research run --on --source` streams the tree (launcher <= 40 MiB; the 16:55Z guardian kill of your 0.64 GB
launcher will not recur), and the next launch on vy-merge-postwave starts the pod-side guard (machines.toml `guard = 90`):
it terminates the pod after 90 idle minutes only once every run is fetched, so run `research fetch <run> --all` for each
run. Still terminate the pod yourself at FINAL. Laptop disk is now 16 GiB free.
Known pre-existing failure on main: test_pythonpath.py::test_this_repository_resolves_every_workspace_package_inside_the_tree.
