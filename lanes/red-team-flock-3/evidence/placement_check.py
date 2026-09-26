#!/usr/bin/env python3
"""red-team-flock-3: were an attention cell's prover and verifier on different physical machines? (red-team-flock's ruling: a
verifier on the prover's machine is not a separate verifier.) From each run's own record (job.json `environment`, which the
research runner writes on the machine, and the cell script's `out/host.txt`): the kernel boot id (containers on one host share
the host kernel, so one boot id), kernel release, host memory, CPU model, GPU name / UUID / driver; and from the cell, the
address the prover dialled (a 172.16/12 docker bridge would be host-private; RunPod global networking is 10.x, routed).

  placement_check.py ART...     -> one PLACEMENT line per cell: SEPARATE | CO-RESIDENT | UNKNOWN

With PR74=<path to main's bench/placement.py>, each pair also goes through PR #74's `separation(prover, verifier, link)`, the
identities merged from the records (boot id, CPU model) and the RunPod API for the pod each attempt recorded
(execution.remote.pod_id -> machineId, publicIp; read-only), the link being the address the prover dialled. `pr74` lists its
reasons; empty = separate machines on an accepted link.
"""
import importlib.util
import ipaddress
import json
import os
import subprocess
import sys
from pathlib import Path

TREES = Path.home() / ".research/store/trees"


def sh(*a):
    return subprocess.run(["research", *a], capture_output=True, text=True).stdout


def record_of(run):
    out = sh("data", "show", run)
    for line in out.splitlines():
        if line.startswith("outputs"):
            return json.loads(line.split(None, 1)[1]).get("run_record")
    return None


_PODS = {}


def pod_of(run):
    for line in sh("data", "show", run).splitlines():
        if line.startswith("execution"):
            return (json.loads(line.split(None, 1)[1]).get("remote") or {}).get("pod_id")
    return None


def runpod_ident(pod_id):
    if pod_id and pod_id not in _PODS:
        from research.pods import runpod
        p = runpod.get(pod_id)
        _PODS[pod_id] = {"machine_id": p.get("machineId") or None, "public_ip": p.get("publicIp") or None}
    return _PODS.get(pod_id, {})


def host(run):
    art = record_of(run)
    if not art:
        return {"run": run, "error": "no run record"}
    sh("data", "fetch", art, "--path", "job.json", "--path", "out/host.txt")
    d = TREES / art[4:]
    try:
        e = json.loads((d / "job.json").read_text())["environment"]
    except (OSError, KeyError, ValueError) as x:
        return {"run": run, "record": art, "error": f"job.json: {x}"}
    txt = (d / "out/host.txt").read_text() if (d / "out/host.txt").exists() else ""
    cpu = next((l.split(":", 1)[1].strip() for l in txt.splitlines() if l.startswith("Model name")), None)
    g = (e.get("gpu") or {}).get("devices") or [{}]
    pod = pod_of(run)
    return {"run": run, "record": art[:12], "boot_id": e.get("boot_id"), "kernel": e.get("kernel"), "hostname": e.get("hostname"),
            "mem": e.get("host_memory_total_bytes"), "cpu": cpu, "gpu": g[0].get("name"), "gpu_uuid": g[0].get("uuid"),
            "driver": g[0].get("driver"), "pod_id": pod, **runpod_ident(pod)}


def main():
    for a in sys.argv[1:]:
        meta = next(json.loads(l.split(None, 1)[1]) for l in sh("data", "show", a).splitlines() if l.startswith("meta"))
        wf = meta["workload_fingerprint"]
        T = wf["software"]["backend"]["unit"].split("/")[-1]
        pr, vr = meta["derived_from"]["prover_run"], meta["derived_from"]["verifier_run"]
        p, v = host(pr), host(vr)
        addr = (wf.get("verifier") or {}).get("placement", "")
        ip = addr.rsplit(":", 1)[0]
        try:
            bridge = ipaddress.ip_address(ip) in ipaddress.ip_network("172.16.0.0/12")
            net = "docker-bridge 172.16/12 (host-private)" if bridge else ("routed " + ("10/8 (RunPod global networking)" if ip.startswith("10.") else "public"))
        except ValueError:
            bridge, net = None, f"unparsed {addr!r}"
        diff = {k: (p.get(k), v.get(k)) for k in ("boot_id", "kernel", "mem", "cpu", "gpu", "gpu_uuid", "driver")}
        differing = [k for k, (x, y) in diff.items() if x is not None and y is not None and x != y]
        if p.get("boot_id") and v.get("boot_id"):
            verdict = "SEPARATE" if p["boot_id"] != v["boot_id"] else "CO-RESIDENT"
        else:
            verdict = "UNKNOWN"
        if bridge:
            verdict = "CO-RESIDENT"
        pr74 = None
        if os.environ.get("PR74"):
            spec = importlib.util.spec_from_file_location("pr74_placement", os.environ["PR74"])
            m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
            ident = lambda h: {"boot_id": h.get("boot_id"), "cpu_model": h.get("cpu"), "hostname": h.get("hostname"),  # noqa: E731
                               "pod_id": h.get("pod_id"), "machine_id": h.get("machine_id"), "public_ip": h.get("public_ip")}
            pr74 = m.separation(ident(p), ident(v), {"peer": addr, "peer_ip": ip})
            if pr74:
                verdict = "NOT-SHOWN-SEPARATE (PR #74)" if verdict == "SEPARATE" else verdict
        print("PLACEMENT", json.dumps({"cell": a[:12], "T": T, "verdict": verdict, "differing": differing, "network": f"{addr} {net}",
                                       "pr74": pr74, "prover": p, "verifier": v}), flush=True)


if __name__ == "__main__":
    main()
