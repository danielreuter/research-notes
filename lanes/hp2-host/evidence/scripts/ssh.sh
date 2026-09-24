#!/bin/bash
exec ssh -o StrictHostKeyChecking=no -o ConnectTimeout=20 -o ServerAliveInterval=30 -o BatchMode=yes -o UserKnownHostsFile=$HOME/.runpod/ssh/veritor-campaign-known_hosts -i $HOME/.runpod/ssh/runpodctl-ssh-key -p 11946 root@47.47.180.108 "$@"
