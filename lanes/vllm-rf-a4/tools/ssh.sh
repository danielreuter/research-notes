# source me: rssh (reg pod), gssh (gpu pod), pssh (cpu pod)
_o() { echo -i $HOME/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=$HOME/.runpod/ssh/veritor-campaign-known_hosts -o LogLevel=ERROR -o ConnectTimeout=15 -o ServerAliveInterval=30; }
pssh() { ssh -i $HOME/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=$HOME/.runpod/ssh/veritor-campaign-known_hosts -o LogLevel=ERROR -o ConnectTimeout=15 -p 34096 root@91.199.227.82 "$@"; }
rssh() { ssh -i $HOME/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=$HOME/.runpod/ssh/veritor-campaign-known_hosts -o LogLevel=ERROR -o ConnectTimeout=15 -p 18748 root@154.54.102.49 "$@"; }
gssh() { ssh -i $HOME/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=$HOME/.runpod/ssh/veritor-campaign-known_hosts -o LogLevel=ERROR -o ConnectTimeout=15 -p 27798 root@81.27.69.178 "$@"; }
