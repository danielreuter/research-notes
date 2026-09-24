#!/usr/bin/env bash
# usage: ssh_h100.sh <cmd...>   (pod vy-open-fixes-h100)
exec ssh -i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -p 10144 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o ServerAliveInterval=30 -o ConnectTimeout=20 root@103.207.149.105 "$@"
