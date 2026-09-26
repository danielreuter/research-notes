"""GPU (podFindAndDeployOnDemand) or CPU (deployCpuPod) pod in a DC the REST enum rejects (US-MO-1).
usage: gql_pod.py gpu NAME DC GPU_TYPE DISK | gql_pod.py cpu NAME DC INSTANCE_ID DISK"""
import json, sys
from research.pods import runpod as r
kind, name, dc, what, disk = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
key = r.public_key()
common = (f'containerDiskInGb: {disk}, dataCenterId: {json.dumps(dc)}, name: {json.dumps(name + "-veritor-campaign")}, '
          f'imageName: {json.dumps(r.DEFAULT_IMAGE)}, startSsh: true, supportPublicIp: true, ports: "22/tcp,7000/tcp", '
          f'env: [{{key: "PUBLIC_KEY", value: {json.dumps(key)}}}]')
if kind == "gpu":
    q = f"mutation {{ podFindAndDeployOnDemand(input: {{cloudType: SECURE, gpuCount: 1, gpuTypeId: {json.dumps(what)}, volumeInGb: 0, {common}}}) {{ id machineId costPerHr }} }}"
else:
    q = f"mutation {{ deployCpuPod(input: {{instanceId: {json.dumps(what)}, cloudType: SECURE, {common}}}) {{ id machineId costPerHr }} }}"
try:
    print(json.dumps(r._graphql(q)))
except Exception as e:
    print("error:", str(e)[:300])
