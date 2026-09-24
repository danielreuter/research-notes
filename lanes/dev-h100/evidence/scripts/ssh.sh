#!/bin/bash
exec ssh -i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -p 14998 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o ServerAliveInterval=30 -o BatchMode=yes -o ConnectTimeout=20 root@64.247.201.59 "$@"
