#!/bin/bash
# vyv-rf-b4b-g1: #101 build,match,commit (FA2 matReq tap) + non-interference at the shipped tree ($PWD), via b4c's scripts
# (outputs /workspace/b4c/b5vab-head/); MAX_JOBS=12 for the FA2 tap build.
export MAX_JOBS=12
echo "start $(date -u +%FT%TZ) src $PWD"
bash /workspace/b4c/g1_cli.sh b5vab-head
bash /workspace/b4c/nonint_cli.sh b5vab-head
echo "done $(date -u +%FT%TZ)"
