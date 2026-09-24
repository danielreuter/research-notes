#!/bin/bash
# rsync the hash-compose worktree (no .git/.venv) to the pod's /workspace/src for the dev loop
cd /Users/danielreuter/projects/verity-main-wt/hash-compose
exec rsync -az --delete --exclude .git --exclude .venv --exclude __pycache__ --exclude '.pytest_cache' --exclude '**/target/' \
  -e "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=20 -o BatchMode=yes -o UserKnownHostsFile=$HOME/.runpod/ssh/veritor-campaign-known_hosts -i $HOME/.runpod/ssh/runpodctl-ssh-key -p 39320" \
  ./ root@103.196.86.167:/workspace/src/ "$@"
