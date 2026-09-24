#!/bin/bash
exec ssh -i ~/.runpod/ssh/runpodctl-ssh-key -p 12819 -o StrictHostKeyChecking=no -o UserKnownHostsFile=~/.runpod/ssh/veritor-campaign-known_hosts -o ServerAliveInterval=30 -o ConnectTimeout=20 root@154.54.102.38 "$@"
