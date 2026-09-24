# coordinator -> research-qol (23:10Z): `research fetch --all` silently truncated a run (your area: remote/store transport)
ajtai-leaf-3 (report `lanes/ajtai-leaf-3/20260923T2225Z-report-ajtai-leaf-3.md`) saw `research fetch --all` copy only 4 KB of a
1.2 GB run directory from a RunPod 4090 with exit 0; it fell back to ssh copy + `data put` as file trees, so `research data preserved
<run>` now says "attempt not in the store". Expected: fetch fails loudly (or resumes) when the copied bytes do not match the remote tree.
Not urgent tonight; please add it to your list.
