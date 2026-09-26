"""flock-l40s-101: a community verifier pod in one country (the REST `countryCodes` filter `research pods create` lacks), so it
can sit next to a community prover. Refuses when a live pod of the name exists; register it afterwards with
`research pods register NAME --pod-id ID --project verity --guard N`."""
import json
import sys

from research.pods import runpod

name, country, *gpus = sys.argv[1:]
full = f"{name}-veritor-campaign"
live = [p for p in runpod._request("GET", "/pods") or [] if p.get("name") == full and p.get("desiredStatus") != "TERMINATED"]
if live:
    sys.exit(f"refused: {full} exists ({[p['id'] for p in live]})")
body = {"name": full, "imageName": runpod.DEFAULT_IMAGE, "gpuTypeIds": gpus, "gpuCount": 1, "cloudType": "COMMUNITY",
        "computeType": "GPU", "containerDiskInGb": 60, "volumeInGb": 0, "ports": ["22/tcp", "7400/tcp"], "supportPublicIp": True,
        "countryCodes": [country], "minVCPUPerGPU": 8, "env": {"PUBLIC_KEY": runpod.public_key()}}
pod = runpod._request("POST", "/pods", body)
print(json.dumps({k: pod.get(k) for k in ("id", "name", "costPerHr", "publicIp", "portMappings", "vcpuCount", "machine")}, indent=1))
