"""Create a RunPod CPU pod in a data center the REST enum rejects (US-MO-1, US-NE-1), via GraphQL deployCpuPod.

    PYTHONPATH=<worktree>/tools/research/src python3.13 gql_cpu_pod.py NAME DC INSTANCE_ID [DISK_GB]
    INSTANCE_ID e.g. cpu3c-16-32 (flavor-vCPU-GB). Exposes 22/tcp and 7000/tcp, public IP, PUBLIC_KEY = the campaign key.
"""
import json
import sys

from research.pods import runpod as r

name, dc, inst = sys.argv[1:4]
disk = int(sys.argv[4]) if len(sys.argv) > 4 else 40
key = r.SSH_KEY.with_suffix(".pub").read_text().strip()
q = """mutation { deployCpuPod(input: {instanceId: %s, cloudType: SECURE, containerDiskInGb: %d, dataCenterId: %s,
  name: %s, imageName: %s, startSsh: true, supportPublicIp: true, ports: "22/tcp,7000/tcp",
  env: [{key: "PUBLIC_KEY", value: %s}]}) { id imageName machineId } }""" % (
    json.dumps(inst), disk, json.dumps(dc), json.dumps(f"{name}-veritor-campaign"), json.dumps(r.DEFAULT_IMAGE), json.dumps(key))
print(json.dumps(r._graphql(q), indent=1))
