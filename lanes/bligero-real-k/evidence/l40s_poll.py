"""bligero-l40s-101: wait (until DEADLINE_UTC) for an L40S prover with a same-DC verifier on ANOTHER physical host whose public ports
hairpin, keeping pods off until the pair checks out.  Every 90 s, per DC with secure L40S stock (not known to fail): create a
cheap verifier there FIRST (another GPU type from ALLOW, or a CPU pod of >= 8 vCPU), then the L40S prover; register both (idle
guard); require distinct kernel boot ids and a prover -> verifier public ssh connect under MAX_CONNECT_MS.  Success prints SUCCESS
and exits 0 with the pair up; otherwise both are drained.  Community L40S: at most every 20 min (COMMUNITY_TRIES), prover first
(its country is known only then), a verifier in the same country, same checks.  Log: /tmp/l40s_poll.log."""
import json
import socket
import subprocess
import sys
import time

from research.pods import runpod

DEADLINE_UTC = "14:25"
BAD = {"EU-NL-1", "EUR-IS-2", "US-WA-1", "OC-AU-1", "CA-MTL-1"}
BAD_COUNTRIES = {"TW"}
L40S = "NVIDIA L40S"
ALLOW = ["NVIDIA RTX A6000", "NVIDIA A40", "NVIDIA GeForce RTX 4090", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A5000", "NVIDIA L4",
         "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA RTX A4000", "NVIDIA RTX PRO 4000 Blackwell", "NVIDIA RTX PRO 4500 Blackwell",
         "NVIDIA RTX PRO 4500 Blackwell Server Edition", "NVIDIA L40", "NVIDIA RTX 6000 Ada Generation", "NVIDIA GeForce RTX 5090"]
CPU_SIZES = ["cpu3c-16-32", "cpu3c-8-16", "cpu3g-8-32", "cpu3m-8-64", "cpu5c-16-32", "cpu5c-8-16", "cpu3c-32-64"]
MAX_CONNECT_MS = 3.0
COMMUNITY_TRIES = 4
LOG = "/tmp/l40s_poll.log"
R = ["uv", "run", "--frozen", "research"]
PROVER, VERIFIER = "vy-bligero-l40s-101", "vy-bligero-l40s-101-ver"


def log(msg):
    line = f"{time.strftime('%H:%M:%SZ', time.gmtime())} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def past_deadline():
    return time.strftime("%H:%M", time.gmtime()) >= DEADLINE_UTC


def rest(name, cloud, gpus, ports, disk, dc=None, country=None):
    body = {"name": f"{name}-veritor-campaign", "imageName": runpod.DEFAULT_IMAGE, "gpuTypeIds": gpus, "gpuCount": 1, "cloudType": cloud,
            "computeType": "GPU", "containerDiskInGb": disk, "volumeInGb": 0, "ports": [f"{p}/tcp" for p in ports], "supportPublicIp": True,
            "minVCPUPerGPU": 8, "env": {"PUBLIC_KEY": runpod.public_key()}}
    if dc:
        body["dataCenterIds"] = [dc]
    if country:
        body["countryCodes"] = [country]
    try:
        pod = runpod._request("POST", "/pods", body)
        m = pod.get("machine") or {}
        return pod["id"], m.get("gpuTypeId"), m.get("location")
    except runpod.PodError as e:
        return None, str(e)[:160], None


def gql(kind, name, dc, what, disk):
    common = (f'containerDiskInGb: {disk}, dataCenterId: {json.dumps(dc)}, name: {json.dumps(name + "-veritor-campaign")}, '
              f'imageName: {json.dumps(runpod.DEFAULT_IMAGE)}, startSsh: true, supportPublicIp: true, ports: "22/tcp,7000/tcp", '
              f'env: [{{key: "PUBLIC_KEY", value: {json.dumps(runpod.public_key())}}}]')
    if kind == "gpu":
        q = (f"mutation {{ podFindAndDeployOnDemand(input: {{cloudType: SECURE, gpuCount: 1, gpuTypeId: {json.dumps(what)}, volumeInGb: 0, "
             f"{common}}}) {{ id }} }}")
    else:
        q = f"mutation {{ deployCpuPod(input: {{instanceId: {json.dumps(what)}, cloudType: SECURE, {common}}}) {{ id }} }}"
    try:
        r = runpod._graphql(q)
    except Exception as e:  # noqa: BLE001
        return None, str(e)[:160]
    d = (r.get("data") or {}).get("podFindAndDeployOnDemand" if kind == "gpu" else "deployCpuPod")
    return (d["id"], what) if d and d.get("id") else (None, json.dumps(r.get("errors"))[:160])


def create_in_dc(name, dc, gpus, ports, disk, cpu_ok):
    """REST first; a DC the REST enum rejects goes through GraphQL (each GPU type, then CPU sizes when cpu_ok)."""
    pid, info, _ = rest(name, "SECURE", gpus, ports, disk, dc=dc)
    if pid:
        return pid, info
    if "dataCenterIds" not in (info or "") and "request body" not in (info or ""):
        err = info
    else:
        err = None
        for g in gpus:
            pid, info = gql("gpu", name, dc, g, disk)
            if pid:
                return pid, g
    if cpu_ok:
        for c in CPU_SIZES:
            pid, info = gql("cpu", name, dc, c, min(disk, 40))
            if pid:
                return pid, c
    return None, err or info


def delete(pid):
    try:
        runpod._request("DELETE", f"/pods/{pid}")
    except runpod.PodError as e:
        log(f"delete {pid}: {e}")


def register(name, pid):
    subprocess.run([*R, "pods", "register", name, "--pod-id", pid, "--project", "verity", "--guard", "60", "--replace"],
                   capture_output=True, text=True, cwd="/workspace")


def ssh(name, cmd):
    r = subprocess.run([*R, "pods", "ssh", name, "--", cmd], capture_output=True, text=True, cwd="/workspace", timeout=180)
    return "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "setlocale" not in l).strip()


def public(pid):
    for _ in range(30):
        p = runpod._request("GET", f"/pods/{pid}") or {}
        if p.get("publicIp") and (p.get("portMappings") or {}).get("22"):
            return p["publicIp"], p["portMappings"]
        time.sleep(10)
    return None, {}


def check_pair(pid, vid):
    register(PROVER, pid)
    register(VERIFIER, vid)
    vip, vports = public(vid)
    pip_, _ = public(pid)
    if not vip or not pip_:
        return False, "no public ip / ssh port"
    for _ in range(12):                                   # sshd on both
        a = ssh(PROVER, "cat /proc/sys/kernel/random/boot_id; nvidia-smi --query-gpu=name --format=csv,noheader")
        b = ssh(VERIFIER, "cat /proc/sys/kernel/random/boot_id")
        if len(a.splitlines()) >= 2 and b:
            break
        time.sleep(15)
    else:
        return False, "ssh not ready"
    boot_p, gpu = a.splitlines()[0], a.splitlines()[1]
    boot_v = b.splitlines()[0]
    probe = ssh(PROVER, f"python3 -c \"import socket,time; ts=[]\nfor _ in range(5):\n t=time.time(); s=socket.create_connection(('{vip}',{vports['22']}),5); ts.append((time.time()-t)*1e3); s.close()\nprint(sorted(ts)[2])\" 2>&1 | tail -1")
    try:
        ms = float(probe)
    except ValueError:
        ms = None
    ok = boot_p != boot_v and "L40S" in gpu and ms is not None and ms < MAX_CONNECT_MS
    return ok, f"prover {pip_} ({gpu}) verifier {vip} ports {vports} boot {boot_p[:8]}/{boot_v[:8]} connect {probe[:60]} ms"


def drain_both(pid, vid):
    for i in (vid, pid):
        if i:
            subprocess.run([*R, "pods", "drain", i], capture_output=True, text=True, cwd="/workspace", timeout=1800)


def secure_attempt(dc, avail, cpu_ok):
    vgpus = [g for g in ALLOW if g in avail]
    if not vgpus and not cpu_ok:
        vgpus = [L40S]                    # a second L40S as the verifier: kept only if it is on another host (boot ids)
        log(f"L40S in {dc}: no other verifier type; trying a second L40S (one try per DC)")
    vid, vinfo = create_in_dc(VERIFIER, dc, vgpus or ALLOW[:1], [22, 7000], 60, cpu_ok)
    if not vid:
        log(f"L40S in {dc}: verifier not created ({vinfo})")
        return False
    pid, pinfo = create_in_dc(PROVER, dc, [L40S], [22], 150, False)
    if not pid:
        log(f"L40S in {dc}: verifier {vid} ({vinfo}) up but the L40S is gone ({pinfo}); deleting the verifier")
        delete(vid)
        return False
    ok, why = check_pair(pid, vid)
    log(f"{dc}: {'PAIR-OK' if ok else 'pair rejected'}: {why}")
    if ok:
        log(f"SUCCESS dc={dc} prover={pid} verifier={vid} ({vinfo})")
        return True
    drain_both(pid, vid)
    BAD.add(dc)
    return False


def community_attempt():
    pid, info, country = rest(PROVER, "COMMUNITY", [L40S], [22], 150)
    if not pid:
        log(f"community L40S: {info}")
        return False
    if country in BAD_COUNTRIES:
        log(f"community L40S in {country} (known: no verifier there); deleting {pid}")
        delete(pid)
        return False
    vid, vinfo, vc = rest(VERIFIER, "COMMUNITY", ALLOW, [22, 7000], 60, country=country)
    if not vid:
        log(f"community L40S in {country}: no verifier ({vinfo}); deleting {pid}")
        delete(pid)
        BAD_COUNTRIES.add(country)
        return False
    ok, why = check_pair(pid, vid)
    log(f"community {country}: {'PAIR-OK' if ok else 'pair rejected'}: {why}")
    if ok:
        log(f"SUCCESS community={country} prover={pid} verifier={vid} ({vinfo})")
        return True
    drain_both(pid, vid)
    BAD_COUNTRIES.add(country)
    return False


def main():
    tries, last_comm_try = 0, 0.0
    log(f"poll start (deadline {DEADLINE_UTC}Z)")
    while not past_deadline():
        try:
            dcs = runpod._graphql("{ dataCenters { id gpuAvailability { gpuTypeId stockStatus } } }")["data"]["dataCenters"]
            for dc in dcs:
                avail = [g["gpuTypeId"] for g in dc.get("gpuAvailability") or [] if g.get("stockStatus")]
                if L40S not in avail or dc["id"] in BAD:
                    continue
                cpu = runpod._graphql('{ cpuFlavors { id specifics(input:{dataCenterId:%s}) { stockStatus } } }' % json.dumps(dc["id"]))
                cpu_ok = any((f.get("specifics") or {}).get("stockStatus") for f in cpu["data"]["cpuFlavors"])
                log(f"L40S in {dc['id']} (others {[g.replace('NVIDIA ', '') for g in avail if g != L40S][:5]}, cpu {cpu_ok})")
                if secure_attempt(dc["id"], avail, cpu_ok):
                    return 0
            cs = runpod._graphql('{ gpuTypes(input:{id:"NVIDIA L40S"}) { lowestPrice(input:{gpuCount:1, secureCloud:false}) { stockStatus } } }')
            if (cs["data"]["gpuTypes"][0]["lowestPrice"] or {}).get("stockStatus") and tries < COMMUNITY_TRIES and time.time() - last_comm_try > 1200:
                tries, last_comm_try = tries + 1, time.time()
                if community_attempt():
                    return 0
        except Exception as e:  # noqa: BLE001
            log(f"poll error: {type(e).__name__}: {str(e)[:160]}")
        time.sleep(90)
    log("DEADLINE: no L40S pair")
    return 1


if __name__ == "__main__":
    sys.exit(main())
