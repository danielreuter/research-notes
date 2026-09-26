"""flock-l40s-101: deploy a pod through GraphQL podFindAndDeployOnDemand, for GPU types the REST enum lacks (MIG slices).
Refuses when a live pod of the name exists; register with `research pods register`.
    python create-pod-gql.py NAME GPU_TYPE_ID DATA_CENTER [MIN_VCPU]"""
import json
import sys

from research.pods import runpod

name, gpu, dc, *rest = sys.argv[1:]
full = f"{name}-veritor-campaign"
live = [p for p in runpod._request("GET", "/pods") or [] if p.get("name") == full and p.get("desiredStatus") != "TERMINATED"]
if live:
    sys.exit(f"refused: {full} exists ({[p['id'] for p in live]})")
s = json.dumps
fields = (f"cloudType: SECURE, gpuCount: 1, gpuTypeId: {s(gpu)}, dataCenterId: {s(dc)}, name: {s(full)}, "
          f"imageName: {s(runpod.DEFAULT_IMAGE)}, containerDiskInGb: 60, volumeInGb: 0, ports: \"22/tcp,7400/tcp\", startSsh: true, "
          f"supportPublicIp: true, minVcpuCount: {int(rest[0]) if rest else 8}, "
          f"env: [{{key: \"PUBLIC_KEY\", value: {s(runpod.public_key())}}}]")
q = "mutation { podFindAndDeployOnDemand(input: {" + fields + "}) { id name costPerHr vcpuCount machine { dataCenterId gpuTypeId } } }"
r = runpod._graphql(q)
print(json.dumps(r)[:1500])
