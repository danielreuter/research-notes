#!/bin/sh
exec ssh -i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -p 10114 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o ServerAliveInterval=30 root@213.173.102.141 "$@"
