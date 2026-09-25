#!/usr/bin/env bash
# red-team-lk (laptop side): ship `git diff --binary 4bd6c54c <rev>` patches and rebuild the producer trees on the pod as
# /workspace/tree-<rev> = /workspace/src (main 4bd6c54c, synced) + patch.  Our own copies; never the producers' pods.
set -euo pipefail
O=(-i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o LogLevel=ERROR)
H=root@149.36.0.4; PORT=27178
ssh "${O[@]}" -p $PORT $H 'mkdir -p /workspace/red-team-lk/patches'
scp "${O[@]}" -P $PORT /tmp/red-team-lk-*.patch $H:/workspace/red-team-lk/patches/
ssh "${O[@]}" -p $PORT $H 'set -e; cd /workspace; for r in 3be6a35f 716ea008 b7cec878; do rm -rf tree-$r; cp -a src tree-$r; (cd tree-$r && git apply --whitespace=nowarn /workspace/red-team-lk/patches/red-team-lk-$r.patch && echo "$r ok"); done; grep -c "^BOOL_QUADRATIC" tree-*/backends/gkr/gpu/nvf4/circuit.py || true; grep -c "def merge_tables" tree-3be6a35f/backends/gkr/gpu/v2/export.py'
