#!/bin/bash
# rsync the hp2-host worktree (tracked + new files, no .git/.venv) to the pod's /workspace/src-hp2 for the dev loop
cd /Users/danielreuter/projects/verity-main-wt/hp2-host
exec rsync -az --delete --exclude .git --exclude .venv --exclude __pycache__ --exclude '.pytest_cache' --exclude '**/target/' \
  -e "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=20 -o BatchMode=yes -o UserKnownHostsFile=$HOME/.runpod/ssh/veritor-campaign-known_hosts -i $HOME/.runpod/ssh/runpodctl-ssh-key -p 11946" \
  ./ root@47.47.180.108:/workspace/src-hp2/ "$@"
