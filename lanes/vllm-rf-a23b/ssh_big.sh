#!/bin/bash
# ssh to vyv-rf-a23b-big (RunPod n2ei0ahhoeu80j); if the port moved, `research pods ssh n2ei0ahhoeu80j --print` has the new one.
exec ssh -i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -p 21626 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o ServerAliveInterval=30 -o LogLevel=ERROR root@213.173.111.105 "$@"
