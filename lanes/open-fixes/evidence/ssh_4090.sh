#!/usr/bin/env bash
# usage: ssh_4090.sh <cmd...>   (pod vy-open-fixes)
exec ssh -i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -p 42516 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o ServerAliveInterval=30 -o ConnectTimeout=20 root@157.157.221.29 "$@"
