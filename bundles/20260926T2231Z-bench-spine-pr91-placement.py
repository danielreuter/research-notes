"""Where a cell's prover and verifier ran: machine identity, and whether the two are separate machines on a routed link.

A container hostname says nothing about the machine: RunPod places several pods on one host, and two such pods share its
kernel, CPUs and public IP and can talk over a host-private bridge (red-team-flock's ruling, coordinator 2026-09-26 12:00Z: a
co-resident verifier is not a separate verifier).  An identity is a dict with any of

    machine_id     the RunPod machine id (the pod API's ``machineId``)
    public_ip      the pod's public IP (the API's ``publicIp``, or ``$RUNPOD_PUBLIC_IP`` on the pod)
    product_uuid   ``/sys/class/dmi/id/product_uuid``
    boot_id        ``/proc/sys/kernel/random/boot_id``: containers of one host share its kernel's
    cpu_model      the host CPU model (``/proc/cpuinfo``)
    hypervisor     whether the CPU flags carry ``hypervisor`` (a virtual machine's guest)
    sys_vendor, product_name   ``/sys/class/dmi/id/``
    pod_id, hostname

and a link ``{peer, peer_ip, source_ip, rtt}`` is how the prover reached the verifier, ``rtt`` its TCP-connect round trip
(:func:`tcp_rtt`).  :func:`assess` says why a pair is not shown to be on separate machines: a shared machine id, product uuid or
boot id; a link to a host bridge (loopback, link-local, the docker pool 172.16/12), to the prover's own public IP, or to another
private address unless the machine ids are known and differ; too little identity to tell (neither a machine id or DMI uuid on
both sides, nor a public IP and CPU model on both); or a shared public IP without the proof a datacenter NAT needs
(:func:`_nat_exception`: the three ids recorded and different, both pods bare metal, the link RunPod's global network, and a
TCP-connect RTT on it of at least :data:`RTT_FLOOR_MS`).  A shared public IP that has that proof is accepted and reported
(``shared_public_ip`` and its evidence).

    python3 placement.py probe [--peer HOST:PORT] [--rtt HOST:PORT] [--out FILE]     stdlib only: runs on a pod before a cell's job
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import socket
import sys
from pathlib import Path
from typing import Any, Mapping

SHARED_KEYS = ("machine_id", "product_uuid", "boot_id", "public_ip")
#: What a pair sharing a public IP (a datacenter's egress NAT) must record, on both pods and all different.
NAT_IDS = ("machine_id", "product_uuid", "boot_id")
#: The measured prover-verifier round trip a shared-IP pair must reach: well above the 0.03 ms of two containers on one host.
RTT_FLOOR_MS = 0.1
RTT_CONNECTS = 30
RTT_METHOD = "tcp-connect: median and minimum of 30 kernel-level TCP connects on the session's route (no payload)"
#: RunPod's global network: a shared-IP pair's only accepted link is ``<verifier pod id>.runpod.internal`` resolving into 10/8.
RUNPOD_INTERNAL = ".runpod.internal"
GLOBAL_NET = ipaddress.ip_network("10.0.0.0/8")
#: ``/sys/class/dmi/id/sys_vendor`` prefixes of hypervisors' guests (red-team-flock-3 S1): a VM's DMI uuid and boot id are its own.
HYPERVISOR_VENDORS = ("QEMU", "KVM", "Xen", "VMware", "Microsoft Corporation", "innotek", "Parallels", "Red Hat", "OpenStack",
                      "Amazon EC2", "Google")
PROBE = "backends/numerical/python/verity_numerical/bench/placement.py"


def _read(path: str) -> str | None:
    try:
        return Path(path).read_text().strip() or None
    except OSError:
        return None


def _cpu_model() -> str | None:
    for line in (_read("/proc/cpuinfo") or "").splitlines():
        if line.lower().startswith("model name"):
            return line.split(":", 1)[1].strip()
    return None


#: Address space a path to which need not leave the host: RFC 1918, shared (100.64/10), IPv6 unique-local.
HOST_LOCAL_NETS = tuple(ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10", "fc00::/7"))
#: Docker's bridge pool: a container-to-container path on one host (RunPod's routed private network is 10.x).
HOST_BRIDGE_NET = ipaddress.ip_network("172.16.0.0/12")


def is_host_private(ip: str | None) -> bool:
    """Loopback, link-local, private (RFC 1918), shared or unique-local address space: a path that need not leave the host."""
    if not ip:
        return False
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return a.is_loopback or a.is_link_local or any(a.version == n.version and a in n for n in HOST_LOCAL_NETS)


def link_to(peer: str) -> dict[str, Any]:
    """The route to ``peer`` (HOST:PORT): its resolved address and the local source address the kernel picks for it."""
    host, _, port = peer.rpartition(":")
    out: dict[str, Any] = {"peer": peer, "peer_ip": None, "source_ip": None}
    try:
        out["peer_ip"] = socket.getaddrinfo(host, int(port or 0), proto=socket.IPPROTO_TCP)[0][4][0]
        with socket.socket(socket.AF_INET6 if ":" in out["peer_ip"] else socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((out["peer_ip"], int(port or 9)))
            out["source_ip"] = s.getsockname()[0]
    except (OSError, ValueError) as e:
        out["error"] = f"{type(e).__name__}: {e}"
    return out


def _hypervisor_flag() -> bool | None:
    """Whether the CPU flags carry ``hypervisor`` (set by every hypervisor for its guests); ``None`` without /proc/cpuinfo flags."""
    for line in (_read("/proc/cpuinfo") or "").splitlines():
        if line.lower().startswith("flags"):
            return "hypervisor" in line.split(":", 1)[1].split()
    return None


def tcp_rtt(target: str, n: int = RTT_CONNECTS, timeout: float = 5.0) -> dict[str, Any]:
    """Round trips of ``n`` kernel-level TCP connects to ``target`` (HOST:PORT): ``connect()`` to the SYN-ACK, no payload, each socket
    closed at once.  Median and minimum in ms, the address connected to, and how many failed."""
    import statistics
    import time

    host, _, port = target.rpartition(":")
    out: dict[str, Any] = {"target": target, "target_ip": None, "n": 0, "failed": 0, "median_ms": None, "min_ms": None,
                           "method": RTT_METHOD}
    try:
        out["target_ip"] = socket.getaddrinfo(host, int(port), proto=socket.IPPROTO_TCP)[0][4][0]
    except (OSError, ValueError) as e:
        out["error"] = f"{type(e).__name__}: {e}"
        return out
    ts = []
    for _ in range(n):
        t = time.perf_counter()
        try:
            socket.create_connection((out["target_ip"], int(port)), timeout=timeout).close()
        except OSError:
            out["failed"] += 1
            continue
        ts.append((time.perf_counter() - t) * 1e3)
    if ts:
        out.update(n=len(ts), median_ms=statistics.median(ts), min_ms=min(ts))
    return out


def probe(peer: str | None = None, rtt: str | None = None) -> dict[str, Any]:
    """This machine's identity as seen from inside its container, the link to ``peer`` and, with ``rtt`` (HOST:PORT on the peer's
    route), the TCP-connect round trip to it."""
    ident = {"pod_id": os.environ.get("RUNPOD_POD_ID"), "public_ip": os.environ.get("RUNPOD_PUBLIC_IP"),
             "product_uuid": _read("/sys/class/dmi/id/product_uuid"), "boot_id": _read("/proc/sys/kernel/random/boot_id"),
             "cpu_model": _cpu_model(), "hypervisor": _hypervisor_flag(), "sys_vendor": _read("/sys/class/dmi/id/sys_vendor"),
             "product_name": _read("/sys/class/dmi/id/product_name"), "hostname": socket.gethostname(),
             "datacenter": os.environ.get("RUNPOD_DC_ID")}
    if peer:
        ident["link"] = link_to(peer)
        if rtt:
            ident["link"]["rtt"] = tcp_rtt(rtt)
    return ident


def from_job(run_dir: Path) -> dict[str, Any]:
    """The identity a run recorded: its ``placement.json`` (the probe), else what ``job.json`` has (boot id, hostname)."""
    ident: dict[str, Any] = {}
    job = run_dir / "job.json"
    if job.is_file():
        env = json.loads(job.read_text()).get("environment") or {}
        ident.update({k: env.get(k) for k in ("boot_id", "hostname", "pod_id") if env.get(k)})
    pl = run_dir / "placement.json"
    if pl.is_file():
        ident = merge(ident, json.loads(pl.read_text()))
    return ident


def from_runpod(machine: str) -> dict[str, Any]:
    """A pod's identity from the RunPod API, by machine name (the machines registry's pod id) or pod id."""
    from research.pods import registry, runpod

    pod_id = machine
    d = os.environ.get("RESEARCH_MACHINES_D")
    if d and Path(d).is_dir():
        entries, _errors = registry.load_dir(Path(d))
        pod_id = (entries.get(machine) or {}).get("pod_id") or machine
    pod = runpod.get(pod_id)
    return {"pod_id": pod.get("id"), "machine_id": pod.get("machineId") or None, "public_ip": pod.get("publicIp") or None}


def rtt_target(peer: str | None) -> str | None:
    """Where the prover times its TCP connects for a global-network peer: the verifier pod's sshd on the same name and route.  Not
    the session port: the verifiers count every connection on it as a session."""
    host = (peer or "").rpartition(":")[0]
    return f"{host}:22" if host.endswith(RUNPOD_INTERNAL) else None


def remote_probe(machine: str, peer: str | None = None) -> dict[str, Any]:
    """:func:`probe` run on a pod over ``research pods ssh`` (this file on stdin), so a plan can see its DMI identity and RTT."""
    import subprocess

    args = ["probe", *(["--peer", peer] if peer else []), *(["--rtt", rtt_target(peer)] if rtt_target(peer) else [])]
    r = subprocess.run(["research", "pods", "ssh", machine, "--", "python3", "-", *args], input=Path(__file__).read_text(),
                       capture_output=True, text=True, timeout=300)
    if r.returncode:
        raise RuntimeError(f"probe on {machine}: rc {r.returncode}: {r.stderr.strip()[-300:]}")
    return json.loads(r.stdout[r.stdout.index("{"):])


def merge(*idents: Mapping[str, Any] | None) -> dict[str, Any]:
    """Later identities override earlier ones; a value not recorded (``None``, empty) never overrides (``False`` is recorded)."""
    out: dict[str, Any] = {}
    for i in idents:
        out.update({k: v for k, v in (i or {}).items() if v is not None and v != "" and v != {}})
    return out


def is_host_bridge(ip: str | None) -> bool:
    """Loopback, link-local or the docker bridge pool (172.16/12, e.g. the 172.24.0.x co-resident path): never a routed link."""
    if not ip:
        return False
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return a.is_loopback or a.is_link_local or (a.version == 4 and a in HOST_BRIDGE_NET)


def is_hypervisor_vendor(vendor: str | None) -> bool:
    return bool(vendor) and any(str(vendor).strip().lower().startswith(v.lower()) for v in HYPERVISOR_VENDORS)


def _nat_exception(prover: Mapping[str, Any], verifier: Mapping[str, Any], link: Mapping[str, Any]) -> tuple[list[str], dict[str, Any]]:
    """Why a pair sharing a public IP does not earn the NAT exception (coordinator 22:00Z; red-team-flock-3 S1-S5, 22:05Z), and its
    evidence: all three :data:`NAT_IDS` recorded and different; both pods bare metal (no ``hypervisor`` CPU flag, a DMI
    ``sys_vendor`` that is no hypervisor's); the link ``<verifier pod id>.runpod.internal`` resolving into 10/8; the TCP-connect RTT
    on that route (median) at least :data:`RTT_FLOOR_MS`."""
    ip, out = prover["public_ip"], []
    pre = f"prover and verifier share public_ip {ip}"
    missing = [k for k in NAT_IDS if not (prover.get(k) and verifier.get(k))]
    if missing:
        out.append(f"{pre}: the NAT exception needs {', '.join(NAT_IDS)} recorded on both pods and all different; missing: {', '.join(missing)}")
    for role, x in (("prover", prover), ("verifier", verifier)):
        if x.get("hypervisor") is None or not x.get("sys_vendor"):
            out.append(f"{pre}: the {role} pod's hypervisor flag and DMI sys_vendor are not recorded (a VM's uuid and boot id are its own)")
        elif x["hypervisor"] is True or is_hypervisor_vendor(x["sys_vendor"]):
            out.append(f"{pre}: the {role} pod is a virtual machine (hypervisor flag {x['hypervisor']}, sys_vendor {x['sys_vendor']!r}): "
                       "two VMs of one host would pass the id checks")
    host = (link.get("peer") or "").rpartition(":")[0]
    want = f"{verifier.get('pod_id')}{RUNPOD_INTERNAL}" if verifier.get("pod_id") else None
    peer_ip = link.get("peer_ip")
    try:
        in_global = peer_ip is not None and ipaddress.ip_address(peer_ip) in GLOBAL_NET
    except ValueError:
        in_global = False
    if not (want and host == want and in_global):
        out.append(f"{pre}: the link must be RunPod's global network, {want or '<verifier pod id>' + RUNPOD_INTERNAL} resolving into "
                   f"{GLOBAL_NET}; it is {host or '?'} at {peer_ip}")
    rtt = link.get("rtt") or {}
    ok_rtt = (str(rtt.get("method", "")).startswith("tcp-connect") and isinstance(rtt.get("median_ms"), (int, float))
              and rtt.get("target_ip") == peer_ip and rtt["median_ms"] >= RTT_FLOOR_MS)
    if not ok_rtt:
        out.append(f"{pre}: no TCP-connect RTT of at least {RTT_FLOOR_MS} ms measured on the link's own route (median "
                   f"{rtt.get('median_ms')!r} ms to {rtt.get('target_ip')!r}, method {rtt.get('method')!r}); a co-resident pair measured "
                   "about 0.03 ms")
    evidence = {k: [prover.get(k), verifier.get(k)] for k in NAT_IDS}
    evidence.update({"public_ip": ip, "bare_metal": {role: {k: x.get(k) for k in ("hypervisor", "sys_vendor", "product_name", "cpu_model")}
                                                     for role, x in (("prover", prover), ("verifier", verifier))},
                     "link": {"name": host or None, "address": peer_ip}, "rtt": {k: rtt.get(k) for k in ("method", "median_ms", "min_ms", "n",
                                                                                                     "failed", "target", "target_ip")},
                     "rtt_floor_ms": RTT_FLOOR_MS})
    return out, evidence


def assess(prover: Mapping[str, Any], verifier: Mapping[str, Any], link: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Whether ``prover`` and ``verifier`` are shown to be separate machines on a routed link: ``{"problems": [...],
    "shared_public_ip": bool, "evidence": {...}}`` (no problems: they are).  A shared public IP (a datacenter's egress NAT) is one
    machine unless the pair earns the NAT exception (:func:`_nat_exception`); ``evidence`` is what it rests on."""
    link = link or {}
    out: list[str] = []
    for k in NAT_IDS:
        if prover.get(k) and prover.get(k) == verifier.get(k):
            out.append(f"prover and verifier share {k} {prover[k]} (one machine)")
    peer = link.get("peer_ip")
    shared = bool(prover.get("public_ip")) and prover.get("public_ip") == verifier.get("public_ip")
    evidence: dict[str, Any] = {}
    if shared:
        why, evidence = _nat_exception(prover, verifier, link)
        out += why
    else:
        ids_differ = any(prover.get(k) and verifier.get(k) and prover[k] != verifier[k] for k in ("machine_id", "product_uuid"))
        ip_cpu = all(x.get(k) for x in (prover, verifier) for k in ("public_ip", "cpu_model"))
        if not out and not (ids_differ or ip_cpu):
            out.append("machine identity not recorded: neither a machine id / DMI product uuid on both pods, nor a public IP and CPU model "
                       "on both, so the verifier is not shown to be on another machine")
    machines_differ = bool(prover.get("machine_id") and verifier.get("machine_id") and prover["machine_id"] != verifier["machine_id"])
    if peer and is_host_bridge(peer):
        out.append(f"the prover reaches the verifier at {peer}, a host bridge or loopback address (one machine, not a routed path)")
    elif peer and is_host_private(peer) and not machines_differ:
        out.append(f"the prover reaches the verifier at {peer}, a private address, and the machine ids are not known to differ")
    if peer and prover.get("public_ip") and peer == prover["public_ip"]:
        out.append(f"the prover reaches the verifier at its own public IP {peer} (a hairpin, never a separate machine's route)")
    return {"problems": out, "shared_public_ip": shared, "evidence": evidence}


def separation(prover: Mapping[str, Any], verifier: Mapping[str, Any], link: Mapping[str, Any] | None = None) -> list[str]:
    """Why ``prover`` and ``verifier`` are not shown to be separate machines on a routed link (empty: they are; :func:`assess`)."""
    return assess(prover, verifier, link)["problems"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="placement.py")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("probe")
    p.add_argument("--peer", default=None)
    p.add_argument("--rtt", default=None, help="HOST:PORT on the peer's route: the TCP-connect RTT target")
    p.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    doc = probe(a.peer or None, a.rtt or None)
    text = json.dumps(doc, indent=1) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
