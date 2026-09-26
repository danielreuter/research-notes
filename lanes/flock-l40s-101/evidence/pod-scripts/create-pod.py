"""flock-l40s-101: create a pod with the REST filters `research pods create` lacks (`countryCodes`, `allowedCudaVersions`), so a
prover lands on a host whose driver runs CUDA 13 (Flock's f128.cuh needs PTX `clmad`: nvcc 12.4 has no such instruction, and
an R550 host refuses the 13.3 compat libcuda) and a verifier next to it. Refuses when a live pod of the name exists; register
it afterwards with `research pods register NAME --pod-id ID --project verity --guard N`.

    python create-pod.py NAME --gpu "NVIDIA L40S" [--gpu ...] [--cloud COMMUNITY|SECURE] [--country SE] [--dc US-MO-1]
                         [--cuda 12.8 --cuda 12.9 --cuda 13.0] [--port 7400] [--min-vcpu 8] [--global-net]"""
import argparse
import json
import sys

from research.pods import runpod

ap = argparse.ArgumentParser()
ap.add_argument("name")
ap.add_argument("--gpu", action="append", required=True)
ap.add_argument("--cloud", default="SECURE", choices=["SECURE", "COMMUNITY"])
ap.add_argument("--country", action="append", default=[])
ap.add_argument("--dc", action="append", default=[])
ap.add_argument("--cuda", action="append", default=[])
ap.add_argument("--port", action="append", type=int, default=[])
ap.add_argument("--min-vcpu", type=int, default=8)
ap.add_argument("--disk", type=int, default=100)
ap.add_argument("--global-net", action="store_true", help="RunPod global networking (<pod id>.runpod.internal between pods)")
a = ap.parse_args()
full = f"{a.name}-veritor-campaign"
live = [p for p in runpod._request("GET", "/pods") or [] if p.get("name") == full and p.get("desiredStatus") != "TERMINATED"]
if live:
    sys.exit(f"refused: {full} exists ({[p['id'] for p in live]})")
body = {"name": full, "imageName": runpod.DEFAULT_IMAGE, "gpuTypeIds": a.gpu, "gpuCount": 1, "cloudType": a.cloud, "computeType": "GPU",
        "containerDiskInGb": a.disk, "volumeInGb": 0, "ports": ["22/tcp", *(f"{p}/tcp" for p in a.port)], "supportPublicIp": True,
        "minVCPUPerGPU": a.min_vcpu, "env": {"PUBLIC_KEY": runpod.public_key()}}
if a.country:
    body["countryCodes"] = a.country
if a.dc:
    body["dataCenterIds"] = a.dc
if a.cuda:
    body["allowedCudaVersions"] = a.cuda
if a.global_net:
    body["globalNetworking"] = True
try:
    pod = runpod._request("POST", "/pods", body)
except runpod.PodError as e:
    sys.exit(f"create failed: {e}")
print(json.dumps({k: pod.get(k) for k in ("id", "name", "costPerHr", "publicIp", "vcpuCount", "machine", "globalNetworking")}))
