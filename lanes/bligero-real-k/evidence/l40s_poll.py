"""bligero-l40s-101: wait for an L40S prover with a same-DC verifier on ANOTHER physical host whose public ports hairpin.
Every 90 s: secure-cloud L40S stock in a DC not known to fail (flock-l40s-101 / kb live-verifier.md) -> create the prover there and
a verifier of another GPU type in the same DC, register both (idle guard), check distinct kernel boot ids and prover -> verifier
public ssh; keep the pair on success (SUCCESS line, exit 0), else drain both and keep polling. Community stock is logged only.
Log: /tmp/l40s_poll.log.  Stops after DEADLINE_S."""
import json
import subprocess
import sys
import time

from research.pods import runpod

BAD = {"EU-NL-1", "EUR-IS-2", "US-WA-1", "OC-AU-1", "CA-MTL-1"}
L40S = "NVIDIA L40S"
DEADLINE_S = 2.5 * 3600
LOG = "/tmp/l40s_poll.log"
R = ["uv", "run", "--frozen", "research"]


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%H:%M:%SZ', time.gmtime())} {msg}\n")


def create(name, dc, gpus, ports, disk):
    body = {"name": f"{name}-veritor-campaign", "imageName": runpod.DEFAULT_IMAGE, "gpuTypeIds": gpus, "gpuCount": 1, "cloudType": "SECURE",
            "computeType": "GPU", "containerDiskInGb": disk, "volumeInGb": 0, "ports": [f"{p}/tcp" for p in ports], "supportPublicIp": True,
            "dataCenterIds": [dc], "minVCPUPerGPU": 8, "env": {"PUBLIC_KEY": runpod.public_key()}}
    try:
        pod = runpod._request("POST", "/pods", body)
        return pod["id"], (pod.get("machine") or {}).get("gpuTypeId")
    except runpod.PodError as e:
        log(f"{name} in {dc}: {str(e)[:120]}")
        return None, None


def sh(name, cmd):
    r = subprocess.run([*R, "pods", "ssh", name, "--", cmd], capture_output=True, text=True, cwd="/workspace", timeout=120)
    return "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "setlocale" not in l).strip()


def drain(name):
    subprocess.run([*R, "pods", "drain", name], capture_output=True, text=True, cwd="/workspace", timeout=1800)


def ports_of(pid):
    for _ in range(20):
        p = runpod._request("GET", f"/pods/{pid}") or {}
        if p.get("publicIp") and p.get("portMappings"):
            return p["publicIp"], p["portMappings"]
        time.sleep(10)
    return None, None


def attempt(dc, avail):
    pid, _ = create("vy-bligero-l40s-101", dc, [L40S], [22], 150)
    if not pid:
        return False
    others = [g for g in avail if g != L40S] or ["NVIDIA RTX A6000", "NVIDIA A40", "NVIDIA GeForce RTX 4090"]
    vid, vgpu = create("vy-bligero-l40s-101-ver", dc, others, [22, 7000], 60)
    if not vid:
        log(f"no verifier next to prover {pid} in {dc}; terminating it")
        runpod._request("DELETE", f"/pods/{pid}")
        return False
    for name, i in (("vy-bligero-l40s-101", pid), ("vy-bligero-l40s-101-ver", vid)):
        subprocess.run([*R, "pods", "register", name, "--pod-id", i, "--project", "verity", "--guard", "60", "--replace"],
                       capture_output=True, text=True, cwd="/workspace")
    vip, vports = ports_of(vid)
    time.sleep(30)
    bp = sh("vy-bligero-l40s-101", "cat /proc/sys/kernel/random/boot_id; nvidia-smi --query-gpu=name --format=csv,noheader; "
            f"timeout 5 bash -c '</dev/tcp/{vip}/{vports.get('22')}' && echo HAIRPIN-OK || echo HAIRPIN-FAIL")
    bv = sh("vy-bligero-l40s-101-ver", "cat /proc/sys/kernel/random/boot_id")
    boot_p, boot_v = bp.splitlines()[0] if bp else "", bv.splitlines()[0] if bv else ""
    ok = "HAIRPIN-OK" in bp and boot_p and boot_v and boot_p != boot_v
    log(f"{dc}: prover {pid} verifier {vid} ({vgpu}) {vip} {vports} boot {boot_p[:8]} vs {boot_v[:8]} {'HAIRPIN-OK' if 'HAIRPIN-OK' in bp else 'HAIRPIN-FAIL'}")
    if ok:
        log(f"SUCCESS {dc} prover {pid} verifier {vid} {vip}:{vports.get('7000')}")
        return True
    drain("vy-bligero-l40s-101-ver")
    drain("vy-bligero-l40s-101")
    log(f"{dc}: pair drained (same host or no hairpin); {dc} added to BAD")
    BAD.add(dc)
    return False


def main():
    t0, last_comm = time.time(), None
    while time.time() - t0 < DEADLINE_S:
        try:
            r = runpod._graphql("{ dataCenters { id gpuAvailability { gpuTypeId stockStatus } } }")["data"]["dataCenters"]
            comm = runpod._graphql('{ gpuTypes(input:{id:"NVIDIA L40S"}) { lowestPrice(input:{gpuCount:1, secureCloud:false}) { stockStatus } } }')
            cs = comm["data"]["gpuTypes"][0]["lowestPrice"]["stockStatus"]
            if cs != last_comm:
                log(f"community L40S stock: {cs}")
                last_comm = cs
            for dc in r:
                avail = [g["gpuTypeId"] for g in dc.get("gpuAvailability") or [] if g.get("stockStatus")]
                if L40S in avail and dc["id"] not in BAD:
                    log(f"L40S in {dc['id']} (others: {[g for g in avail if g != L40S][:6]})")
                    if attempt(dc["id"], avail):
                        return 0
        except Exception as e:  # noqa: BLE001
            log(f"poll error: {type(e).__name__}: {str(e)[:120]}")
        time.sleep(90)
    log("DEADLINE: no L40S pair found")
    return 1


if __name__ == "__main__":
    sys.exit(main())
