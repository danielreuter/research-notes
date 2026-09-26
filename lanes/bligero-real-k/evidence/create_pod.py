"""create a RunPod pod with REST fields `research pods create` lacks (countryCodes, dataCenterIds, globalNetworking); refuses a live duplicate.
usage: create_pod.py NAME CLOUD DISK PORTS(comma) [--country C] [--dc DC] GPU..."""
import argparse, json, sys
from research.pods import runpod
ap = argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("cloud"); ap.add_argument("disk", type=int); ap.add_argument("ports")
ap.add_argument("--country", action="append", default=[]); ap.add_argument("--dc", action="append", default=[]); ap.add_argument("gpus", nargs="+")
a = ap.parse_args()
full = f"{a.name}-veritor-campaign"
if [p for p in runpod._request("GET", "/pods") or [] if p.get("name") == full and p.get("desiredStatus") != "TERMINATED"]:
    sys.exit(f"refused: {full} exists")
body = {"name": full, "imageName": runpod.DEFAULT_IMAGE, "gpuTypeIds": a.gpus, "gpuCount": 1, "cloudType": a.cloud, "computeType": "GPU",
        "containerDiskInGb": a.disk, "volumeInGb": 0, "ports": [f"{p}/tcp" for p in a.ports.split(",")], "supportPublicIp": True,
        "minVCPUPerGPU": 8, "env": {"PUBLIC_KEY": runpod.public_key()}}
if a.country: body["countryCodes"] = a.country
if a.dc: body["dataCenterIds"] = a.dc
try:
    pod = runpod._request("POST", "/pods", body)
except runpod.PodError as e:
    sys.exit(f"create failed: {str(e)[:200]}")
m = pod.get("machine") or {}
print(json.dumps({"id": pod.get("id"), "cost": pod.get("costPerHr"), "gpu": m.get("gpuTypeId"), "location": m.get("location"), "dc": m.get("dataCenterId")}))
