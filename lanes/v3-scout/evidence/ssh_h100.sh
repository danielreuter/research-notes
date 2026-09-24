#!/bin/bash
exec ssh -i ~/.runpod/ssh/runpodctl-ssh-key -p 13884 -o StrictHostKeyChecking=no -o UserKnownHostsFile=~/.runpod/ssh/veritor-campaign-known_hosts -o ServerAliveInterval=30 -o ConnectTimeout=20 root@31.24.80.44 "$@"
