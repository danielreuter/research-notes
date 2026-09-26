#!/bin/bash
# copycommit.sh RUNID: copy the Commit re-run outputs (sweep/*/commit/, verdict.json, stages.txt, row.log, commit.log; files < 50 MB)
# of the recording run RUNID into this run for custody (the recording run published before the Commits re-ran).
S=/workspace/research/runs/$1/sweep; D=$RESEARCH_RUN_DIR/commit-copy; mkdir -p $D
cd $S && find . \( -path "*/commit/*" -o -name verdict.json -o -name stages.txt -o -name row.log -o -name commit.log -o -name admission.json \) -type f -size -50M -print0 | tar --null -T - -czf $D/commits-lt50M.tgz
find . -path "*/commit/*" -type f -size +50M -printf "%s %p\n" > $D/omitted-ge50M.txt
ls -la $D
