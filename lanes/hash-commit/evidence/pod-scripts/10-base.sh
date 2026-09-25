#!/usr/bin/env bash
# hash-commit, 4090 fp8-ada (the Table 2 +hash cell config: l=8192 p4): the BEFORE committer (tree /workspace/src-base =
# lane/hash-commit 6e1cc576, main's committer + the --commit-reps harness), one run, reps 5, commitment built 1 + 3 times.
source /workspace/hash-commit/scripts/lib.sh
run base-fp8ada-l8192-p4-r${R:-1} /workspace/src-base fp8-ada 8192 4 5
