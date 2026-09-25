#!/bin/bash
# raw ssh to vyv-rf-f3-lint (RunPod xroshfy57ofi18, cpu3g 16 vCPU / 64 GB) -- binary-safe stdin/stdout, runs the command once
exec ssh -i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -p 11676 -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o ServerAliveInterval=30 -o LogLevel=ERROR \
  root@213.173.105.71 "$@"
