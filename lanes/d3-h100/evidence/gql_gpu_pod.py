"""Create a RunPod GPU pod in a data center the REST enum rejects (US-MO-1), via GraphQL podFindAndDeployOnDemand.

    PYTHONPATH=<worktree>/tools/research/src python3.13 gql_gpu_pod.py NAME DC GPU_TYPE [DISK_GB]
"""
import json
import sys

from research.pods import runpod as r

name, dc, gpu = sys.argv[1:4]
disk = int(sys.argv[4]) if len(sys.argv) > 4 else 100
key = r.SSH_KEY.with_suffix(".pub").read_text().strip()
q = """mutation { podFindAndDeployOnDemand(input: {cloudType: SECURE, gpuCount: 1, gpuTypeId: %s, dataCenterId: %s,
  containerDiskInGb: %d, volumeInGb: 0, name: %s, imageName: %s, startSsh: true, supportPublicIp: true,
  ports: "22/tcp,7000/tcp", env: [{key: "PUBLIC_KEY", value: %s}]}) { id imageName machineId costPerHr } }""" % (
    json.dumps(gpu), json.dumps(dc), disk, json.dumps(f"{name}-veritor-campaign"), json.dumps(r.DEFAULT_IMAGE), json.dumps(key))
print(json.dumps(r._graphql(q), indent=1))
