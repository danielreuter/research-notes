"""Create a RunPod pod in a data center the REST enum rejects (US-MO-1), via GraphQL (after lanes/d3-h100/evidence/gql_*.py).

    PYTHONPATH=tools/research/src python3 gql_pod.py gpu NAME DC "NVIDIA H100 80GB HBM3" [DISK_GB]
    PYTHONPATH=tools/research/src python3 gql_pod.py cpu NAME DC cpu3c-16-32 [DISK_GB]
Exposes 22/tcp and 7400/tcp (the Flock verifier's listen port), public IP, PUBLIC_KEY = the campaign key.
"""
import json
import sys

from research.pods import runpod as r

kind, name, dc, what = sys.argv[1:5]
disk = int(sys.argv[5]) if len(sys.argv) > 5 else 100
common = """containerDiskInGb: %d, dataCenterId: %s, name: %s, imageName: %s, startSsh: true, supportPublicIp: true,
  ports: "22/tcp,7400/tcp", env: [{key: "PUBLIC_KEY", value: %s}]""" % (
    disk, json.dumps(dc), json.dumps(f"{name}-veritor-campaign"), json.dumps(r.DEFAULT_IMAGE), json.dumps(r.public_key()))
if kind == "gpu":
    q = "mutation { podFindAndDeployOnDemand(input: {cloudType: SECURE, gpuCount: 1, gpuTypeId: %s, volumeInGb: 0, %s}) { id costPerHr } }" % (json.dumps(what), common)
else:
    q = "mutation { deployCpuPod(input: {instanceId: %s, cloudType: SECURE, %s}) { id } }" % (json.dumps(what), common)
print(json.dumps(r._graphql(q), indent=1))
